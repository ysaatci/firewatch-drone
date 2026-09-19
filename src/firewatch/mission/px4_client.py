"""Upload and fly a patrol on PX4 (SITL or real) via MAVSDK.

Requires: pip install -e ".[sim]" and a running PX4 SITL (see sim/README.md).

    python -m firewatch.mission.px4_client --width 400 --height 300
"""

from __future__ import annotations

import argparse
import asyncio

from firewatch.mission.patrol import Waypoint, plan_patrol


async def fly_patrol(waypoints: list[Waypoint], address: str = "udp://:14540") -> None:
    from mavsdk import System
    from mavsdk.mission import MissionItem, MissionPlan

    drone = System()
    await drone.connect(system_address=address)

    print("Waiting for drone...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            break
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            break

    items = [
        MissionItem(
            wp.lat,
            wp.lon,
            wp.alt_agl,
            10.0,  # speed m/s
            True,  # fly through
            -90.0,  # gimbal pitch: straight down
            float("nan"),
            MissionItem.CameraAction.NONE,
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            float("nan"),
            MissionItem.VehicleAction.NONE,
        )
        for wp in waypoints
    ]
    await drone.mission.set_return_to_launch_after_mission(True)
    await drone.mission.upload_mission(MissionPlan(items))
    print(f"Uploaded {len(items)} waypoints, arming...")
    await drone.action.arm()
    await drone.mission.start_mission()

    async for progress in drone.mission.mission_progress():
        print(f"Mission progress: {progress.current}/{progress.total}")
        if progress.current == progress.total:
            break


def main() -> None:
    ap = argparse.ArgumentParser()
    # Default origin is PX4 SITL's default home (Zurich); set to your sim world's home.
    ap.add_argument("--lat", type=float, default=47.397742)
    ap.add_argument("--lon", type=float, default=8.545594)
    ap.add_argument("--width", type=float, default=400)
    ap.add_argument("--height", type=float, default=300)
    ap.add_argument("--alt", type=float, default=60)
    ap.add_argument("--address", default="udp://:14540")
    args = ap.parse_args()

    wps = plan_patrol(args.lat, args.lon, args.width, args.height, alt_agl=args.alt)
    asyncio.run(fly_patrol(wps, args.address))


if __name__ == "__main__":
    main()
