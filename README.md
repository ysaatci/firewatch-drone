# FireWatch

Autonomous thermal drones that detect wildfire hotspots and map fire fronts in real time.
Built simulation-first: the detection, geolocation, mission and fire-modelling code runs
against PX4 SITL + Gazebo today and against a real drone later.

See **[docs/PLAN.md](docs/PLAN.md)** for the roadmap, architecture and business track.

## Layout

```
src/firewatch/
  detection/   YOLO fire/smoke/hotspot training & inference
  geo/         pixel → GPS geolocation from drone pose + camera
  mission/     patrol planning + PX4 (MAVSDK) mission upload
  firesim/     fire spread models (simple CA now, Cell2Fire/ForeFire later)
  dashboard/   operator web dashboard (Phase 5)
sim/           PX4 SITL + Gazebo setup (WSL2 on Windows)
configs/       dataset / training configs
data/          datasets (git-ignored)
tests/
```

## Quick start

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash; use .venv/bin/activate on Linux/WSL
pip install -e ".[dev]"
pytest
```

Optional extras:

```bash
pip install -e ".[detection]"      # YOLO training/inference (ultralytics, opencv)
pip install -e ".[sim]"            # MAVSDK for talking to PX4
```

## Try it

```bash
# Where on the ground is the pixel (640, 360) of a 1280x720 frame?
python -m firewatch.geo.geolocate

# Generate a lawnmower patrol over a 1 km x 600 m area
python -m firewatch.mission.patrol

# Run the toy fire spread model and print the grid
python -m firewatch.firesim.spread

# Train a fire/smoke detector (after downloading D-Fire, see configs/dfire.yaml)
python -m firewatch.detection.train --data configs/dfire.yaml --epochs 50 --device 0

# Render an operator-style video: detections + GPS of each hotspot
python -m firewatch.detection.video_demo --weights runs/detect/fire_smoke/weights/best.pt     --source data/footage/wennington_aerial_2022.webm --out out/demo.mp4
```

Demo footage is git-ignored; see [data/footage/CREDITS.md](data/footage/CREDITS.md) for
attribution (aerial Wennington wildfire video by Harri Healey, CC BY 3.0).

Flying in simulation: see [sim/README.md](sim/README.md).
