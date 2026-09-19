import pytest

yaml = pytest.importorskip("yaml")

from firewatch.detection.data import resolve_dataset_yaml  # noqa: E402


def test_relative_path_resolved_against_yaml(tmp_path):
    (tmp_path / "ds").mkdir()
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text("path: ds\ntrain: train/images\nval: test/images\n", encoding="utf-8")

    out = yaml.safe_load(resolve_dataset_yaml(cfg).read_text(encoding="utf-8"))

    assert out["path"] == str(tmp_path / "ds")
    assert out["train"] == "train/images"


def test_absolute_path_left_alone(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(f"path: {tmp_path.as_posix()}\ntrain: a\nval: b\n", encoding="utf-8")
    assert resolve_dataset_yaml(cfg) == cfg.resolve()
