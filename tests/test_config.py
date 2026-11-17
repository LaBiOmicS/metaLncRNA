from pathlib import Path

from metalncrna.config import Image, Manifest
from metalncrna.tools import ALL

CONTAINERS = Path(__file__).parent.parent / "containers"


def test_builtin_manifest_is_complete():
    m = Manifest.load()
    assert set(m.images) == set(ALL)
    for name, img in m.images.items():
        assert img.local_only or "@sha256:" in img.ref, f"registry image not pinned by digest: {img.ref}"
        assert img.build and (CONTAINERS / img.build / "Dockerfile").is_file(), name


def test_every_image_has_a_launcher_matching_the_tool_command():
    for name, tool in ALL.items():
        assert tool.command == f"run-{name}"
        assert (CONTAINERS / name / tool.command).is_file()


def test_local_only_detection():
    assert Image("metalncrna/cnci:dev", None, "").local_only
    assert not Image("ghcr.io/org/cnci:1@sha256:" + "0" * 64, None, "").local_only
    assert not Image("quay.io/biocontainers/cpc2:1.0.1", None, "").local_only
