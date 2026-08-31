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
    engine = ConsensusEngine()
    result = engine.simple_voting(data, total_tools_count=1)
    assert result.iloc[0]["sequence_id"] == "seq_1"


def test_original_fasta_id_preservation(tmp_path):
    fasta_file = tmp_path / "transcriptome.fasta"
    fasta_file.write_text(">TRINITY_DN100_c0_g1_i1 len=500\nATGC\n>MSTRG.1234.1\nATGC\n")

    data = {
        "tool1": pd.DataFrame({
            "sequence_id": ["trinity_dn100_c0_g1_i1_orf_1", "mstrg.1234.1"],
            "coding_probability": [0.1, 0.9],
            "coding_label": ["noncoding", "coding"]
        })
    }

    engine = ConsensusEngine()
    result = engine.simple_voting(data, total_tools_count=1, input_fasta=str(fasta_file))

    # Must preserve exact original ID strings and order from FASTA
    assert result.iloc[0]["sequence_id"] == "TRINITY_DN100_c0_g1_i1"
    assert result.iloc[1]["sequence_id"] == "MSTRG.1234.1"


def test_custom_cutoff():
    data = {
        "tool1": pd.DataFrame({
            "sequence_id": ["seq1"],
            "coding_probability": [0.45],
            "coding_label": ["noncoding"]
        })
    }
    engine = ConsensusEngine()
    # Default cutoff 0.5 -> noncoding
    res_default = engine.simple_voting(data, cutoff=0.5)
    assert res_default.iloc[0]["consensus_label"] == "noncoding"

    # Lower cutoff 0.4 -> coding
    res_low = engine.simple_voting(data, cutoff=0.4)
    assert res_low.iloc[0]["consensus_label"] == "coding"


