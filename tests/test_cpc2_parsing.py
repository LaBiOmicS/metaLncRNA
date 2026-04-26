
import pytest
import pandas as pd
from pathlib import Path
from metalncrna.adapters.cpc2 import CPC2Adapter

def test_cpc2_parsing_logic():
    """
    Test that CPC2Adapter correctly parses the 8-column CPC2 output format.
    Reflecting the fix for v1.1.8 where indices were updated to 6 (prob) and 7 (label).
    """
    adapter = CPC2Adapter()
    
    # Synthetic CPC2 output (8 columns: ID, len, pep_len, fickett, pI, integrity, prob, label)
    # The adapter also adds its own sequence_id column as the first step, but 
    # pd.read_csv reads the raw file first.
    
    # Raw data as it would appear in the TSV file
    data = {
        "#ID": ["seq1", "seq2"],
        "transcript_length": [100, 200],
        "peptide_length": [30, 60],
        "Fickett_score": [0.4, 0.5],
        "pI": [5.5, 6.5],
        "ORF_integrity": [1, 1],
        "coding_probability": [0.123, 0.856],
        "label": ["noncoding", "coding"]
    }
    
    df_raw = pd.DataFrame(data)
    
    # We need to simulate the file read
    temp_file = Path("tests/test_cpc2_raw.txt")
    df_raw.to_csv(temp_file, sep="\t", index=False)
    
    try:
        standard_df = adapter.parse_results(temp_file)
        
        assert not standard_df.empty
        assert "coding_probability" in standard_df.columns
        assert "coding_label" in standard_df.columns
        
        # Check values
        assert standard_df.iloc[0]["coding_probability"] == 0.123
        assert standard_df.iloc[1]["coding_probability"] == 0.856
        assert standard_df.iloc[0]["coding_label"] == "noncoding"
        assert standard_df.iloc[1]["coding_label"] == "coding"
        assert standard_df.iloc[0]["sequence_id"] == "seq1"
        
    finally:
        if temp_file.exists():
            temp_file.unlink()

if __name__ == "__main__":
    test_cpc2_parsing_logic()
