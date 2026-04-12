import pandas as pd
import os
import multiprocessing
import subprocess
from pathlib import Path
from .base import BaseAdapter

class PLEKAdapter(BaseAdapter):
    def __init__(self, tool_name="PLEK.py", env_name="metalnc_plek"):
        super().__init__(tool_name, env_name)
        self.cores = max(1, multiprocessing.cpu_count() - 1)

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_output = output_dir / "plek_raw.txt"
        
        # PLEK.py -fasta <fasta> -out <output> -thread <n>
        cmd = [
            self.tool_path,
            "-fasta", str(input_fasta),
            "-out", str(raw_output),
            "-thread", str(self.cores)
        ]
        
        try:
            self.run_command(cmd, log_file=log_file)
        except subprocess.CalledProcessError as e:
            # PLEK sometimes returns 1 even on success. 
            # We check if output exists.
            if not raw_output.exists():
                raise e
                
        return raw_output

    def parse_results(self, raw_output_path):
        # PLEK format (Bioconda): [Non-coding|Coding] [Score] >[ID]
        results = []
        with open(raw_output_path, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    label_raw = parts[0]
                    score = float(parts[1])
                    seq_id = parts[2].lstrip(">")
                    
                    # Convert to standard
                    label = "coding" if label_raw.lower() == "coding" else "noncoding"
                    # Approximate probability from SVM distance
                    prob = 1 / (1 + pow(2.718, -score))
                    
                    results.append({
                        "sequence_id": seq_id.lower().split()[0],
                        "coding_probability": prob,
                        "coding_label": label
                    })
        
        return pd.DataFrame(results)
