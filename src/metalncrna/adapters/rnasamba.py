from pathlib import Path

import pandas as pd

from .base import BaseAdapter


class RNAsambaAdapter(BaseAdapter):
    def __init__(self, weights_path, tool_path="rnasamba", env_name="metalnc_rnasamba"):
        super().__init__(tool_path, env_name)
        self.weights_path = Path(weights_path).absolute()

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_output = output_dir / "rnasamba_raw.tsv"
        cmd = [self.tool_path, "classify", str(raw_output), str(input_fasta), str(self.weights_path)]
        self.run_command(cmd, log_file=log_file)
        return raw_output

    def parse_results(self, raw_output_path):
        df = pd.read_csv(raw_output_path, sep="\t")
        df["sequence_id"] = df["sequence_name"].astype(str).str.lower().str.split().str[0]
        standard_df = pd.DataFrame({
            "sequence_id": df["sequence_id"],
            "coding_probability": df["coding_score"],
            "coding_label": df["classification"]
        })
        return standard_df
