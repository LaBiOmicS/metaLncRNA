"""Run a command inside a tool container with Docker or Apptainer/Singularity.

Every tool sees the same layout regardless of the engine:

    /work    read-write: the run's work directory (renamed input FASTA + one sub-directory per tool)

Each image is self-contained (tool, dependencies and model files), so nothing else is mounted.

Containers run as the calling user, without network (Docker), with a clean environment, and are
removed afterwards.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


class RunnerError(RuntimeError):
    pass


@dataclass
class RunResult:
    returncode: int
    seconds: float
    argv: list[str]


@dataclass
class Runner:
    engine: str  # "docker" | "apptainer" | "singularity"
    cache_dir: Path
    extra_args: list[str] = field(default_factory=list)

    # ------------------------------------------------------------------ discovery
    @staticmethod
    def detect(preferred: str | None, cache_dir: Path) -> "Runner":
        order = [preferred] if preferred else ["docker", "apptainer", "singularity"]
        for engine in order:
            if engine and shutil.which(engine):
                if engine == "docker" and not _docker_alive():
                    if preferred:
                        raise RunnerError("docker is installed but the daemon is not reachable")
                    continue
                return Runner(engine=engine, cache_dir=cache_dir)
        raise RunnerError(
            f"no container engine found (tried: {', '.join(e for e in order if e)}). "
            "Install Docker or Apptainer."
        )

    # ------------------------------------------------------------------ images
    def sif_path(self, ref: str) -> Path:
        digest = hashlib.sha256(ref.encode()).hexdigest()[:16]
        return self.cache_dir / "images" / f"{digest}.sif"

    def has_image(self, ref: str) -> bool:
        if self.engine == "docker":
            return subprocess.run(["docker", "image", "inspect", ref], capture_output=True).returncode == 0
        return self.sif_path(ref).exists()

    def pull(self, ref: str, local_only: bool = False) -> None:
        """Make ``ref`` available. ``local_only``: the image only exists in the local Docker daemon."""
        if self.engine == "docker":
            if not local_only:
                _check(["docker", "pull", "--quiet", ref])
            return
        sif = self.sif_path(ref)
        sif.parent.mkdir(parents=True, exist_ok=True)
        src = f"docker-daemon://{ref}" if local_only else f"docker://{ref}"
        tmp = sif.with_suffix(".sif.part")
        _check([self.engine, "build", "--force", str(tmp), src])
        tmp.replace(sif)
        (sif.with_suffix(".json")).write_text(
            json.dumps({"ref": ref, "source": src, "sha256": _sha256(sif)}, indent=2)
        )

    def image_identity(self, ref: str) -> dict:
        """What exactly will run: Docker image ID / repo digests, or the SIF file hash."""
        if self.engine == "docker":
            out = subprocess.run(
                ["docker", "image", "inspect", ref, "--format", "{{json .}}"],
                capture_output=True, text=True,
            )
            if out.returncode != 0:
                return {"ref": ref, "error": "image not found"}
            info = json.loads(out.stdout)
            return {
                "ref": ref,
                "image_id": info.get("Id"),
                "repo_digests": info.get("RepoDigests", []),
                "labels": (info.get("Config") or {}).get("Labels") or {},
            }
        meta = self.sif_path(ref).with_suffix(".json")
        info = json.loads(meta.read_text()) if meta.exists() else {"ref": ref}
        info["sif"] = str(self.sif_path(ref))
        return info

    # ------------------------------------------------------------------ execution
    def run(
        self,
        ref: str,
        command: str,
        args: list[str],
        work_dir: Path,
        cwd: str,
        log_path: Path,
    ) -> RunResult:
        work_dir = work_dir.resolve()
        if self.engine == "docker":
            argv = [
                "docker", "run", "--rm", "--network", "none",
                "--user", f"{os.getuid()}:{os.getgid()}",
                "--env", "HOME=/tmp",
                "--volume", f"{work_dir}:/work",
                "--workdir", cwd,
                "--entrypoint", command,
                *self.extra_args,
                ref, *args,
            ]
        else:
            sif = self.sif_path(ref)
            if not sif.exists():
                raise RunnerError(f"image for {ref} not found; run `metalncrna setup`")
            argv = [
                self.engine, "exec", "--cleanenv", "--containall", "--no-home",
                "--bind", f"{work_dir}:/work",
                "--pwd", cwd,
                *self.extra_args,
                str(sif), command, *args,
            ]
        log_path.parent.mkdir(parents=True, exist_ok=True)
        start = time.monotonic()
        with open(log_path, "w") as log:
            log.write("$ " + " ".join(argv) + "\n\n")
            log.flush()
            proc = subprocess.run(argv, stdout=log, stderr=subprocess.STDOUT)
        return RunResult(returncode=proc.returncode, seconds=time.monotonic() - start, argv=argv)


def _docker_alive() -> bool:
    try:
        return subprocess.run(["docker", "info"], capture_output=True, timeout=20).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def _check(argv: list[str]) -> None:
    proc = subprocess.run(argv, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RunnerError(f"command failed ({proc.returncode}): {' '.join(argv)}\n{proc.stderr[-2000:]}")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()
