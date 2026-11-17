"""Runs the real containers. Needs a container engine and `metalncrna setup`; skipped otherwise."""

import csv

import pytest
from conftest import DATA

from metalncrna.config import Manifest, cache_dir
from metalncrna.pipeline import run
from metalncrna.runner import Runner, RunnerError
from metalncrna.tools import ALL, Options

pytestmark = pytest.mark.containers


@pytest.fixture(scope="module")
def runner():
    try:
        r = Runner.detect(None, cache_dir())
    except RunnerError as exc:
        pytest.skip(str(exc))
    m = Manifest.load()
    if not all(r.has_image(m.images[n].ref) for n in ALL):
        pytest.skip("tool images not installed (run `metalncrna setup`)")
    return r


def test_real_tools_reproduce_recorded_labels(tmp_path, runner):
    run(DATA / "small.fa", tmp_path, list(ALL), Options(threads=2), runner, Manifest.load(), jobs=7)
    rows = list(csv.DictReader(open(tmp_path / "results.tsv"), delimiter="\t"))
    expected = list(csv.DictReader(open(DATA / "small.expected.tsv"), delimiter="\t"))
    for row, exp in zip(rows, expected, strict=True):
        for col in [*ALL, "consensus"]:
            assert row[col] == exp[col], (row["sequence_id"], col)
