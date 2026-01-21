#!/usr/bin/env bash
set -e

echo "=== Submarine Raspberry Pi Setup ==="

# Ensure script is not run as root
if [[ "$EUID" -eq 0 ]]; then
  echo "Please run this script as a normal user, not root."
  exit 1
fi

echo "[1/6] Updating system..."
sudo apt update

echo "[2/6] Installing system dependencies..."
sudo apt install -y \
  python3 \
  python3-venv \
  python3-pip \
  python3-dev \
  python3-setuptools \
  python3-libgpiod \
  libgpiod-dev \
  i2c-tools

echo "[3/6] Enabling I2C..."
sudo raspi-config nonint do_i2c 0

echo "[4/6] Creating virtual environment..."
if [[ ! -d "venv" ]]; then
  python3 -m venv venv
else
  echo "Virtual environment already exists."
fi

echo "[5/6] Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "[6/6] Setup complete!"
echo
echo "IMPORTANT:"
echo "  - Reboot before running code:"
echo "      sudo reboot"
echo
echo "After reboot:"
echo "  source venv/bin/activate"
echo "  python -m src.tests.test_motors"
