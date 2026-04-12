import pandas as pd
import os
import subprocess
import multiprocessing
from pathlib import Path
from .base import BaseAdapter

class CNCIAdapter(BaseAdapter):
    def __init__(self, mode="ve", tool_name="CNCI.py", env_name="metalnc_legacy"):
        super().__init__(tool_name, env_name)
        self.root = Path(__file__).parent.parent / "third_party" / "CNCI"
        self.script = self.root / "CNCI.py"
        self.mode = mode # 've' for vertebrate (human), 'pl' for plant
        self.cores = max(1, multiprocessing.cpu_count() - 1)

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        cnci_out_dir = output_dir / "cnci_run"
        abs_input = Path(input_fasta).absolute()
        
        # Ensure mode is lowercase 've' or 'pl'
        run_mode = str(self.mode).lower()
        if run_mode not in ["ve", "pl"]:
            run_mode = "ve"

        cmd = [
            "python", str(self.script),
            "-f", str(abs_input),
            "-o", str(cnci_out_dir),
            "-p", str(self.cores),
            "-m", run_mode
        ]
        
        self.run_command(cmd, log_file=log_file, cwd=self.root)
        actual_output = cnci_out_dir / "CNCI.index"
        return actual_output

    def parse_results(self, raw_output_path):
        if not raw_output_path or not raw_output_path.exists():
            return pd.DataFrame()
        df = pd.read_csv(raw_output_path, sep="\t")
        df["sequence_id"] = df.iloc[:, 0].astype(str).str.lower().str.split().str[0]
        
        def to_prob(s):
            try:
                s = float(s)
                return 1 / (1 + pow(2.718, -s))
            except: return 0.5

        standard_df = pd.DataFrame({
            "sequence_id": df["sequence_id"],
            "coding_probability": df.iloc[:, 2].apply(to_prob),
            "coding_label": df.iloc[:, 1].str.lower()
        })
        return standard_df
