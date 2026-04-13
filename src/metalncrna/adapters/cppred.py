from pathlib import Path

import pandas as pd

from .base import BaseAdapter


class CPPredAdapter(BaseAdapter):
    def __init__(self, tool_name="CPPred_fixed.py", env_name="metalnc_legacy"):
        super().__init__(tool_name, env_name)
        self.root = Path(__file__).parent.parent / "third_party" / "CPPred"
        self.script = self.root / "bin" / "CPPred_fixed.py"
        self.model = self.root / "Human_Model" / "Human.model"
        self.range = self.root / "Human_Model" / "Human.range"
        self.hexamer = self.root / "Hexamer" / "Human_Hexamer.tsv"

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_output = output_dir / "cppred_raw.txt"
        abs_input = Path(input_fasta).absolute()

        cmd = [
            "python", str(self.script),
            "-i", str(abs_input),
            "-o", str(raw_output),
            "-r", str(self.range),
            "-m", str(self.model),
            "-hex", str(self.hexamer),
            "-s", "Human"
        ]

        self.run_command(cmd, log_file=log_file, cwd=self.root / "bin")
        return raw_output

    def parse_results(self, raw_output_path):
        if not raw_output_path or not raw_output_path.exists():
            return pd.DataFrame()
        df = pd.read_csv(raw_output_path, sep="\t")
        # FIX: Added .str before .lower()
        df["sequence_id"] = df.iloc[:, 0].astype(str).str.lower().str.split().str[0]

        standard_df = pd.DataFrame({
            "sequence_id": df["sequence_id"],
            "coding_probability": df["coding_potential"],
            "coding_label": df["table"].str.lower()
        })
        return standard_df
