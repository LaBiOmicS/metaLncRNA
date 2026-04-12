import pandas as pd
import os
import glob
from pathlib import Path
from .base import BaseAdapter

class CPATAdapter(BaseAdapter):
    def __init__(self, logit_model, hexamer_table, tool_name="cpat.py", env_name="metalnc_cpat"):
        super().__init__(tool_name, env_name)
        self.logit_model = Path(logit_model).absolute()
        self.hexamer_table = Path(hexamer_table).absolute()

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_output_base = output_dir / "cpat_raw.txt"
        
        for f in glob.glob(str(raw_output_base) + "*"):
            try: os.remove(f)
            except: pass
            
        # Call the script directly using absolute path
        cmd = [
            self.tool_path,
            "-g", str(input_fasta),
            "-d", str(self.logit_model),
            "-x", str(self.hexamer_table),
            "-o", str(raw_output_base)
        ]
        
        self.run_command(cmd, log_file=log_file)
        
        if os.path.exists("CPAT_run_info.log"):
            try: os.remove("CPAT_run_info.log")
            except: pass

        best_output = Path(str(raw_output_base) + ".ORF_prob.best.tsv")
        if best_output.exists():
            return best_output
        return Path(str(raw_output_base) + ".ORF_prob.tsv")

    def parse_results(self, raw_output_path):
        df = pd.read_csv(raw_output_path, sep="\t")
        if "seq_ID" in df.columns:
            df["sequence_id"] = df["seq_ID"]
        else:
            df["sequence_id"] = df["ID"].astype(str).str.replace(r"_ORF_\d+$", "", regex=True)
        
        df["sequence_id"] = df["sequence_id"].astype(str).str.lower().str.split().str[0]
        
        standard_df = pd.DataFrame({
            "sequence_id": df["sequence_id"],
            "coding_probability": df["Coding_prob"],
            "coding_label": df["Coding_prob"].apply(lambda x: "coding" if x >= 0.364 else "noncoding")
        })
        return standard_df
