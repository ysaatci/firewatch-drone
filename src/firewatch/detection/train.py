"""Fine-tune a YOLO model for fire/smoke detection.

Requires: pip install -e ".[detection]"

    python -m firewatch.detection.train --data configs/dfire.yaml --epochs 50 --device 0

Note on --fraction: Ultralytics takes the *first* N% of the file list, not a random
sample. D-Fire is sorted by category, so a small fraction is mostly background images
with empty labels and trains to nothing. Use it only for pipeline checks, never to judge
model quality.

Note on --plots: plotting needs matplotlib's compiled backend, which Windows Application
Control blocks on some machines. Plots are off by default so a run can't die at the end
after hours of training; metrics are still written to results.csv.
"""

from __future__ import annotations

import argparse


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="configs/dfire.yaml")
    ap.add_argument("--model", default="yolo11n.pt", help="pretrained weights to start from")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--imgsz", type=int, default=640)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--device", default=None, help="e.g. 0 for first GPU, cpu for CPU")
    ap.add_argument("--name", default="fire_smoke")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--fraction", type=float, default=1.0, help="pipeline checks only; see above")
    ap.add_argument("--plots", action="store_true", help="save training plots (needs matplotlib)")
    args = ap.parse_args()

    from ultralytics import YOLO

    from firewatch.detection.data import resolve_dataset_yaml

    model = YOLO(args.model)
    results = model.train(
        data=str(resolve_dataset_yaml(args.data)),
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        device=args.device,
        workers=args.workers,
        fraction=args.fraction,
        name=args.name,
        plots=args.plots,
    )
    print(f"Weights: {results.save_dir}/weights/best.pt")

    metrics = model.val(plots=args.plots)
    print(f"mAP50: {metrics.box.map50:.3f}  mAP50-95: {metrics.box.map:.3f}")


if __name__ == "__main__":
    main()
