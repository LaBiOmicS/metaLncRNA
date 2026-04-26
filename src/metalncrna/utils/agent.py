
import pandas as pd
from rich.console import Console
from rich.markdown import Markdown

console = Console()

class LncRNAAgent:
    """
    Expert Bioinformatician Agent based on Llama-3.2 to assist in lncRNA analysis.
    """
    def __init__(self, model: str = "llama3.2"):
        self.model = model
        self._client = None
        self._initialized = False
        self.system_prompt = (
            "You are an expert bioinformatician specializing in Long Non-coding RNA (lncRNA) identification. "
            "Your role is to interpret results from the metaLncRNA tool, which aggregates 7 different predictors "
            "(RNAsamba, CPAT, CPC2, PLEK, CNCI, CPPred, LGC). "
            "CRITICAL LOGIC: In metaLncRNA, a 'meta_score' < 0.5 indicates a NON-CODING (lncRNA) transcript, "
            "while a 'meta_score' > 0.5 indicates a PROTEIN-CODING transcript. "
            "A consensus support of 7/7 means all tools agreed; 4/7 means a weak consensus."
        )

    def _lazy_init(self):
        if self._initialized: return
        try:
            import ollama
            self._client = ollama
            self._initialized = True
        except ImportError:
            console.print("[yellow]Warning: 'ollama' package not found.[/yellow]")
            raise ImportError("Agent dependencies not met.")

    def summarize_results(self, df: pd.DataFrame) -> str:
        """Generates a high-level executive summary of the findings."""
        self._lazy_init()

        total = len(df)
        lncrnas = df[df["consensus_label"] == "noncoding"]
        coding = df[df["consensus_label"] == "coding"]

        # Calculate agreement stats
        unanimous_lnc = len(lncrnas[lncrnas["consensus_support_count"] >= 6])
        tools_used = [c.replace('_prob', '').upper() for c in df.columns if c.endswith('_prob')]

        context = f"""
        ### Data Summary:
        - Total sequences: {total}
        - lncRNAs found: {len(lncrnas)} ({len(lncrnas)/total:.1%})
        - Protein-coding found: {len(coding)} ({len(coding)/total:.1%})
        - Highly confident lncRNAs (>= 6 tools agreeing): {unanimous_lnc}
        - Tools in this run: {', '.join(tools_used)}

        ### Top 3 Most Confident lncRNA Candidates:
        {lncrnas.nsmallest(3, 'meta_score')[['sequence_id', 'meta_score', 'consensus_support']].to_string(index=False)}
        """

        prompt = f"""
        {self.system_prompt}
        Based on the following data, write a professional executive summary for a scientific report.
        Focus on the prevalence of lncRNAs and the overall tool agreement.
        Keep it under 150 words and use Markdown.

        {context}
        """

        try:
            response = self._client.generate(model=self.model, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"Error: {str(e)}"

    def explain_sequence(self, sequence_id: str, df: pd.DataFrame) -> str:
        """Detailed technical explanation of a specific classification."""
        self._lazy_init()

        row = df[df["sequence_id"].str.lower() == sequence_id.lower()]
        if row.empty: return f"Sequence {sequence_id} not found."

        data = row.to_dict(orient='records')[0]
        probs = {k.replace('_prob', '').upper(): v for k, v in data.items() if k.endswith('_prob')}

        # Identify "dissenting" tools
        label = data['consensus_label']
        dissenters = []
        for tool, prob in probs.items():
            if label == "noncoding" and prob > 0.5: dissenters.append(f"{tool} ({prob:.2f})")
            if label == "coding" and prob < 0.5: dissenters.append(f"{tool} ({prob:.2f})")

        context = f"""
        ### Transcript Analysis: {sequence_id}
        - FINAL CLASSIFICATION: {label.upper()}
        - Consensus Score: {data['meta_score']:.4f}
        - Support Count: {data['consensus_support']}
        - Individual Tool Probabilities: {probs}
        - Tools that disagreed with consensus: {', '.join(dissenters) if dissenters else 'None (Unanimous)'}
        """

        prompt = f"""
        {self.system_prompt}
        Explain the classification of '{sequence_id}'.
        If there was disagreement, explain why the meta-consensus still chose {label}.
        Briefly mention what the dissenting tools might have seen.
        Be technical but concise. Use Markdown.

        {context}
        """

        try:
            response = self._client.generate(model=self.model, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"Error: {str(e)}"

    def chat(self, df: pd.DataFrame):
        """Interactive session with biological context."""
        self._lazy_init()
        console.print(f"[bold green]─── metaLncRNA AI Chat (Model: {self.model}) ───[/bold green]")
        console.print("[italic]Expert persona active. Ask about your results or lncRNA biology.[/italic]\n")

        while True:
            query = console.input("[bold cyan]You > [/bold cyan]")
            if query.lower() in ["exit", "quit", "sair"]: break

            # Simple context injection
            lnc_count = len(df[df['consensus_label'] == 'noncoding'])
            prompt = f"{self.system_prompt}\nContext: {len(df)} sequences, {lnc_count} lncRNAs found.\nUser: {query}"

            try:
                with console.status("[italic]Analyzing...[/italic]"):
                    response = self._client.generate(model=self.model, prompt=prompt)
                console.print("\n[bold green]AI Agent:[/bold green]")
                console.print(Markdown(response['response']))
                console.print(f"[bold cyan]{'─' * 40}[/bold cyan]\n")
            except Exception as e:
                console.print(f"[red]Error: {str(e)}[/red]")
