import pytest
from metalncrna.utils.fasta import clean_sequence_key, build_id_mapping
from pathlib import Path
import tempfile

def test_clean_sequence_key_complex_headers():
    """Test sanitization across complex genomic FASTA header formats."""
    # Ensembl format
    assert clean_sequence_key("ENST00000380152.5 cdna:transcript") == "enst00000380152.5"
    # NCBI format
    assert clean_sequence_key("gnl|NCBI|seq123.1 Transcript description") == "gnl|ncbi|seq123.1"
    # Header with leading '>'
    assert clean_sequence_key(">seq_001_orf_1") == "seq_001"
    # Header with coordinate range suffix
    assert clean_sequence_key("chr1:100-200") == "chr1"
    # Header with spaces and pipes
    assert clean_sequence_key("NR_002887.2 | Homo sapiens lncRNA") == "nr_002887.2"

def test_build_id_mapping_preserves_unique_originals():
    """Test that build_id_mapping preserves exact original sequence IDs."""
    content = ">ENST00000380152.5 cdna:transcript chromosome:GRCh38:1:100:200:1\nATGC\n>gnl|NCBI|seq123.1 description\nGGCC\n"
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".fasta") as f:
        f.write(content)
        temp_path = f.name

    try:
        orig_ids, norm_map = build_id_mapping(temp_path)
        assert len(orig_ids) == 2
        assert orig_ids[0] == "ENST00000380152.5"
        assert orig_ids[1] == "gnl|NCBI|seq123.1"
        assert norm_map["enst00000380152.5"] == "ENST00000380152.5"
    finally:
        Path(temp_path).unlink(missing_ok=True)
