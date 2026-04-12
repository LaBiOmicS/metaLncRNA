import pandas as pd
import os
import subprocess
from pathlib import Path
from .base import BaseAdapter

class LGCAdapter(BaseAdapter):
    def __init__(self, tool_name="lgc-1.0.0.py", env_name="metalnc_legacy"):
        super().__init__(tool_name, env_name)
        self.root = Path(__file__).parent.parent / "third_party" / "LGC"
        self.script = self.root / "scr" / "lgc-1.0.0.py"

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_output = output_dir / "lgc_raw.txt"
        abs_input = Path(input_fasta).absolute()
        
        cmd = ["python", str(self.script), str(abs_input), str(raw_output)]
        self.run_command(cmd, log_file=log_file, cwd=self.root / "scr")
        return raw_output

    def parse_results(self, raw_output_path):
        if not raw_output_path or not raw_output_path.exists():
            return pd.DataFrame()
        
        rows = []
        with open(raw_output_path, "r") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                parts = line.strip().split("\t")
                if len(parts) >= 5:
                    rows.append(parts)
        
        if not rows:
            return pd.DataFrame()
            
        df = pd.DataFrame(rows)
        # FIX: Added .str before .lower()
        df["sequence_id"] = df.iloc[:, 0].astype(str).str.lower().str.split().str[0]
        
        def to_prob(s):
            try:
                s = float(s)
                return 1 / (1 + pow(2.718, -s))
            except: return 0.5

        standard_df = pd.DataFrame({
            "sequence_id": df["sequence_id"],
            "coding_probability": df.iloc[:, 3].apply(to_prob),
            "coding_label": df.iloc[:, 4].str.lower().replace({"coding": "coding", "non-coding": "noncoding"})
        })
        return standard_df
