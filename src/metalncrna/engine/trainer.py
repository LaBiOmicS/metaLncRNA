import os
import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

class Trainer:
    """
    Engine to retrain lncRNA tools with custom data.
    Supported tools: RNAsamba, CPAT.
    """
    def __init__(self, coding_fasta, noncoding_fasta, output_dir):
        self.coding = Path(coding_fasta).absolute()
        self.noncoding = Path(noncoding_fasta).absolute()
        self.output_dir = Path(output_dir).absolute()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def train_rnasamba(self, epochs=20, batch_size=128):
        """Train RNAsamba deep learning model."""
        console.print("[cyan][*] Training RNAsamba (Deep Learning)...[/cyan]")
        out_weights = self.output_dir / "rnasamba_custom.hdf5"
        cmd = [
            "mamba", "run", "-n", "metalnc_rnasamba", 
            "rnasamba", "train", 
            "--epochs", str(epochs),
            "--batch_size", str(batch_size),
            str(out_weights), str(self.coding), str(self.noncoding)
        ]
        subprocess.run(cmd, check=True)
        return out_weights

    def train_cpat(self):
        """Train CPAT hexamer table and logit model."""
        console.print("[cyan][*] Training CPAT (Logistic Regression)...[/cyan]")
        hex_table = self.output_dir / "cpat_custom_hexamer.tsv"
        logit_model = self.output_dir / "cpat_custom_model.RData"
        
        # 1. Make hexamer table
        cmd1 = ["mamba", "run", "-n", "metalnc_cpat", "make_hexamer_tab.py", "-c", str(self.coding), "-n", str(self.noncoding)]
        console.print(f"   > Generating species-specific hexamer table...")
        with open(hex_table, "w") as f:
            subprocess.run(cmd1, check=True, stdout=f)
            
        # 2. Make logit model
        out_prefix = str(self.output_dir / "cpat_custom")
        cmd2 = [
            "mamba", "run", "-n", "metalnc_cpat", 
            "make_logitModel.py", 
            "-c", str(self.coding), 
            "-n", str(self.noncoding), 
            "-x", str(hex_table), 
            "-o", out_prefix
        ]
        console.print(f"   > Generating logistic regression model...")
        subprocess.run(cmd2, check=True)
        return logit_model, hex_table

    def train_all(self, tools=["rnasamba", "cpat"]):
        results = {}
        for tool in tools:
            try:
                if tool == "rnasamba": results["rnasamba"] = self.train_rnasamba()
                elif tool == "cpat": results["cpat"] = self.train_cpat()
            except Exception as e:
                console.print(f"[bold red]✗ Failed to train {tool}: {str(e)}[/bold red]")
        return results
