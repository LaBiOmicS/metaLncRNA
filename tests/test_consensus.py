import pytest
import pandas as pd
import numpy as np
from metalncrna.engine.consensus import ConsensusEngine

def test_weighted_voting_logic():
    # Synthetic results
    data = {
        "tool1": pd.DataFrame({
            "sequence_id": ["seq1", "seq2"],
            "coding_probability": [0.9, 0.1],
            "coding_label": ["coding", "noncoding"]
        }),
        "tool2": pd.DataFrame({
            "sequence_id": ["seq1", "seq2"],
            "coding_probability": [0.8, 0.2],
            "coding_label": ["coding", "noncoding"]
        })
    }
    
    weights = {"tool1": 1.0, "tool2": 2.0}
    
    # Run consensus
    engine = ConsensusEngine()
    result = engine.simple_voting(data, custom_weights=weights, total_tools_count=2)
    
    assert "consensus_label" in result.columns
    assert result.iloc[0]["consensus_label"] == "coding"
    assert result.iloc[1]["consensus_label"] == "noncoding"
    assert result.iloc[0]["consensus_support"] == "2/2"

def test_id_normalization():
    data = {
        "tool1": pd.DataFrame({
            "sequence_id": ["SEQ_1_ORF_1", "SEQ_2"],
            "coding_probability": [0.9, 0.1],
            "coding_label": ["coding", "noncoding"]
        })
    }
    # Merging logic should normalize SEQ_1_ORF_1 to seq_1
    engine = ConsensusEngine()
    # Mocking data dict
    result = engine.simple_voting(data, total_tools_count=1)
    assert result.iloc[0]["sequence_id"] == "seq_1"
