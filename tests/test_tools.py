import csv

import pytest
from conftest import DATA, OUTPUTS

from metalncrna.tools import ALL, CODING, NONCODING, Options, ParseError

EXPECTED = list(csv.DictReader(open(DATA / "small.expected.tsv"), delimiter="\t"))
IDS = [f"s{i:07d}" for i in range(1, 8)]


@pytest.mark.parametrize("name", list(ALL))
def test_parsers_read_real_outputs(name):
    calls = ALL[name].parse(OUTPUTS / name, Options())
    for iid, row in zip(IDS, EXPECTED, strict=True):
        got = calls[iid].label if iid in calls else "NA"
        assert got == row[name], f"{name} {iid}"


def test_cpat_upper_case_ids_and_no_orf():
    calls = ALL["cpat"].parse(OUTPUTS / "cpat", Options())
    assert set(calls) == set(IDS)  # mapped back although CPAT wrote S0000001…
    assert calls["s0000006"].note == "no ORF found" and calls["s0000006"].label == NONCODING


def test_cpat_species_cutoff(tmp_path):
    (tmp_path / "cpat.ORF_prob.best.tsv").write_text("seq_ID\tID\tCoding_prob\nS0000001\tx\t0.40\n")
    assert ALL["cpat"].parse(tmp_path, Options(species="human"))["s0000001"].label == CODING  # >= 0.364
    assert ALL["cpat"].parse(tmp_path, Options(species="mouse"))["s0000001"].label == NONCODING  # < 0.44


def test_unexpected_label_is_an_error(tmp_path):
    (tmp_path / "plek").write_text("Maybe\t0.1\t>s0000001\n")
    with pytest.raises(ParseError):
        ALL["plek"].parse(tmp_path, Options())


def test_missing_output_is_an_error(tmp_path):
    with pytest.raises(ParseError, match="not found"):
        ALL["cpc2"].parse(tmp_path, Options())


def test_plek_success_rule():
    plek = ALL["plek"]
    assert plek.succeeded(1, "... Run complete\n")
    assert not plek.succeeded(1, "Traceback ...")
    assert ALL["cpc2"].succeeded(0, "") and not ALL["cpc2"].succeeded(1, "")


def test_species_model_selection():
    assert ALL["cpat"].unavailable_reason(Options(species="plant"))
    assert "/opt/cpat/models/Mouse_logitModel.RData" in ALL["cpat"].args(Options(species="mouse"))
    assert "Integrated" in ALL["cppred"].args(Options(species="fly"))
    assert ALL["cnci"].args(Options(species="plant"))[5] == "pl"
