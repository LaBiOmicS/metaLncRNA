from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from metalncrna.config import Image, Manifest
from metalncrna.runner import Runner, RunResult
from metalncrna.tools import ALL

DATA = Path(__file__).parent / "data"
OUTPUTS = DATA / "outputs"


class FakeRunner(Runner):
    """Replays real tool outputs recorded from tests/data/small.fa instead of starting containers."""

    def __init__(self, cache_dir: Path, fail: dict[str, int] | None = None):
        super().__init__(engine="docker", cache_dir=cache_dir)
        self.fail = fail or {}
        self.calls: list[str] = []

    def image_identity(self, ref):
        return {"ref": ref, "image_id": "sha256:fake"}

    def run(self, ref, command, args, work_dir, cwd, log_path):
        tool = cwd.rsplit("/", 1)[-1]
        self.calls.append(tool)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        rc = self.fail.get(tool, 0)
        text = "fake run\n"
        if rc == 0:
            shutil.copytree(OUTPUTS / tool, work_dir / tool, dirs_exist_ok=True)
            if tool == "plek":  # reproduce PLEK's real behaviour: exit 1 after success
                rc, text = 1, "[..] Run complete\n"
        log_path.write_text(text)
        return RunResult(returncode=rc, seconds=0.01, argv=[command, *args])


@pytest.fixture
def fake_env(tmp_path):
    """A cache directory and a manifest pointing at (fake) images."""
    images = {n: Image(ref=f"example/{n}:test", build=None, upstream="test") for n in ALL}
    return tmp_path / "cache", Manifest(images=images, source="test")
