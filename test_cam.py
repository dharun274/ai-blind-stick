import cv2
import os

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
if not cap.isOpened():
    raise SystemExit("USB camera could not be opened")
if not os.environ.get("DISPLAY"):
    print("USB camera opened in headless mode. Press Ctrl+C to stop.")
    try:
        frame_number = 0
        while True:
            ok, frame = cap.read()
            if not ok:
                raise SystemExit("Camera opened but frame capture failed")
            frame_number += 1
            if frame_number % 30 == 0:
                print(f"Captured {frame_number} frames: {frame.shape[1]}x{frame.shape[0]}")
    finally:
        cap.release()
    raise SystemExit(0)

print("USB camera opened. Press q in the preview window to stop.")
try:
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        cv2.imshow("AI Blind Stick camera", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
finally:
    cap.release()
    cv2.destroyAllWindows()
