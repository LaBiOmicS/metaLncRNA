"""Command-line interface: setup, check, predict."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from . import __version__
from .config import Manifest, cache_dir
from .fasta import FastaError
from .pipeline import PipelineError, run
from .runner import Runner, RunnerError
from .tools import ALL, SPECIES, Options

log = logging.getLogger("metalncrna")


def _tools(value: str) -> list[str]:
    names = [t.strip().lower() for t in value.split(",") if t.strip()]
    bad = [n for n in names if n not in ALL]
    if bad:
        raise argparse.ArgumentTypeError(f"unknown tool(s): {', '.join(bad)} (choose from {', '.join(ALL)})")
    return list(dict.fromkeys(names))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="metalncrna",
        description="Consensus lncRNA identification: seven unmodified predictors, one majority vote.",
    )
    p.add_argument("--version", action="version", version=f"metalncrna {__version__}")
    p.add_argument("-v", "--verbose", action="store_true")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--engine", choices=["docker", "apptainer", "singularity"],
                        help="container engine (default: first available)")
    common.add_argument("--manifest", type=Path, help="alternative image manifest (TOML)")
    common.add_argument("--tools", type=_tools, default=list(ALL),
                        help=f"comma-separated subset (default: {','.join(ALL)})")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("setup", parents=[common], help="fetch (or build) the tool images")
    s.add_argument("--build-from", type=Path, metavar="DIR",
                   help="containers/ directory used to build images that are not in a registry")

    sub.add_parser("check", parents=[common], help="report what is installed and verified")

    r = sub.add_parser("predict", parents=[common], help="run the tools and build the consensus")
    r.add_argument("-i", "--input", type=Path, required=True, help="transcripts in FASTA format")
    r.add_argument("-o", "--outdir", type=Path, required=True)
    r.add_argument("-s", "--species", choices=SPECIES, default="human",
                   help="selects CPAT/CPPred/CNCI models (default: human)")
    r.add_argument("-j", "--jobs", type=int, default=3, help="tools run concurrently (default: 3)")
    r.add_argument("-t", "--threads", type=int, default=4, help="threads per tool where supported (default: 4)")
    r.add_argument("--min-agree", type=int, metavar="N",
                   help="lncrna.fasta: also require at least N noncoding votes")
    r.add_argument("--min-length", type=int, default=200,
                   help="lncrna.fasta: minimum transcript length in nt (default: 200)")
    r.add_argument("--allow-failures", action="store_true",
                   help="build the consensus even if some tools fail (default: abort)")
    r.add_argument("--force", action="store_true", help="ignore checkpoints and rerun every tool")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S",
    )
    try:
        manifest = Manifest.load(args.manifest)
        runner = Runner.detect(args.engine, cache_dir())
        log.info("engine: %s, cache: %s", runner.engine, runner.cache_dir)
        return {"setup": cmd_setup, "check": cmd_check, "predict": cmd_predict}[args.command](
            args, manifest, runner
        )
    except (RunnerError, FastaError, PipelineError) as exc:
        log.error("%s", exc)
        return 1


def cmd_setup(args, manifest: Manifest, runner: Runner) -> int:
    for name in args.tools:
        image = manifest.images[name]
        if image.local_only:
            exists = subprocess.run(["docker", "image", "inspect", image.ref], capture_output=True).returncode == 0
            if not exists:
                if not (args.build_from and image.build):
                    raise RunnerError(f"{name}: image {image.ref} is not in any registry; use --build-from containers/")
                log.info("%s: building %s from %s", name, image.ref, args.build_from / image.build)
                proc = subprocess.run(["docker", "build", "-t", image.ref, str(args.build_from / image.build)])
                if proc.returncode != 0:
                    raise RunnerError(f"{name}: docker build failed")
        if runner.has_image(image.ref):
            log.info("image ok: %s (%s)", name, image.ref)
            continue
        log.info("%s: fetching %s", name, image.ref)
        runner.pull(image.ref, local_only=image.local_only)
        log.info("image ok: %s", name)
    return 0


def cmd_check(args, manifest: Manifest, runner: Runner) -> int:
    ok = True
    for name in args.tools:
        present = runner.has_image(manifest.images[name].ref)
        ok &= present
        print(f"image  {name:9} {'ok' if present else 'MISSING'}  {manifest.images[name].ref}")
    print("ready" if ok else "not ready: run `metalncrna setup`")
    return 0 if ok else 1


def cmd_predict(args, manifest: Manifest, runner: Runner) -> int:
    if not args.input.is_file():
        raise FastaError(f"input not found: {args.input}")
    summary = run(
        input_fasta=args.input, out_dir=args.outdir, tool_names=args.tools,
        opts=Options(species=args.species, threads=args.threads),
        runner=runner, manifest=manifest, jobs=args.jobs, min_agree=args.min_agree,
        min_length=args.min_length, allow_failures=args.allow_failures, force=args.force,
    )
    c = summary["consensus"]
    log.info(
        "consensus over %d sequences: %d coding, %d noncoding, %d ambiguous, %d unclassified",
        summary["sequences"], c["coding"], c["noncoding"], c["ambiguous"], c["unclassified"],
    )
    log.info("%d sequences written to %s", summary["lncrna_fasta"]["sequences"], args.outdir / "lncrna.fasta")
    return 0


if __name__ == "__main__":
    sys.exit(main())
