"""The seven predictors.

Each tool is described by: the image it runs in, the command line it receives (always the authors'
documented interface, with default parameters), and a parser that reads the tool's *own* verdict
(coding / noncoding) from its output. The verdict is never re-derived from scores, except for CPAT,
which does not emit a label: there the authors' published species cut-off is applied.

A sequence a tool does not report on (e.g. PLEK skips sequences <= 200 nt, CNCI skips sequences
with ambiguous bases) is an abstention: that tool simply does not vote for it.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

CODING = "coding"
NONCODING = "noncoding"

SPECIES = ("human", "mouse", "fly", "zebrafish", "plant", "other")


@dataclass(frozen=True)
class Call:
    label: str  # CODING | NONCODING
    score: float | None = None  # the tool's native score, reported for information only
    note: str = ""


@dataclass
class Options:
    species: str = "human"
    threads: int = 4


class ParseError(RuntimeError):
    pass


class Tool:
    name: str
    command: str
    citation: str

    def unavailable_reason(self, opts: Options) -> str | None:
        """Why this tool cannot run for these options (e.g. no model for the species)."""
        return None

    def args(self, opts: Options) -> list[str]:
        raise NotImplementedError

    def succeeded(self, returncode: int, log_text: str) -> bool:
        """Whether the run completed. Most tools follow the exit-code convention."""
        return returncode == 0

    def parse(self, out_dir: Path, opts: Options) -> dict[str, Call]:
        raise NotImplementedError

    # helpers --------------------------------------------------------------
    @staticmethod
    def _label(raw: str, coding: set[str], noncoding: set[str], where: str) -> str:
        if raw in coding:
            return CODING
        if raw in noncoding:
            return NONCODING
        raise ParseError(f"{where}: unexpected label {raw!r}")

    @staticmethod
    def _float(raw: str) -> float | None:
        try:
            return float(raw)
        except ValueError:
            return None


INPUT = "/work/input.fa"


def _rows(path: Path):
    if not path.exists():
        raise ParseError(f"expected output not found: {path.name}")
    with open(path, newline="") as fh:
        yield from csv.reader(fh, delimiter="\t")


def _first_token(s: str) -> str:
    return s.lstrip(">").split()[0]


class CNCI(Tool):
    name = "cnci"
    command = "run-cnci"
    citation = "Sun L. et al. (2013) Nucleic Acids Res 41:e166"

    def args(self, opts):
        model = "pl" if opts.species == "plant" else "ve"
        return ["-f", INPUT, "-o", "/work/cnci/out", "-m", model, "-p", str(opts.threads)]

    def parse(self, out_dir, opts):
        calls = {}
        rows = _rows(out_dir / "out" / "CNCI.index")
        header = next(rows, None)
        if not header or header[:3] != ["Transcript ID", "index", "score"]:
            raise ParseError(f"CNCI.index: unexpected header {header}")
        for r in rows:
            if r:
                calls[_first_token(r[0])] = Call(
                    self._label(r[1], {"coding"}, {"noncoding"}, "CNCI"), self._float(r[2])
                )
        return calls


class CPPred(Tool):
    name = "cppred"
    command = "run-cppred"
    citation = "Tong X., Liu S. (2019) Nucleic Acids Res 47:e43"

    def _model(self, opts):
        return "Human" if opts.species == "human" else "Integrated"

    def args(self, opts):
        m = self._model(opts)
        return [
            "-i", INPUT,
            "-hex", f"/opt/CPPred/Hexamer/{m}_Hexamer.tsv",
            "-r", f"/opt/CPPred/{m}_Model/{m}.range",
            "-mol", f"/opt/CPPred/{m}_Model/{m}.model",
            "-spe", m,
            "-o", "/work/cppred/cppred.txt",
        ]

    def parse(self, out_dir, opts):
        rows = _rows(out_dir / "cppred.txt")
        header = next(rows, None)
        if not header or header[0] != "#ID" or header[-2:] != ["table", "coding_potential"]:
            raise ParseError(f"CPPred: unexpected header {header and header[:3]}…")
        calls = {}
        for r in rows:
            if r:
                calls[r[0]] = Call(
                    self._label(r[-2], {"coding"}, {"noncoding"}, "CPPred"), self._float(r[-1])
                )
        return calls


class LGC(Tool):
    name = "lgc"
    command = "run-lgc"
    citation = "Wang G. et al. (2019) Bioinformatics 35:2949-2956"

    def args(self, opts):
        return [INPUT, "/work/lgc/lgc.txt"]

    def parse(self, out_dir, opts):
        # Data columns: name, ORF length, GC, coding potential score, label, pc, pnc, fc, fnc.
        # (The tool's own '# Sequence Name …' header lists the label last; the data puts it 5th.)
        calls = {}
        for r in _rows(out_dir / "lgc.txt"):
            if not r or r[0].startswith("#"):
                continue
            calls[r[0]] = Call(
                self._label(r[4], {"Coding"}, {"Non-coding"}, "LGC"), self._float(r[3])
            )
        return calls


class CPAT(Tool):
    name = "cpat"
    command = "run-cpat"
    citation = "Wang L. et al. (2013) Nucleic Acids Res 41:e74"
    # Optimum cut-offs published by the authors (CPAT documentation, "How to choose cutoff").
    CUTOFF = {"human": 0.364, "mouse": 0.44, "fly": 0.39, "zebrafish": 0.38}
    PREFIX = {"human": "Human", "mouse": "Mouse", "fly": "Fly", "zebrafish": "Zebrafish"}

    def unavailable_reason(self, opts):
        if opts.species not in self.PREFIX:
            return f"CPAT has no published model for species '{opts.species}'"
        return None

    def args(self, opts):
        p = self.PREFIX[opts.species]
        return [
            "-x", f"/opt/cpat/models/{p}_Hexamer.tsv",
            "-d", f"/opt/cpat/models/{p}_logitModel.RData",
            "-g", INPUT,
            "-o", "/work/cpat/cpat",
        ]

    def parse(self, out_dir, opts):
        cutoff = self.CUTOFF[opts.species]
        # CPAT upper-cases sequence names; internal IDs are lower-case by construction.
        rows = _rows(out_dir / "cpat.ORF_prob.best.tsv")
        header = next(rows, None)
        if not header or "seq_ID" not in header or "Coding_prob" not in header:
            raise ParseError(f"CPAT: unexpected header {header}")
        i_id, i_p = header.index("seq_ID"), header.index("Coding_prob")
        calls = {}
        for r in rows:
            if r:
                p = float(r[i_p])
                calls[r[i_id].lower()] = Call(CODING if p >= cutoff else NONCODING, p)
        no_orf = out_dir / "cpat.no_ORF.txt"
        if no_orf.exists():
            for line in no_orf.read_text().split():
                # No ORF of at least --min-orf (75 nt): CPAT has nothing that could code.
                calls.setdefault(line.lower(), Call(NONCODING, 0.0, "no ORF found"))
        return calls


class CPC2(Tool):
    name = "cpc2"
    command = "run-cpc2"
    citation = "Kang Y.-J. et al. (2017) Nucleic Acids Res 45:W12-W16"

    def args(self, opts):
        return ["-i", INPUT, "-o", "/work/cpc2/cpc2"]

    def parse(self, out_dir, opts):
        rows = _rows(out_dir / "cpc2.txt")
        header = next(rows, None)
        if not header or header[0] != "#ID" or header[-2:] != ["coding_probability", "label"]:
            raise ParseError(f"CPC2: unexpected header {header}")
        calls = {}
        for r in rows:
            if r:
                calls[r[0]] = Call(
                    self._label(r[-1], {"coding"}, {"noncoding"}, "CPC2"), self._float(r[-2])
                )
        return calls


class PLEK(Tool):
    name = "plek"
    command = "run-plek"
    citation = "Li A. et al. (2014) BMC Bioinformatics 15:311"

    def args(self, opts):
        return ["-fasta", INPUT, "-out", "/work/plek/plek", "-thread", str(opts.threads)]

    def succeeded(self, returncode, log_text):
        # PLEK.py ends with sys.exit(1) even after a successful run; its error paths also exit 1
        # but never print the completion message.
        return returncode in (0, 1) and "Run complete" in log_text

    def parse(self, out_dir, opts):
        calls = {}
        for r in _rows(out_dir / "plek"):
            if r:
                calls[_first_token(r[2])] = Call(
                    self._label(r[0], {"Coding"}, {"Non-coding"}, "PLEK"), self._float(r[1])
                )
        return calls


class RNAsamba(Tool):
    name = "rnasamba"
    command = "run-rnasamba"
    citation = "Camargo A.P. et al. (2020) NAR Genomics and Bioinformatics 2:lqz024"

    def args(self, opts):
        return [
            "classify", "/work/rnasamba/rnasamba.tsv", INPUT,
            "/opt/rnasamba/full_length_weights.hdf5",
        ]

    def parse(self, out_dir, opts):
        rows = _rows(out_dir / "rnasamba.tsv")
        header = next(rows, None)
        if header != ["sequence_name", "coding_score", "classification"]:
            raise ParseError(f"RNAsamba: unexpected header {header}")
        calls = {}
        for r in rows:
            if r:
                calls[_first_token(r[0])] = Call(
                    self._label(r[2], {"coding"}, {"noncoding"}, "RNAsamba"), self._float(r[1])
                )
        return calls


ALL: dict[str, Tool] = {t.name: t for t in (CNCI(), CPPred(), LGC(), CPAT(), CPC2(), PLEK(), RNAsamba())}
