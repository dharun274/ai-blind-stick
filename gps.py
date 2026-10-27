import serial
import pynmea2

SERIAL_PORT = "/dev/serial0"
BAUD_RATE = 9600
FALLBACK = {"latitude": 11.0168, "longitude": 76.9558, "location": "Coimbatore (fallback)"}

def get_gps_location(timeout=2.0):
    """Return a GPS fix when available, otherwise return the configured fallback."""
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=timeout) as port:
            for _ in range(3):
                line = port.readline().decode("ascii", errors="ignore").strip()
                if line.startswith(("$GPGGA", "$GNGGA")):
                    msg = pynmea2.parse(line)
                    if int(msg.gps_qual or 0) > 0:
                        return {"latitude": msg.latitude, "longitude": msg.longitude, "location": "GPS fix"}
    except (OSError, serial.SerialException, pynmea2.ParseError, ValueError):
        pass
    return FALLBACK.copy()

if __name__ == "__main__":
    print(get_gps_location())
