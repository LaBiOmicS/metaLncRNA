import csv
import json

import pytest
from conftest import DATA, FakeRunner

from metalncrna.fasta import read_fasta
from metalncrna.pipeline import PipelineError, run
from metalncrna.tools import ALL, Options

EXPECTED = list(csv.DictReader(open(DATA / "small.expected.tsv"), delimiter="\t"))


def _run(fake_env, out, runner=None, **kw):
    cache, manifest = fake_env
    runner = runner or FakeRunner(cache)
    kw.setdefault("tool_names", list(ALL))
    kw.setdefault("opts", Options())
    summary = run(input_fasta=DATA / "small.fa", out_dir=out, runner=runner, manifest=manifest, **kw)
    return summary, runner


def test_end_to_end(tmp_path, fake_env):
    summary, _ = _run(fake_env, tmp_path / "out")
    rows = list(csv.DictReader(open(tmp_path / "out" / "results.tsv"), delimiter="\t"))
    originals = [r.id for r in read_fasta(DATA / "small.fa")]
    assert [r["sequence_id"] for r in rows] == originals
    assert [r["consensus"] for r in rows] == [e["consensus"] for e in EXPECTED]
    for row, exp in zip(rows, EXPECTED, strict=True):
        for tool in ALL:
            assert row[tool] == exp[tool]
    assert rows[5]["voters"] == "6" and rows[5]["plek"] == "NA"

    # lncrna.fasta: noncoding consensus and >= 200 nt; the 111-nt ncRNA is excluded.
    lnc = [r.id for r in read_fasta(tmp_path / "out" / "lncrna.fasta")]
    assert lnc == [originals[3], originals[4], originals[6]]
    assert summary["consensus"] == {"coding": 3, "noncoding": 4, "ambiguous": 0, "unclassified": 0}

    prov = json.loads((tmp_path / "out" / "provenance.json").read_text())
    assert prov["tools"]["cpat"]["image"]["ref"] == "example/cpat:test"
    assert all(t["status"] == "ok" for t in prov["tools"].values())


def test_min_agree_filters_fasta(tmp_path, fake_env):
    _run(fake_env, tmp_path / "out", min_agree=7)
    lnc = [r.id for r in read_fasta(tmp_path / "out" / "lncrna.fasta")]
    assert lnc == ["gi|1063744952|ref|NR_143190.1|"]  # the only 7/7 noncoding call


def test_checkpoint_reuse_and_force(tmp_path, fake_env):
    out = tmp_path / "out"
    _run(fake_env, out)
    _, second = _run(fake_env, out)
    assert second.calls == []
    _, forced = _run(fake_env, out, force=True)
    assert sorted(forced.calls) == sorted(ALL)


def test_failure_aborts_by_default(tmp_path, fake_env):
    cache, _ = fake_env
    with pytest.raises(PipelineError, match="cnci"):
        _run(fake_env, tmp_path / "out", runner=FakeRunner(cache, fail={"cnci": 2}))
    prov = json.loads((tmp_path / "out" / "provenance.json").read_text())
    assert prov["tools"]["cnci"]["status"] == "failed"


def test_allow_failures(tmp_path, fake_env):
    cache, _ = fake_env
    summary, _ = _run(fake_env, tmp_path / "out", runner=FakeRunner(cache, fail={"cnci": 2}),
                      allow_failures=True)
    assert "cnci" not in summary["voting_tools"] and len(summary["voting_tools"]) == 6


def test_species_without_cpat_model(tmp_path, fake_env):
    summary, runner = _run(fake_env, tmp_path / "out", opts=Options(species="plant"),
                           tool_names=["cnci", "cpat", "cpc2"])
    assert "cpat" not in runner.calls
    prov = json.loads((tmp_path / "out" / "provenance.json").read_text())
    assert prov["tools"]["cpat"]["status"] == "unavailable"
