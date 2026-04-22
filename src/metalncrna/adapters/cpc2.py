from pathlib import Path

import pandas as pd

from .base import BaseAdapter


class CPC2Adapter(BaseAdapter):
    def __init__(self, tool_path="CPC2.py", env_name="metalnc_cpc2", use_mamba=True):
        super().__init__(tool_path, env_name, use_mamba=use_mamba)

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_output = output_dir / "cpc2_raw.txt"
        abs_input = Path(input_fasta).absolute()

        # CPC2.py -i input.fasta -o output.txt
        cmd = ["python", self.tool_path, "-i", str(abs_input), "-o", str(raw_output)]
        self.run_command(cmd, log_file=log_file)
        return raw_output

    def parse_results(self, raw_output_path):
        if not raw_output_path or not raw_output_path.exists():
            return pd.DataFrame()
        df = pd.read_csv(raw_output_path, sep="\t")
        df["sequence_id"] = df.iloc[:, 0].astype(str).str.lower().str.split().str[0]

        standard_df = pd.DataFrame({
            "sequence_id": df["sequence_id"],
            "coding_probability": df.iloc[:, 6],
            "coding_label": df.iloc[:, 7].str.lower()
        })
        return standard_df
