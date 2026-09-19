"""Run a trained fire/smoke detector on an image, video, or folder.

Requires: pip install -e ".[detection]"

    python -m firewatch.detection.infer --weights runs/detect/fire_smoke/weights/best.pt \
        --source path/to/flame_video.mp4
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def center(self) -> tuple[float, float]:
        """Box centre in pixels; feed this to firewatch.geo.pixel_to_latlon."""
        return (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2


def detect(model, frame, conf: float = 0.35) -> list[Detection]:
    """Detect fire/smoke in a single frame (numpy image or path)."""
    result = model.predict(frame, conf=conf, verbose=False)[0]
    return [
        Detection(result.names[int(c)], float(p), *map(float, xyxy))
        for xyxy, c, p in zip(result.boxes.xyxy, result.boxes.cls, result.boxes.conf, strict=True)
    ]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--conf", type=float, default=0.35)
    args = ap.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.weights)
    # save=True writes annotated output to runs/detect/predict*
    for result in model.predict(args.source, conf=args.conf, stream=True, save=True):
        if len(result.boxes):
            labels = [result.names[int(c)] for c in result.boxes.cls]
            print(f"{result.path}: {labels}")


if __name__ == "__main__":
    main()
