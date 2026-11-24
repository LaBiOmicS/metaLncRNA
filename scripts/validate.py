#!/usr/bin/env python3
"""Benchmark metaLncRNA on the independent test sets shipped inside the CPPred package.

For each species, the coding and ncRNA test FASTA files are taken from
containers/cppred/upstream/CPPred.tar.gz (SHA-256 checked by the CPPred image build), run through
`metalncrna predict` and scored per tool and for the consensus.

    python scripts/validate.py -o validation/        # all four species
    python scripts/validate.py -o validation/ --species human

Writes <outdir>/<species>/ (the normal metalncrna outputs) and <outdir>/metrics.tsv.

Metrics treat `noncoding` as the positive class (the class metaLncRNA selects):
sensitivity = noncoding test RNAs called noncoding; specificity = coding test RNAs called coding.
`called` is the fraction of transcripts that got a label (tools abstain, e.g. PLEK on sequences of
200 nt or less; the consensus can be ambiguous). sensitivity, specificity, precision and
`accuracy` are computed on the labelled transcripts only; `accuracy_all` counts every unlabelled
transcript as an error.

Caveat: these are CPPred's own held-out test sets, so CPPred has a home advantage, and the other
tools may have seen some of these transcripts in training. The ncRNA sets are mostly short
ncRNAs (the human one is 95 snRNA + 5 rRNA), not lncRNAs.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARBALL = ROOT / "containers/cppred/upstream/CPPred.tar.gz"
# metalncrna species -> (coding test set, ncRNA test set) inside CPPred/data/
SETS = {
    "human": ("Human_coding_RNA_test.fa", "Human_ncrna_test.fa"),
    "mouse": ("Mouse_coding_RNA_test.fa", "Mouse_ncRNA_test.fa"),
    "zebrafish": ("Zebrafish_coding_RNA_test.fa", "Zebrafish_ncRNA_test.fa"),
    "fly": ("Fruit_fly_coding_RNA_test.fa", "Fruit_fly_ncRNA_test.fa"),
}
TOOLS = ["cnci", "cppred", "lgc", "cpat", "cpc2", "plek", "rnasamba"]


def read_ids(text: str) -> list[str]:
    return [line[1:].split()[0] for line in text.splitlines() if line.startswith(">")]


def score(truth: dict[str, str], called: dict[str, str]) -> dict[str, float]:
    nan = float("nan")
    lab = {i: called.get(i) for i in truth if called.get(i) in ("coding", "noncoding")}
    pos = [i for i in lab if truth[i] == "noncoding"]
    neg = [i for i in lab if truth[i] == "coding"]
    tp = sum(lab[i] == "noncoding" for i in pos)
    tn = sum(lab[i] == "coding" for i in neg)
    fp = len(neg) - tn
    return {
        "n": len(truth),
        "called": len(lab) / len(truth),
        "sensitivity": tp / len(pos) if pos else nan,
        "specificity": tn / len(neg) if neg else nan,
        "precision": tp / (tp + fp) if tp + fp else nan,
        "accuracy": (tp + tn) / len(lab) if lab else nan,
        "accuracy_all": (tp + tn) / len(truth),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("-o", "--outdir", type=Path, required=True)
    ap.add_argument("--species", nargs="+", choices=list(SETS), default=list(SETS))
    ap.add_argument("--metalncrna", default="metalncrna", help="command to run (default: metalncrna)")
    ap.add_argument("predict_args", nargs="*", help="extra arguments for `metalncrna predict` (after --)")
    a = ap.parse_args()

    a.outdir.mkdir(parents=True, exist_ok=True)
    rows = []
    with tarfile.open(TARBALL) as tar:
        for sp in a.species:
            truth: dict[str, str] = {}
            parts = []
            for member, label in zip(SETS[sp], ("coding", "noncoding"), strict=True):
                text = tar.extractfile(f"CPPred/data/{member}").read().decode()
                for i in read_ids(text):
                    truth[i] = label
                parts.append(text if text.endswith("\n") else text + "\n")
            fasta = a.outdir / f"{sp}.fa"
            fasta.write_text("".join(parts))
            out = a.outdir / sp
            cmd = [a.metalncrna, "predict", "-i", str(fasta), "-o", str(out), "-s", sp, *a.predict_args]
            print("+", " ".join(cmd), file=sys.stderr, flush=True)
            subprocess.run(cmd, check=True)

            with open(out / "results.tsv") as fh:
                res = list(csv.DictReader(fh, delimiter="\t"))
            results = {r["sequence_id"].split()[0]: r for r in res}
            for col in TOOLS + ["consensus"]:
                if col not in res[0]:
                    continue
                called = {i: r[col] for i, r in results.items()}
                rows.append({"species": sp, "predictor": col, **score(truth, called)})

    keys = ["species", "predictor", "n", "called", "sensitivity", "specificity", "precision",
            "accuracy", "accuracy_all"]
    with open(a.outdir / "metrics.tsv", "w") as fh:
        fh.write("\t".join(keys) + "\n")
        for r in rows:
            fh.write("\t".join(str(r[k]) if isinstance(r[k], (str, int)) else f"{r[k]:.3f}" for k in keys) + "\n")
    print((a.outdir / "metrics.tsv").read_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
