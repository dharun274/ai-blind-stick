import time
import RPi.GPIO as GPIO

TRIG, ECHO = 23, 24
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.04)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)
    GPIO.output(TRIG, GPIO.LOW)
    deadline = time.monotonic() + 0.03
    while GPIO.input(ECHO) == 0:
        if time.monotonic() > deadline:
            return None
    start = time.monotonic()
    deadline = time.monotonic() + 0.03
    while GPIO.input(ECHO) == 1:
        if time.monotonic() > deadline:
            return None
    distance = (time.monotonic() - start) * 34300 / 2
    return distance if 2 <= distance <= 400 else None

try:
    print("HC-SR04 active. Press Ctrl+C to stop.")
    while True:
        value = get_distance()
        print(f"Distance: {value:.1f} cm" if value is not None else "No echo")
        time.sleep(0.1)
finally:
    GPIO.cleanup()
