"""Image manifest and cache location."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from importlib import resources
from pathlib import Path


@dataclass(frozen=True)
class Image:
    ref: str
    build: str | None
    upstream: str

    @property
    def local_only(self) -> bool:
        """True for images that only exist in a local Docker daemon (no registry, no digest)."""
        first = self.ref.split("/", 1)[0]
        has_registry = "/" in self.ref and ("." in first or ":" in first or first == "localhost")
        return not has_registry and "@sha256:" not in self.ref


@dataclass(frozen=True)
class Manifest:
    images: dict[str, Image]
    source: str

    @staticmethod
    def load(path: Path | None = None) -> "Manifest":
        """Load ``path``, else $METALNCRNA_MANIFEST, else the manifest shipped with the package."""
        if path is None and (env := os.environ.get("METALNCRNA_MANIFEST")):
            path = Path(env)
        if path is None:
            text = resources.files("metalncrna").joinpath("manifest.toml").read_text()
            source = "builtin"
        else:
            text = Path(path).read_text()
            source = str(Path(path).resolve())
        data = tomllib.loads(text)
        images = {
            k: Image(ref=v["ref"], build=v.get("build"), upstream=v.get("upstream", ""))
            for k, v in data.get("images", {}).items()
        }
        return Manifest(images, source)


def cache_dir() -> Path:
    if env := os.environ.get("METALNCRNA_CACHE"):
        return Path(env).expanduser()
    base = os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    return Path(base) / "metalncrna"
