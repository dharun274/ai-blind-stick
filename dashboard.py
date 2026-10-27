import threading
import time

import cv2
from flask import Flask, Response, jsonify, render_template_string

from gps import get_gps_location

try:
    import RPi.GPIO as GPIO
except ImportError:
    GPIO = None

TRIG, ECHO = 23, 24
if GPIO:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ECHO, GPIO.IN)

app = Flask(__name__)
camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera_lock = threading.Lock()

PAGE = """<!doctype html>
<html><head><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>AI Blind Stick</title>
<style>body{font-family:Arial;background:#101820;color:#eef;margin:0;padding:18px}h1{margin-top:0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}.card{background:#1d2a35;border-radius:10px;padding:16px}img{width:100%;max-width:640px;border-radius:8px;background:#000}.value{font-size:1.6em;color:#60d394}small{color:#aab}</style>
</head><body><h1>AI Blind Stick</h1><div class='grid'>
<div class='card'><h2>Camera</h2><img src='/camera.mjpg'><p id='camera'>Connecting...</p></div>
<div class='card'><h2>Ultrasonic</h2><div class='value' id='distance'>--</div><small>GPIO 23/24</small></div>
<div class='card'><h2>GPS</h2><div id='gps'>Loading...</div><small>Fallback is used when no fix is available</small></div>
</div><script>
async function update(){try{let r=await fetch('/api/status');let d=await r.json();document.querySelector('#distance').textContent=d.distance_cm===null?'No echo':d.distance_cm.toFixed(1)+' cm';document.querySelector('#gps').innerHTML=`${d.gps.location}<br>Lat: ${d.gps.latitude.toFixed(6)}<br>Lon: ${d.gps.longitude.toFixed(6)}`;document.querySelector('#camera').textContent=d.camera?'Camera active':'Camera unavailable';}catch(e){document.querySelector('#camera').textContent='Dashboard connection error';}}update();setInterval(update,1000);
</script></body></html>"""

def sonar_distance():
    if not GPIO:
        return None
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.0002)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)
    deadline = time.monotonic() + 0.03
    while GPIO.input(ECHO) == 0:
        if time.monotonic() > deadline:
            return None
    start = time.monotonic()
    while GPIO.input(ECHO) == 1:
        if time.monotonic() > deadline:
            return None
    value = (time.monotonic() - start) * 34300 / 2
    return round(value, 1) if 2 <= value <= 400 else None

def frames():
    while True:
        with camera_lock:
            ok, frame = camera.read()
        if ok:
            ok, encoded = cv2.imencode('.jpg', frame)
            if ok:
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + encoded.tobytes() + b'\r\n')
        time.sleep(0.04)

@app.get('/')
def index():
    return render_template_string(PAGE)

@app.get('/camera.mjpg')
def camera_stream():
    return Response(frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.get('/api/status')
def status():
    return jsonify({'camera': camera.isOpened(), 'distance_cm': sonar_distance(), 'gps': get_gps_location(timeout=0.2)})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    finally:
        camera.release()
        if GPIO:
            GPIO.cleanup()
