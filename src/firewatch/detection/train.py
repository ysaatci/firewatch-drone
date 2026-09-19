"""Fine-tune a YOLO model for fire/smoke detection.

Requires: pip install -e ".[detection]"

    python -m firewatch.detection.train --data configs/dfire.yaml --epochs 50
"""

from __future__ import annotations

import argparse


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="configs/dfire.yaml")
    ap.add_argument("--model", default="yolov8n.pt", help="pretrained weights to start from")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default=None, help="e.g. 0 for first GPU, cpu for CPU")
    ap.add_argument("--name", default="fire_smoke")
    args = ap.parse_args()

    from ultralytics import YOLO

    model = YOLO(args.model)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        project="runs/detect",
        name=args.name,
    )
    metrics = model.val()
    print(f"mAP50: {metrics.box.map50:.3f}  mAP50-95: {metrics.box.map:.3f}")


if __name__ == "__main__":
    main()
