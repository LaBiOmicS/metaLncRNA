"""FASTA reading and the internal-ID scheme.

Tools mangle sequence names in different ways (CPAT upper-cases them, CNCI keeps the whole header,
CPPred keeps only the first token...). Instead of guessing how to map each tool's output back, every
sequence is renamed to a safe internal ID (``s0000001``) before any tool runs. Only the header
changes; the sequence bytes are passed through untouched. Results are mapped back to the original
IDs at the end.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


class FastaError(ValueError):
    pass


@dataclass(frozen=True)
class Record:
    id: str  # first whitespace-delimited token of the header
    header: str  # full header line without '>'
    seq: str


def read_fasta(path: Path) -> Iterator[Record]:
    header: str | None = None
    chunks: list[str] = []
    with open(path, encoding="utf-8", errors="strict") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\r\n")
            if line.startswith(">"):
                if header is not None:
                    yield _make(header, chunks)
                header = line[1:].strip()
                chunks = []
            elif header is None:
                if line.strip():
                    raise FastaError(f"{path}:{lineno}: sequence data before the first '>' header")
            else:
                chunks.append(line.strip())
    if header is not None:
        yield _make(header, chunks)


def _make(header: str, chunks: list[str]) -> Record:
    if not header:
        raise FastaError("empty FASTA header")
    return Record(id=header.split()[0], header=header, seq="".join(chunks))


def internal_id(index: int) -> str:
    return f"s{index:07d}"


@dataclass
class PreparedInput:
    fasta: Path  # renamed FASTA given to the tools
    records: list[Record]  # original records, in input order
    to_internal: dict[str, str]  # original id -> internal id
    to_original: dict[str, str]  # internal id -> original id
    sha256: str  # of the original input file
    warnings: list[str]


def prepare(input_fasta: Path, out_fasta: Path) -> PreparedInput:
    """Validate the input and write a copy whose headers are internal IDs."""
    records = list(read_fasta(input_fasta))
    if not records:
        raise FastaError(f"{input_fasta}: no sequences found")

    warnings: list[str] = []
    seen: set[str] = set()
    to_internal: dict[str, str] = {}
    to_original: dict[str, str] = {}
    with open(out_fasta, "w", encoding="ascii") as out:
        for i, rec in enumerate(records, 1):
            if rec.id in seen:
                raise FastaError(f"duplicate sequence ID: {rec.id!r}")
            seen.add(rec.id)
            if not rec.seq:
                raise FastaError(f"empty sequence: {rec.id!r}")
            try:
                rec.seq.encode("ascii")
            except UnicodeEncodeError as exc:
                raise FastaError(f"non-ASCII characters in sequence {rec.id!r}") from exc
            odd = set(rec.seq.upper()) - set("ACGTU")
            if odd:
                warnings.append(
                    f"{rec.id}: contains non-ACGTU characters {''.join(sorted(odd))}; "
                    "some tools (e.g. CNCI) skip such sequences, which then count as abstentions"
                )
            iid = internal_id(i)
            to_internal[rec.id] = iid
            to_original[iid] = rec.id
            out.write(f">{iid}\n")
            for j in range(0, len(rec.seq), 80):
                out.write(rec.seq[j : j + 80] + "\n")

    return PreparedInput(
        fasta=out_fasta,
        records=records,
        to_internal=to_internal,
        to_original=to_original,
        sha256=sha256_file(input_fasta),
        warnings=warnings,
    )


def write_subset(records: list[Record], ids: set[str], out: Path) -> int:
    """Write the records whose original ID is in ``ids``, keeping the original full headers."""
    n = 0
    with open(out, "w", encoding="utf-8") as fh:
        for rec in records:
            if rec.id in ids:
                fh.write(f">{rec.header}\n")
                for j in range(0, len(rec.seq), 80):
                    fh.write(rec.seq[j : j + 80] + "\n")
                n += 1
    return n


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()
