"""Run the selected tools on one FASTA file and build the consensus."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import logging
import platform
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from . import __version__
from .config import Manifest
from .consensus import vote
from .fasta import PreparedInput, prepare, write_subset
from .runner import Runner
from .tools import ALL, NONCODING, Call, Options, ParseError, Tool

log = logging.getLogger("metalncrna")

DONE_FILE = ".metalncrna-done.json"


@dataclass
class ToolRun:
    name: str
    status: str = "pending"  # ok | reused | failed | unavailable
    message: str = ""
    calls: dict[str, Call] = field(default_factory=dict)
    image: dict = field(default_factory=dict)
    argv: list[str] = field(default_factory=list)
    seconds: float | None = None


class PipelineError(RuntimeError):
    pass


def run(
    input_fasta: Path,
    out_dir: Path,
    tool_names: list[str],
    opts: Options,
    runner: Runner,
    manifest: Manifest,
    jobs: int = 3,
    min_agree: int | None = None,
    min_length: int = 200,
    allow_failures: bool = False,
    force: bool = False,
) -> dict:
    out_dir = out_dir.resolve()
    work = out_dir / "work"
    logs = out_dir / "logs"
    work.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    started = dt.datetime.now(dt.timezone.utc)
    prepared = prepare(input_fasta, work / "input.fa")
    for w in prepared.warnings:
        log.warning(w)
    log.info("%d sequences read from %s", len(prepared.records), input_fasta)

    runs = {name: ToolRun(name) for name in tool_names}
    runnable: list[Tool] = []
    for name in tool_names:
        tool = ALL[name]
        if reason := tool.unavailable_reason(opts):
            runs[name].status, runs[name].message = "unavailable", reason
            log.warning("%s skipped: %s", name, reason)
        else:
            runnable.append(tool)

    def one(tool: Tool) -> None:
        tr = runs[tool.name]
        try:
            _run_tool(tool, tr, prepared, opts, runner, manifest, work, logs, force)
        except Exception as exc:  # recorded per tool; decided on below
            tr.status, tr.message = "failed", str(exc)
            log.error("%s failed: %s (see %s)", tool.name, exc, logs / f"{tool.name}.log")

    with ThreadPoolExecutor(max_workers=max(1, jobs)) as pool:
        list(pool.map(one, runnable))

    failed = [r.name for r in runs.values() if r.status == "failed"]
    if failed and not allow_failures:
        _write_provenance(out_dir, prepared, runs, opts, runner, manifest, started, None)
        raise PipelineError(
            f"tool(s) failed: {', '.join(failed)}. Logs in {logs}. "
            "Use --allow-failures to build the consensus from the remaining tools."
        )
    voters = [r for r in runs.values() if r.status in ("ok", "reused")]
    if not voters:
        raise PipelineError("no tool produced results")

    summary = _write_results(out_dir, prepared, voters, min_agree, min_length)
    _write_provenance(out_dir, prepared, runs, opts, runner, manifest, started, summary)
    return summary


# --------------------------------------------------------------------------- one tool
def _run_tool(tool, tr, prepared: PreparedInput, opts, runner, manifest, work, logs, force):
    image = manifest.images[tool.name]
    args = tool.args(opts)
    tr.image = runner.image_identity(image.ref)
    key = _checkpoint_key(prepared.sha256, tr.image, tool.command, args)

    tool_dir = work / tool.name
    done = tool_dir / DONE_FILE
    if not force and done.exists() and json.loads(done.read_text()).get("key") == key:
        tr.calls = _parse_checked(tool, tool_dir, opts, prepared)
        tr.status, tr.message = "reused", "checkpoint matched"
        log.info("%s: reusing previous result (same input, image and parameters)", tool.name)
        return

    if tool_dir.exists():
        shutil.rmtree(tool_dir)
    tool_dir.mkdir(parents=True)
    log.info("%s: running", tool.name)
    res = runner.run(
        image.ref, tool.command, args,
        work_dir=work,
        cwd=f"/work/{tool.name}", log_path=logs / f"{tool.name}.log",
    )
    tr.argv, tr.seconds = res.argv, round(res.seconds, 2)
    log_text = (logs / f"{tool.name}.log").read_text(errors="replace")
    if not tool.succeeded(res.returncode, log_text):
        raise RuntimeError(f"exit code {res.returncode}")
    tr.calls = _parse_checked(tool, tool_dir, opts, prepared)
    done.write_text(json.dumps({"key": key}))
    tr.status = "ok"
    log.info("%s: %d sequences classified in %.1fs", tool.name, len(tr.calls), res.seconds)


def _parse_checked(tool, tool_dir, opts, prepared) -> dict[str, Call]:
    calls = tool.parse(tool_dir, opts)
    unknown = set(calls) - set(prepared.to_original)
    if unknown:
        raise ParseError(f"{tool.name} reported unknown sequence IDs, e.g. {sorted(unknown)[:3]}")
    return calls


def _checkpoint_key(input_sha, image, command, args) -> str:
    blob = json.dumps(
        {"input": input_sha, "image": image, "command": command, "args": args,
         "metalncrna": __version__},
        sort_keys=True,
    )
    return hashlib.sha256(blob.encode()).hexdigest()


# --------------------------------------------------------------------------- outputs
def _write_results(out_dir, prepared: PreparedInput, voters: list[ToolRun], min_agree, min_length):
    names = [r.name for r in voters]
    counts = {"coding": 0, "noncoding": 0, "ambiguous": 0, "unclassified": 0}
    lnc_ids: set[str] = set()
    with open(out_dir / "results.tsv", "w") as fh:
        cols = ["sequence_id", "length"]
        cols += names + [f"{n}_score" for n in names]
        cols += ["votes_coding", "votes_noncoding", "voters", "consensus", "agreement"]
        fh.write("\t".join(cols) + "\n")
        for rec in prepared.records:
            iid = prepared.to_internal[rec.id]
            calls = {r.name: r.calls[iid] for r in voters if iid in r.calls}
            v = vote(calls)
            counts[v.label] += 1
            if (
                v.label == NONCODING
                and len(rec.seq) >= min_length
                and (min_agree is None or v.noncoding >= min_agree)
            ):
                lnc_ids.add(rec.id)
            row = [rec.id, str(len(rec.seq))]
            row += [calls[n].label if n in calls else "NA" for n in names]
            row += [_fmt(calls[n].score) if n in calls else "NA" for n in names]
            row += [str(v.coding), str(v.noncoding), str(v.voters), v.label,
                    "NA" if v.agreement is None else f"{v.agreement:.3f}"]
            fh.write("\t".join(row) + "\n")
    n_lnc = write_subset(prepared.records, lnc_ids, out_dir / "lncrna.fasta")
    return {
        "sequences": len(prepared.records),
        "consensus": counts,
        "lncrna_fasta": {"sequences": n_lnc, "min_length": min_length, "min_agree": min_agree},
        "voting_tools": names,
    }


def _fmt(x: float | None) -> str:
    return "NA" if x is None else f"{x:.6g}"


def _write_provenance(out_dir, prepared, runs, opts, runner, manifest, started, summary):
    prov = {
        "metalncrna_version": __version__,
        "started_utc": started.isoformat(timespec="seconds"),
        "finished_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "host": {"python": platform.python_version(), "platform": platform.platform()},
        "engine": runner.engine,
        "manifest": manifest.source,
        "input": {"sha256": prepared.sha256, "sequences": len(prepared.records)},
        "options": {"species": opts.species, "threads": opts.threads},
        "consensus_rule": "majority of the tools' own labels; abstentions excluded; tie = ambiguous",
        "tools": {
            r.name: {
                "status": r.status,
                "message": r.message,
                "upstream": manifest.images[r.name].upstream if r.name in manifest.images else "",
                "citation": ALL[r.name].citation,
                "image": r.image,
                "command": r.argv,
                "seconds": r.seconds,
                "sequences_classified": len(r.calls),
            }
            for r in runs.values()
        },
        "summary": summary,
    }
    (out_dir / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
