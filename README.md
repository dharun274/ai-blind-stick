# AI Blind Stick — Raspberry Pi minimal runtime

This repository contains the lightweight Raspberry Pi runtime for the AI Blind Stick project. It combines the tested USB camera, HC-SR04 ultrasonic sensor, GPS fallback interface, and a browser dashboard.

## Hardware

- HC-SR04: TRIG GPIO 23 (physical pin 16), ECHO GPIO 24 (physical pin 18) through a 5V-to-3.3V divider
- USB camera: `/dev/video0`
- NEO-6M GPS: `/dev/serial0` at 9600 baud (optional; fallback coordinates are used)

## Install

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip python3-opencv python3-rpi.gpio
python3 -m venv --system-site-packages .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Run dashboard

```bash
python3 dashboard.py
```

Open `http://<raspberry-pi-ip>:5000`. The dashboard provides live camera MJPEG, ultrasonic distance, GPS/fallback coordinates, and device status.

The runtime intentionally excludes the Windows-only SAPI voice code, the training dataset, and the PyTorch/Ultralytics stack so it fits a 32 GB Raspberry Pi system. AI inference can be added later with an exported ONNX model and OpenCV DNN.
