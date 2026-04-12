import pandas as pd
import os
import multiprocessing
from pathlib import Path
from .base import BaseAdapter

class LncADeepAdapter(BaseAdapter):
    def __init__(self, model_dir=None, tool_name="LncADeep.py", env_name="metalnc_lncadeep"):
        super().__init__(tool_name, env_name)
        self.model_dir = Path(model_dir).absolute() if model_dir else None
        self.cores = max(1, multiprocessing.cpu_count() - 1)

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        # LncADeep generates output in a specific directory
        
        # LncADeep.py -i <fasta> -o <out_dir> -m <model_dir> -t <threads>
        cmd = [
            "python", self.tool_path,
            "-i", str(input_fasta),
            "-o", str(output_dir),
            "-m", str(self.model_dir),
            "-t", str(self.cores)
        ]
        
        self.run_command(cmd, log_file=log_file)
        
        # LncADeep output name is usually based on input fasta name
        input_stem = Path(input_fasta).stem
        actual_output = output_dir / f"{input_stem}_LncADeep.txt"
        return actual_output

    def parse_results(self, raw_output_path):
        # LncADeep format: ID  Coding_prob  Label
        df = pd.read_csv(raw_output_path, sep="\t")
        df["sequence_id"] = df.iloc[:, 0].astype(str).lower().str.split().str[0]
        
        standard_df = pd.DataFrame({
            "sequence_id": df["sequence_id"],
            "coding_probability": df.iloc[:, 1],
            "coding_label": df.iloc[:, 2].str.lower()
        })
        return standard_df
