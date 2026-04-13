import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd


class ConsensusEngine:
    """
    ConsensusEngine implements the weighted soft-voting logic for metaLncRNA.
    """

    @staticmethod
    def from_files(files_dict: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        data = {}
        for name, path in files_dict.items():
            if pd.io.common.file_exists(path):
                data[name] = pd.read_csv(path, sep="\t")
        return data

    @staticmethod
    def simple_voting(data_dict: Dict[str, pd.DataFrame],
                      custom_weights: Optional[Dict[str, float]] = None,
                      total_tools_count: int = 7) -> pd.DataFrame:

        default_weights = {
            "rnasamba": 1.5, "cpat": 1.2, "cppred": 1.1,
            "cnci": 1.0, "cpc2": 0.9, "lgc": 0.9, "plek": 0.8
        }
        weights = custom_weights or default_weights

        merged_df = None
        for name, df in data_dict.items():
            df = df.copy()
            df = df.rename(columns={
                "coding_probability": f"{name}_prob",
                "coding_label": f"{name}_label"
            })
            df["sequence_id"] = (
                df["sequence_id"].astype(str).str.lower().str.replace(r"(_orf_\d+|:.*)$", "", regex=True)
            )
            if merged_df is None: merged_df = df
            else: merged_df = pd.merge(merged_df, df, on="sequence_id", how="outer")

        if merged_df is None: return pd.DataFrame()

        prob_cols = [c for c in merged_df.columns if c.endswith("_prob")]

        def calculate_weighted_prob(row):
            total_w, weighted_sum, support_count = 0, 0, 0
            for col in prob_cols:
                tool_name = col.replace("_prob", "")
                val = row[col]
                try:
                    val_float = float(val)
                    if not pd.isna(val_float):
                        w = weights.get(tool_name, 1.0)
                        weighted_sum += (val_float * w)
                        total_w += w
                        support_count += 1
                except (ValueError, TypeError): continue
            return (weighted_sum / total_w) if total_w > 0 else 0.5, support_count

        res = merged_df.apply(calculate_weighted_prob, axis=1)
        merged_df["meta_score"] = res.apply(lambda x: x[0])
        merged_df["consensus_support_count"] = res.apply(lambda x: x[1])
        merged_df["consensus_label"] = np.where(merged_df["meta_score"] > 0.5, "coding", "noncoding")
        merged_df["consensus_support"] = merged_df["consensus_support_count"].astype(str) + f"/{total_tools_count}"

        # Optimize memory usage for large genomic datasets
        for col in merged_df.select_dtypes(include=['float64']).columns:
            merged_df[col] = pd.to_numeric(merged_df[col], downcast='float')
        for col in merged_df.select_dtypes(include=['int64']).columns:
            merged_df[col] = pd.to_numeric(merged_df[col], downcast='integer')

        return merged_df

    @staticmethod
    def export_multiqc(final_df: pd.DataFrame, output_path: Path):
        """Export results in MultiQC generic JSON format."""
        mqc_data = {
            "id": "metalncrna_consensus",
            "plot_type": "table",
            "data": final_df.to_dict(orient="records")
        }
        with open(output_path, "w") as f:
            json.dump(mqc_data, f)
