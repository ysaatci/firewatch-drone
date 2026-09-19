"""Run a fire/smoke detector over drone footage and render an operator-style video.

Each frame gets detection boxes plus a side panel showing what the system would report
to a fire crew: the detection, its confidence, and the GPS position derived from the
drone pose (simulated telemetry here; real telemetry on a real flight).

    python -m firewatch.detection.video_demo \
        --weights runs/detect/fire_smoke/weights/best.pt \
        --source data/footage/wennington_aerial_2022.webm \
        --out out/wennington_detected.mp4

Requires: pip install -e ".[detection]"
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np

from firewatch.detection.infer import Detection, detect
from firewatch.geo.geolocate import Camera, DronePose, pixel_to_latlon

# BGR colours per class.
COLOURS = {"fire": (0, 90, 255), "smoke": (200, 200, 200)}
PANEL_W = 380


def annotate(frame, detections: list[Detection], pose: DronePose, cam: Camera, t: float):
    """Draw boxes on the frame and return it with an operator panel attached."""
    for det in detections:
        colour = COLOURS.get(det.label, (0, 255, 0))
        p1, p2 = (int(det.x1), int(det.y1)), (int(det.x2), int(det.y2))
        cv2.rectangle(frame, p1, p2, colour, 2)
        cv2.putText(
            frame,
            f"{det.label} {det.confidence:.2f}",
            (p1[0], max(p1[1] - 8, 14)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            colour,
            2,
        )

    h = frame.shape[0]
    panel = np.zeros((h, PANEL_W, 3), dtype=frame.dtype)
    y = 34
    cv2.putText(panel, "FIREWATCH", (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)
    y += 30
    for line in [
        f"t+{t:5.1f}s",
        f"lat {pose.lat:.5f}  lon {pose.lon:.5f}",
        f"alt {pose.alt_agl:.0f} m AGL  hdg {pose.yaw:03.0f}",
        f"gimbal {cam.pitch:.0f} deg down",
    ]:
        cv2.putText(panel, line, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)
        y += 22

    y += 12
    label = f"DETECTIONS: {len(detections)}" if detections else "SCANNING..."
    colour = (0, 90, 255) if detections else (120, 120, 120)
    cv2.putText(panel, label, (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colour, 2)
    y += 28

    for det in sorted(detections, key=lambda d: -d.confidence)[:6]:
        u, v = det.center
        ll = pixel_to_latlon(u, v, pose, cam)
        where = f"{ll[0]:.5f}, {ll[1]:.5f}" if ll else "beyond horizon"
        cv2.putText(
            panel,
            f"{det.label.upper():5s} {det.confidence:.0%}",
            (16, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            COLOURS.get(det.label, (0, 255, 0)),
            1,
        )
        y += 20
        cv2.putText(
            panel, f"  {where}", (16, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1
        )
        y += 26
        if y > h - 30:
            break

    return cv2.hconcat([panel, frame])


def run(
    weights: str,
    source: str,
    out: str,
    conf: float = 0.35,
    max_width: int = 1280,
    every: int = 1,
    pose: DronePose | None = None,
    cam: Camera | None = None,
) -> Path:
    from ultralytics import YOLO

    model = YOLO(weights)
    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        raise SystemExit(f"cannot open {source}")

    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    src_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    src_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    scale = min(1.0, max_width / src_w)
    w, h = int(src_w * scale), int(src_h * scale)

    # Simulated telemetry: a drone drifting north while filming at 45 degrees down.
    pose = pose or DronePose(lat=51.5215, lon=0.2140, alt_agl=120.0, yaw=0.0)  # Wennington, London
    cam = cam or Camera(width=w, height=h, hfov=70.0, pitch=45.0)

    Path(out).parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        out, cv2.VideoWriter_fourcc(*"mp4v"), src_fps / every, (w + PANEL_W, h)
    )

    i = frames = hits = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if i % every:
            i += 1
            continue
        if scale < 1.0:
            frame = cv2.resize(frame, (w, h))

        detections = detect(model, frame, conf=conf)
        hits += bool(detections)
        t = i / src_fps
        # Drift the drone 2 m/s north so the reported coordinates move like a real flight.
        flying = DronePose(pose.lat + t * 2 / 111_320, pose.lon, pose.alt_agl, pose.yaw)
        writer.write(annotate(frame, detections, flying, cam, t))

        frames += 1
        if frames % 50 == 0:
            print(f"  {frames} frames processed, {hits} with detections")
        i += 1

    cap.release()
    writer.release()
    print(f"Wrote {out}: {frames} frames, {hits} with detections ({hits / max(frames, 1):.0%})")
    return Path(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--weights", required=True)
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", default="out/demo.mp4")
    ap.add_argument("--conf", type=float, default=0.35)
    ap.add_argument("--max-width", type=int, default=1280)
    ap.add_argument("--every", type=int, default=1, help="process every Nth frame")
    args = ap.parse_args()
    run(args.weights, args.source, args.out, args.conf, args.max_width, args.every)


if __name__ == "__main__":
    main()
