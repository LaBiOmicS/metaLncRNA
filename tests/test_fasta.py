import pytest
from conftest import DATA

from metalncrna.fasta import FastaError, prepare, read_fasta, write_subset


def test_prepare_renames_and_keeps_sequences(tmp_path):
    p = prepare(DATA / "small.fa", tmp_path / "in.fa")
    originals = list(read_fasta(DATA / "small.fa"))
    renamed = list(read_fasta(tmp_path / "in.fa"))
    assert [r.id for r in renamed] == [f"s{i:07d}" for i in range(1, 8)]
    assert [r.seq for r in renamed] == [r.seq for r in originals]
    assert p.to_original["s0000001"] == "gi|881717123|ref|NM_001310462.1|"
    assert p.to_internal["ENST00000516288.1"] == "s0000006"
    assert any("non-ACGTU" in w for w in p.warnings)


@pytest.mark.parametrize(
    "content, message",
    [
        (">a\nACGT\n>a\nACGT\n", "duplicate"),
        (">a\n>b\nACGT\n", "empty sequence"),
        ("ACGT\n>a\nACGT\n", "before the first"),
        ("", "no sequences"),
    ],
)
def test_prepare_rejects_bad_input(tmp_path, content, message):
    f = tmp_path / "bad.fa"
    f.write_text(content)
    with pytest.raises(FastaError, match=message):
        prepare(f, tmp_path / "out.fa")


def test_write_subset_keeps_full_headers(tmp_path):
    recs = list(read_fasta(DATA / "small.fa"))
    n = write_subset(recs, {"ENST00000516288.1"}, tmp_path / "sub.fa")
    assert n == 1
    assert (tmp_path / "sub.fa").read_text().startswith(">ENST00000516288.1 ncrna chromosome:")
