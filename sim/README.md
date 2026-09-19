# Simulation: PX4 SITL + Gazebo

PX4's simulator runs on Linux. On Windows use **WSL2 with Ubuntu 22.04**.

## 1. Install WSL2 (PowerShell as admin, once)

```powershell
wsl --install -d Ubuntu-22.04
```

Reboot, open "Ubuntu 22.04", create a user.

## 2. Install PX4 + Gazebo (inside Ubuntu)

```bash
bash /mnt/c/Users/<you>/Documents/firewatch-drone/sim/setup_px4_wsl.sh
```

This clones PX4-Autopilot to `~/PX4-Autopilot` and runs PX4's official setup script
(takes a while). Restart the Ubuntu shell when it finishes.

## 3. Start the simulated drone

```bash
cd ~/PX4-Autopilot
make px4_sitl gz_x500
```

A Gazebo window opens with a quadcopter. Optionally install
[QGroundControl](https://qgroundcontrol.com) on Windows to watch it on a map.

## 4. Fly a FireWatch patrol

In a second Ubuntu shell, from the repo:

```bash
python3 -m venv .venv-wsl && source .venv-wsl/bin/activate
pip install -e ".[sim]"
python -m firewatch.mission.px4_client --width 400 --height 300 --alt 60
```

The drone arms, flies the lawnmower patrol, and returns home.

## Next steps (Phase 3)

- Gazebo world with real terrain for a Turkish fire area (Copernicus DEM heightmap)
- Downward camera on the drone; stream frames to `firewatch.detection`
- Visual "fire" objects placed in the world, driven by `firewatch.firesim`
