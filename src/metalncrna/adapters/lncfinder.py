import pandas as pd
import os
import subprocess
from pathlib import Path
from .base import BaseAdapter
from ..utils.logger import logger

class LncFinderAdapter(BaseAdapter):
    def __init__(self, tool_name="Rscript", env_name="metalnc_lncfinder"):
        super().__init__(tool_name, env_name)
        # Path to our R wrapper
        self.wrapper = Path(__file__).parent.parent / "utils" / "lncfinder_wrapper.R"

    def run(self, input_fasta, output_dir, log_file=None):
        output_dir = Path(output_dir).absolute()
        output_dir.mkdir(parents=True, exist_ok=True)
        raw_output = output_dir / "lncfinder_raw.tsv"
        
        # Cleanup
        if raw_output.exists():
            os.remove(raw_output)
            
        cmd = [
            self.tool_path, str(self.wrapper),
            str(input_fasta), str(raw_output)
        ]
        
        try:
            self.run_command(cmd, log_file=log_file)
        except subprocess.CalledProcessError:
            logger.warning("LncFinder execution failed (possibly due to sequence incompatibility).")
            
        return raw_output

    def parse_results(self, raw_output_path):
        if not raw_output_path or not raw_output_path.exists():
            return pd.DataFrame(columns=["sequence_id", "coding_probability", "coding_label"])
            
        try:
            df = pd.read_csv(raw_output_path, sep="\t")
            if df.empty:
                return pd.DataFrame(columns=["sequence_id", "coding_probability", "coding_label"])
                
            # Standardize ID
            df["sequence_id"] = df.iloc[:, 0].astype(str).str.lower().str.split().str[0]
            
            standard_df = pd.DataFrame({
                "sequence_id": df["sequence_id"],
                "coding_probability": df["Pred"],
                "coding_label": df["Pred"].apply(lambda x: "coding" if x >= 0.5 else "noncoding")
            })
            return standard_df
        except Exception as e:
            logger.warning(f"Failed to parse LncFinder results: {e}")
            return pd.DataFrame(columns=["sequence_id", "coding_probability", "coding_label"])
