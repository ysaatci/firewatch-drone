# FireWatch — Project Plan

Autonomous thermal drones that find wildfire hotspots and map fire fronts in real time,
built simulation-first by a software team on off-the-shelf drone hardware.

## 1. Problem & focus

Turkey's Forestry Directorate (OGM) already runs lookout towers, camera networks, and air
assets for *initial* detection. The gaps where drones clearly add value:

| Use case | Why drones | Priority |
|---|---|---|
| **Post-fire hotspot detection (mop-up)** | Smoldering spots reignite; thermal drones find them fast, day or night | **P1** |
| **Live fire-front mapping** | Commanders need the current perimeter; helicopters can't hover over it all night | **P1** |
| Night / smoke patrols in high-risk zones | Thermal sees through darkness and light smoke | P2 |
| Spread prediction from drone data | Perimeter + wind + fuel → where it goes next | P2 |

We **do not build airframes**. We build the software layer: detection, geolocation,
autonomous missions, fire modelling, and the operator dashboard.

## 2. System architecture

```
 ┌──────────────┐   video (RGB + thermal)   ┌──────────────────┐
 │ Drone        │ ────────────────────────► │ detection/       │  YOLO fire/smoke/hotspot
 │ (PX4 / DJI)  │                           └────────┬─────────┘
 │              │   telemetry (pose, gimbal)         │ pixel boxes
 │              │ ─────────────────────────┐         ▼
 └──────▲───────┘                          │  ┌──────────────────┐
        │ missions                         └─►│ geo/             │  pixel → GPS
 ┌──────┴───────┐                             └────────┬─────────┘
 │ mission/     │ ◄── re-task on detection ────────────┤ geolocated detections
 │ patrol plans │                                      ▼
 └──────────────┘                             ┌──────────────────┐
                                              │ firesim/         │  perimeter + spread forecast
                                              └────────┬─────────┘
                                                       ▼
                                              ┌──────────────────┐
                                              │ dashboard/       │  map for operators
                                              └──────────────────┘
```

In simulation, the drone box is **PX4 SITL + Gazebo**; everything else is the same code
that will run against a real drone.

## 3. Technical roadmap

### Phase 0 — Foundations (week 1)
- [x] Repo, package layout, CI (lint + tests)
- [ ] Install Python 3.11+, create venv, `pip install -e ".[dev]"`, tests green locally
- [ ] Install WSL2 + Ubuntu 22.04 (needed for PX4 SITL on Windows) — see `sim/README.md`

### Phase 1 — Fire & smoke detection (weeks 2–4)
- [x] Download D-Fire (RGB fire/smoke, YOLO format) → `data/dfire` (17,221 train / 4,306 test)
- [x] Baseline: fine-tune YOLO on D-Fire (`firewatch.detection.train`)

  yolo11n, 20 epochs, 640 px, RTX 5050 (~63 min). On the D-Fire test split:

  | class | precision | recall | mAP50 | mAP50-95 |
  |---|---|---|---|---|
  | smoke | 0.794 | 0.727 | 0.800 | 0.482 |
  | fire  | 0.700 | 0.582 | 0.678 | 0.350 |
  | **all** | | | **0.739** | **0.416** |

  2.7 ms/frame inference — real-time onboard is feasible. Caveat: D-Fire is mostly
  ground-level imagery, so this number does *not* transfer to aerial views.
- [x] First aerial test: Wennington wildfire footage (CC BY 3.0), 278 sampled frames

  Smoke detected in **80%** of frames (246 boxes, peak confidence 0.86) — the smoke
  column is tracked continuously. Flames: only **5** boxes, peak confidence 0.38.
  So the ground-level → aerial gap is real and it is concentrated on *flames*, not smoke.
  Practical read: a D-Fire-trained model is already usable for smoke-column spotting,
  but hotspot/flame work needs aerial + thermal training data.
- [ ] Download FLAME / FLAME 2 (aerial RGB + thermal from real burns)
- [ ] Fine-tune on aerial data to close the flame gap
- [ ] Thermal hotspot detector for the mop-up use case — RGB flames are the wrong sensor;
      start with thresholding + blob detection, then a learned model
- [ ] Collect false-positive cases: sun glare, hot rocks, vehicles, roofs
- **Exit:** mAP50 ≥ 0.6 on held-out aerial frames; demo video of detections on FLAME

### Phase 2 — Geolocation (weeks 4–5)
- [x] Pinhole pixel → ground GPS (flat-terrain) in `firewatch.geo`
- [ ] Use terrain elevation (SRTM / Copernicus DEM) instead of flat ground
- [ ] Fuse repeated detections across frames into one hotspot (clustering + confidence)
- **Exit:** < 10 m error in simulation at 100 m altitude

### Phase 3 — Autonomous patrols in simulation (weeks 5–8)
- [ ] PX4 SITL + Gazebo running in WSL2 (`sim/setup_px4_wsl.sh`)
- [x] Lawnmower coverage planner in `firewatch.mission.patrol`
- [ ] Upload & fly patrol via MAVSDK (`firewatch.mission.px4_client`)
- [ ] Gazebo world with real terrain of a Turkish fire area (e.g., Manavgat / Marmaris)
- [ ] Simulated camera feed → detector → geolocation loop
- [ ] Re-tasking: on detection, orbit the hotspot and confirm
- **Exit:** drone autonomously patrols an area, detects a simulated fire, reports its GPS

### Phase 4 — Fire spread modelling (weeks 8–10)
- [x] Simple cellular-automaton spread model (`firewatch.firesim`) for integration testing
- [ ] Integrate Cell2Fire or ForeFire with real fuel + slope + wind data
- [ ] Update forecast from drone-observed perimeter (data assimilation, start simple)
- **Exit:** forecast perimeter for +30/60 min shown alongside observed perimeter

### Phase 5 — Operator dashboard (weeks 10–12)
- [ ] Backend (FastAPI + WebSocket) streaming drone positions & detections
- [ ] Web map (MapLibre / Leaflet): drones, hotspots, perimeter, forecast
- [ ] Mission controls: draw area → generate patrol → launch
- **Exit:** end-to-end demo in simulation, recorded as a pitch video

### Phase 6 — Real hardware (month 4+)
- [ ] Get SHGM İHA-1 pilot licence; register the drone
- [ ] Off-the-shelf PX4 drone with thermal camera (or DJI + SDK)
- [ ] Record own thermal footage (controlled burns, bonfires, BBQs) to fine-tune the detector
- [ ] Run the *same* mission + detection stack on the real drone
- **Exit:** field demo finding a planted heat source

## 4. Resources

- **Sim:** PX4 (px4.io), Gazebo (gazebosim.org), MAVSDK (mavsdk.mavlink.io), QGroundControl
- **Datasets:** D-Fire (github.com/gaiasd/DFireDataset), FLAME (IEEE DataPort), FASDD, NASA FIRMS
- **Fire models:** Cell2Fire, ForeFire, FARSITE/FlamMap (USFS)
- **Terrain:** Copernicus DEM, OpenTopography
