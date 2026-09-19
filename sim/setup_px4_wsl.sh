#!/usr/bin/env bash
# Install PX4-Autopilot and Gazebo on Ubuntu 22.04 (WSL2).
set -euo pipefail

sudo apt-get update
sudo apt-get install -y git python3-pip python3-venv

if [ ! -d "$HOME/PX4-Autopilot" ]; then
  git clone https://github.com/PX4/PX4-Autopilot.git --recursive "$HOME/PX4-Autopilot"
fi

bash "$HOME/PX4-Autopilot/Tools/setup/ubuntu.sh"

echo
echo "Done. Restart this shell, then run:"
echo "  cd ~/PX4-Autopilot && make px4_sitl gz_x500"
