import click
import yaml
import os
import pandas as pd
import datetime
import subprocess
import concurrent.futures
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TaskProgressColumn

from .engine.dispatcher import Dispatcher
from .engine.consensus import ConsensusEngine
from .engine.trainer import Trainer
from .utils.downloader import download_all_resources
from .utils.setup_envs import create_environments
from .utils.fasta import get_sequence_stats, extract_lncrnas
from .utils.logger import setup_logger, logger

console = Console()

def load_config(config_path=None):
    default_paths = [config_path, Path.cwd() / "metaLncRNA_config.yaml", Path.home() / ".metalncrna" / "config.yaml"]
    config = {}
    for p in default_paths:
        if p and Path(p).exists():
            with open(p, "r") as f:
                config = yaml.safe_load(f)
            break
    return config

def get_data_dir(config):
    return Path(config.get("data_dir", Path.home() / ".metalncrna" / "data")).expanduser().absolute()

@click.group()
def main():
    """metaLncRNA: A modular and modern meta-predictor for lncRNA identification."""
    pass

@main.command()
@click.option("--data-dir", help="Directory for models and databases.")
@click.option("--tools", help="Specify tools.")
@click.option("-c", "--config", "config_file", type=click.Path(exists=True))
def setup(data_dir, tools, config_file):
    """Setup isolated environments and download databases."""
    setup_logger()
    logger.info("Starting metaLncRNA setup...")
    config = load_config(config_file)
    final_data_dir = get_data_dir(config) if not data_dir else Path(data_dir).expanduser().absolute()
    final_data_dir.mkdir(parents=True, exist_ok=True)
    download_all_resources(final_data_dir)
    tool_list = (tools or config.get("tools", "rnasamba,cpc2,cpat,plek,cnci,cppred,lgc")).split(",")
    create_environments(tool_list)
    logger.info(f"Setup completed! Data stored in {final_data_dir}.")

@main.command()
@click.option("--coding", required=True, type=click.Path(exists=True), help="FASTA file with protein-coding sequences.")
@click.option("--noncoding", required=True, type=click.Path(exists=True), help="FASTA file with non-coding sequences.")
@click.option("-o", "--output", required=True, type=click.Path(), help="Directory to save custom models.")
@click.option("--tools", default="rnasamba,cpat", help="Tools to train (rnasamba,cpat).")
def train(coding, noncoding, output, tools):
    """Train supported models (RNAsamba, CPAT) with custom datasets."""
    setup_logger()
    console.print(f"[bold cyan][*] metaLncRNA Training Module[/bold cyan]")
    trainer = Trainer(coding, noncoding, output)
    tool_list = [t.strip() for t in tools.split(",")]
    results = trainer.train_all(tools=tool_list)
    console.print(f"[bold green][+] Training completed! Models saved in {output}[/bold green]")

def run_single_tool(name, input_fasta, output_dir, config_file, **kwargs):
    output_dir = Path(output_dir).absolute()
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logger(output_dir, silent_console=True)
    input_fasta = Path(input_fasta).absolute()
    log_file = output_dir / "metalncrna.log"
    config = load_config(config_file)
    data_dir = get_data_dir(config)
    
    tool_config = config.get(name, {})
    if name == "rnasamba":
        tool_config.setdefault("weights", str(data_dir / "rnasamba" / "full_length_weights.hdf5"))
    elif name == "cpat":
        species = (kwargs.get("species") or tool_config.get("species", "human")).capitalize()
        tool_config.setdefault("logit_model", str(data_dir / "cpat" / f"{species}_logitModel.RData"))
        tool_config.setdefault("hexamer_table", str(data_dir / "cpat" / f"{species}_Hexamer.tsv"))
    elif name in ["cppred", "lgc"]:
        tool_config.setdefault("env_name", "metalnc_legacy")
    elif name == "cnci":
        tool_config.setdefault("env_name", "metalnc_legacy")
        tool_config.setdefault("mode", kwargs.get("mode", "ve"))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), TimeElapsedColumn(), console=console) as progress:
        task = progress.add_task(f"[cyan]Running {name.upper()}", total=1)
        dispatcher = Dispatcher({name: tool_config}, use_mamba=True)
        adapter = dispatcher.adapters[name]
        results_df = adapter.get_standardized_results(input_fasta, output_dir, log_file=log_file)
        progress.update(task, completed=1, description=f"[bold green]✓ {name.upper()} Finished")
    if results_df is not None:
        final_out = output_dir / f"{name}_standardized.tsv"
        results_df.to_csv(final_out, sep="\t", index=False)
        return results_df
    return None

@main.command()
@click.option("-i", "--input", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
@click.option("-c", "--config", type=click.Path(exists=True))
def rnasamba(input, output, config): run_single_tool("rnasamba", input, output, config)

@main.command()
@click.option("-i", "--input", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
@click.option("-c", "--config", type=click.Path(exists=True))
def cpc2(input, output, config): run_single_tool("cpc2", input, output, config)

@main.command()
@click.option("-i", "--input", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
@click.option("-s", "--species")
@click.option("-c", "--config", type=click.Path(exists=True))
def cpat(input, output, species, config): run_single_tool("cpat", input, output, config, species=species)

@main.command()
@click.option("-i", "--input", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
@click.option("-c", "--config", type=click.Path(exists=True))
def plek(input, output, config): run_single_tool("plek", input, output, config)

@main.command()
@click.option("-i", "--input", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
@click.option("-c", "--config", type=click.Path(exists=True))
def cppred(input, output, config): run_single_tool("cppred", input, output, config)

@main.command()
@click.option("-i", "--input", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
@click.option("-m", "--mode", default="ve", help="ve (vertebrate) or pl (plant)")
@click.option("-c", "--config", type=click.Path(exists=True))
def cnci(input, output, mode, config): run_single_tool("cnci", input, output, config, mode=mode)

@main.command()
@click.option("-i", "--input", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
@click.option("-c", "--config", type=click.Path(exists=True))
def lgc(input, output, config): run_single_tool("lgc", input, output, config)

@main.command()
@click.option("-d", "--results-dir", required=True, type=click.Path(exists=True))
@click.option("-o", "--output", required=True, type=click.Path())
def aggregate(results_dir, output):
    output_path = Path(output).absolute()
    setup_logger(output_path.parent)
    results_dir = Path(results_dir)
    files = list(results_dir.glob("*_standardized.tsv"))
    if not files:
        logger.error("No files found.")
        return
    files_dict = {f.name.replace("_standardized.tsv", ""): f for f in files}
    config = load_config()
    data_dict = ConsensusEngine.from_files(files_dict)
    final_df = ConsensusEngine.simple_voting(data_dict, custom_weights=config.get("weights"), total_tools_count=len(files_dict))
    final_df.to_csv(output, sep="\t", index=False)
    logger.info(f"Aggregation finished! Saved to: {output}")

@main.command()
@click.argument("query")
@click.option("-r", "--results", required=True, type=click.Path(exists=True), help="Results TSV file.")
@click.option("-m", "--model", default="phi3", help="LLM model name (e.g., phi3, llama3, mistral).")
def ask(query, results, model):
    """Ask the metaLncRNA AI agent about your analysis results."""
    try:
        from .utils.agent import LncRNAAgent
        import pandas as pd
    except ImportError:
        console.print("[red]Error: Agent dependencies not found.[/red]")
        console.print("Please install with: [bold]pip install ollama[/bold]")
        return

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        task = progress.add_task(f"[cyan]Consulting AI Agent ({model})...", total=None)
        
        try:
            df = pd.read_csv(results, sep="\t")
            agent = LncRNAAgent(model=model)
            
            # Simple routing based on the query content
            q_lower = query.lower()
            if any(x in q_lower for x in ["summary", "resumo", "overview"]):
                response = agent.summarize_results(df)
            elif any(x in q_lower for x in ["explain", "expliqu", "why", "por que"]):
                # Try to extract a potential sequence ID from the query
                # This is a simple heuristic, we could improve it
                words = query.replace("?", "").split()
                # Find the word that matches a sequence ID in the DF
                seq_id = next((w for w in words if w.lower() in df["sequence_id"].str.lower().values), None)
                if seq_id:
                    response = agent.explain_sequence(seq_id, df)
                else:
                    response = "I couldn't identify a sequence ID in your query to explain. Please provide the exact ID."
            else:
                # Fallback to general query with context
                response = agent.summarize_results(df) # Default for now
            
            progress.update(task, completed=True)
            console.print(f"\n[bold cyan]─── metaLncRNA AI Insight ───[/bold cyan]")
            console.print(response)
            console.print(f"[bold cyan]──────────────────────────────[/bold cyan]\n")
            
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]Error interacting with the agent: {str(e)}[/red]")

@main.command()
@click.option("-r", "--results", required=True, type=click.Path(exists=True), help="Results TSV file.")
@click.option("-m", "--model", default="llama3.2", help="LLM model name.")
def chat(results, model):
    """Start an interactive chat with the metaLncRNA AI agent."""
    try:
        from .utils.agent import LncRNAAgent
        import pandas as pd
    except ImportError:
        console.print("[red]Error: Agent dependencies not found.[/red]")
        console.print("Please install with: [bold]pip install ollama[/bold]")
        return
    
    df = pd.read_csv(results, sep="\t")
    agent = LncRNAAgent(model=model)
    agent.chat(df)

@main.command()
@click.option("-i", "--input", "input_fasta", required=True, type=click.Path(exists=True), help="Input FASTA file.")
@click.option("-o", "--output", "output_base", required=True, type=click.Path(), help="Base output directory.")
@click.option("-p", "--project", "project_name", help="Analysis project name (creates a subfolder).")
@click.option("-c", "--config", "config_file", type=click.Path(exists=True))
@click.option("--tools", help="Comma-separated tools.")
@click.option("--n-jobs", type=int, help="Number of parallel jobs.")
@click.option("--no-mamba", is_flag=True, help="Disable mamba run.")
@click.option("--keep-intermediates", is_flag=True, help="Keep raw tool output files.")
def predict(input_fasta, output_base, project_name, config_file, tools, n_jobs, no_mamba, keep_intermediates):
    """Run the integrated lncRNA identification pipeline."""
    output_dir = Path(output_base).absolute()
    if project_name:
        output_dir = output_dir / project_name
    
    output_dir.mkdir(parents=True, exist_ok=True)
    setup_logger(output_dir, silent_console=True)
    input_fasta = Path(input_fasta).absolute()
    log_file = output_dir / "metalncrna.log"
    
    with open(log_file, "w") as f:
        f.write(f"--- metaLncRNA Project Analysis ---\n")
        f.write(f"Project: {project_name or 'Default'}\n")
        f.write(f"Started at: {datetime.datetime.now()}\n\n")
    
    config = load_config(config_file)
    data_dir = get_data_dir(config)
    tool_list = (tools or config.get("tools", "rnasamba,cpc2,cpat,plek,cnci,cppred,lgc")).split(",")
    tool_list = [t.strip() for t in tool_list]
    
    run_config = {}
    for tool in tool_list:
        tool_config = config.get(tool, {})
        if tool == "rnasamba":
            tool_config.setdefault("weights", str(data_dir / "rnasamba" / "full_length_weights.hdf5"))
        elif tool == "cpat":
            species = tool_config.get("species", "human").capitalize()
            tool_config.setdefault("logit_model", str(data_dir / "cpat" / f"{species}_logitModel.RData"))
            tool_config.setdefault("hexamer_table", str(data_dir / "cpat" / f"{species}_Hexamer.tsv"))
        elif tool in ["cppred", "lgc"]:
            tool_config.setdefault("env_name", "metalnc_legacy")
        elif tool == "cnci":
            tool_config.setdefault("env_name", "metalnc_legacy")
            tool_config.setdefault("mode", "ve")
        run_config[tool] = tool_config
        
    console.print(f"[bold cyan][*] metaLncRNA Integrated Pipeline[/bold cyan]")
    if project_name:
        console.print(f"[bold white]Project:[/bold white] [green]{project_name}[/green]")
    
    dispatcher = Dispatcher(run_config, n_jobs=n_jobs, use_mamba=not no_mamba, keep_intermediates=keep_intermediates)
    results = dispatcher.run_all(input_fasta, output_dir, log_file=log_file, parallel=True)
    
    if results:
        setup_logger(output_dir, silent_console=False)
        logger.info("Computing consensus...")
        final_results = ConsensusEngine.simple_voting(results, custom_weights=config.get("weights"), total_tools_count=len(tool_list))
        final_output = output_dir / "metalncrna_results.tsv"
        final_results.to_csv(final_output, sep="\t", index=False)
        
        logger.info("Generating FASTA output...")
        lncrna_ids = final_results[final_results["consensus_label"] == "noncoding"]["sequence_id"].tolist()
        extract_lncrnas(input_fasta, output_dir / "predicted_lncrnas.fasta", lncrna_ids)
        
        logger.info(f"Execution finished! Project files saved in: {output_dir}")

if __name__ == "__main__":
    main()
