"""Dataset config helpers.

Ultralytics resolves a relative ``path:`` in a dataset YAML against its own global
datasets directory, not against the YAML file — which silently looks in the wrong place.
We resolve it against the YAML's own location instead and hand Ultralytics an absolute one.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml


def resolve_dataset_yaml(config: str | Path) -> Path:
    """Return a dataset YAML whose ``path`` is absolute.

    If it already is, the original file is returned unchanged.
    """
    config = Path(config).resolve()
    data = yaml.safe_load(config.read_text(encoding="utf-8"))
    root = Path(data.get("path", "."))
    if root.is_absolute():
        return config

    data["path"] = str((config.parent / root).resolve())
    out = Path(tempfile.gettempdir()) / f"firewatch_{config.stem}_resolved.yaml"
    out.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return out
