# ESP32 Smart Lock Integration Guide

## Overview
The face recognition system (`recognize.py`) now integrates with the ESP32 smart lock controller to:
- **Unlock door** when a recognized resident is detected
- **Lock door** when an intruder is detected
- Display alerts on the LCD (16x2 character display)
- Control a servo motor lock

## Hardware Setup

### ESP32 Connections
```
ESP32 Pin Layout:
- GPIO 18: Servo signal (PWM)
- GPIO 4:  LCD RS (Register Select)
- GPIO 5:  LCD EN (Enable)
- GPIO 6:  LCD D4
- GPIO 7:  LCD D5
- GPIO 8:  LCD D6
- GPIO 9:  LCD D7
- GND:     Ground (common with servo/LCD)
- 5V:      Power (servo + LCD)
```

### Servo Motor Wiring
```
Servo Signal → GPIO 18
Servo Power  → 5V
Servo Ground → GND
```

### LCD Display (16x2)
```
RS → GPIO 4
EN → GPIO 5
D4 → GPIO 6
D5 → GPIO 7
D6 → GPIO 8
D7 → GPIO 9
VSS → GND
VDD → 5V
VO → GND (contrast)
```

## ESP32 Firmware
Upload the provided Arduino sketch to your ESP32:

```c
#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h>
#include <LiquidCrystal.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
// ... (rest of code provided by user)
```

**Find your ESP32 IP address:**
```bash
# Check the serial monitor after uploading
# Should print: "ESP32 IP: 192.168.x.x"
```

## Python Configuration

### 1. Find Your ESP32 IP
After uploading firmware to ESP32, check the serial monitor:
```
ESP32 IP: 192.168.1.100
```

### 2. Set Environment Variables

**Option A: Inline (one-time)**
```bash
export ESP32_IP="192.168.1.100"
export ESP32_ENABLED="true"
python image_authenticate/recognize.py
```

**Option B: .env file (permanent)**
Create `.env` in `/home/srj/cryptiq`:
```
ESP32_IP=192.168.1.100
ESP32_ENABLED=true
```

Then run:
```bash
cd /home/srj/cryptiq && source venv/bin/activate
python image_authenticate/recognize.py
```

**Option C: Modify code directly**
Edit `image_authenticate/recognize.py` line 43-45:
```python
ESP32_IP = "192.168.1.100"       # Your ESP32 IP
ESP32_PORT = 80
ESP32_ENABLED = True              # Set to True to enable
```

## API Endpoints (ESP32)

### `/vision?status=<status>`
Send face detection results:
```bash
# Recognized resident (unlock door)
curl "http://192.168.1.100/vision?status=recognize"

# Intruder detected (lock door)
curl "http://192.168.1.100/vision?status=intruder"
```

### `/unlock`
Manually unlock door:
```bash
curl "http://192.168.1.100/unlock"
```

### `/lock`
Manually lock door:
```bash
curl "http://192.168.1.100/lock"
```

### `/state`
Check current lock state:
```bash
curl "http://192.168.1.100/state" | python -m json.tool
```

### `/ping`
Health check:
```bash
curl "http://192.168.1.100/ping" | python -m json.tool
```

## Running the Integration

### Start the face recognition with ESP32 enabled:
```bash
cd /home/srj/cryptiq
source venv/bin/activate
export ESP32_IP="192.168.1.100"
export ESP32_ENABLED="true"
python image_authenticate/recognize.py
```

### Expected Output:
```
[recognize] Loading InsightFace model...
[recognize] Model loaded.
[recognize] Loaded 1 enrolled resident(s):
  - snehanshu

[ESP32] Smart Lock ENABLED
        IP: 192.168.1.100:80
        • Recognized → /vision?status=recognize (unlock)
        • Intruder   → /vision?status=intruder (lock)

[recognize] Opening camera (index 0)...
[recognize] Camera opened. Press 'q' to quit.
```

### Detection Log Example:
```json
# Recognized resident detected
{"status": "recognized", "name": "snehanshu", "similarity": 0.75}
[ESP32] RECOGNIZE notification sent
[ESP32] Person: snehanshu

# Intruder detected
{"status": "unknown", "similarity": 0.25, "frame_saved": "intruder_frames/intruder_2026-04-18_08-56-29_frame1.jpg"}
[ESP32] INTRUDER notification sent
```

## LCD Display Messages

Based on ESP32 firmware, LCD shows:

| Event | Line 1 | Line 2 |
|-------|--------|--------|
| Boot | "Booting..." | "Connecting WiFi" |
| WiFi Connected | "WiFi connected" | "192.168.1.100" |
| Recognized | "Recognized" | "Access allowed" |
| Intruder | "INTRUDER ALERT" | "Access denied" |
| Door Unlocked | "Door unlocked" | "Access granted" |
| Door Locked | "Door locked" | "Secure" |

## Servo Motor Behavior

### Recognized Resident:
```
1. Servo rotates to 90° (UNLOCKED_ANGLE) - door opens
2. Holds for 1 second
3. Returns to 0° (LOCKED_ANGLE) - door locks
4. This allows person to enter
```

### Intruder:
```
1. Servo stays at 0° (LOCKED_ANGLE) - door remains locked
2. LCD displays alert
3. Frame saved to `intruder_frames/`
```

## Troubleshooting

### Connection Error: Cannot connect to ESP32
- **Check ESP32 IP**: Print it from serial monitor
- **Check WiFi**: Ensure both ESP32 and laptop on same network
- **Check Firewall**: May need to allow port 80
- **Restart ESP32**: Press reset button

### ESP32 Won't Connect to WiFi
- Edit ESP32 code: `ssid` and `password`
- Upload again
- Check WiFi credentials

### Servo Not Moving
- Check GPIO 18 connection
- Verify servo power (5V) and ground
- Check servo signal is 50Hz PWM

### LCD Not Displaying
- Check all GPIO pins (4-9)
- Verify power (5V) and ground
- Adjust contrast (VO pin)

### Face Recognition Not Triggering ESP32
- Verify `ESP32_ENABLED="true"`
- Check ESP32_IP is correct
- Add debug: `print(f"[ESP32] Sending to {ESP32_IP}")` in code

## Testing Workflow

1. **Start recognition:**
   ```bash
   export ESP32_IP="192.168.1.100"
   export ESP32_ENABLED="true"
   python image_authenticate/recognize.py
   ```

2. **Show recognized face to camera:**
   - Should see: `{"status": "recognized", ...}`
   - Should see: `[ESP32] RECOGNIZE notification sent`
   - Servo should rotate then return to locked position
   - LCD should show "Recognized"

3. **Show unknown face to camera:**
   - Should see: `{"status": "unknown", ...}`
   - Should see: `[ESP32] INTRUDER notification sent`
   - Servo stays locked
   - LCD should show "INTRUDER ALERT"
   - Frame saved to `intruder_frames/`

## Security Notes

- **WiFi Security**: Use WPA2/WPA3 (provided code uses credentials in plaintext - add encryption in production)
- **API Authentication**: ESP32 API currently has no auth - add token validation in production
- **Network Access**: Keep ESP32 on private network, don't expose to internet without auth
- **Face Recognition Threshold**: Current threshold is 0.4 - adjust if getting false positives/negatives

## Production Checklist

- [ ] ESP32 running on stable power (not USB)
- [ ] Face recognition database updated with all residents
- [ ] THRESHOLD tuned for your environment (0.3-0.5)
- [ ] Servo motor tested with full range (0-90°)
- [ ] LCD contrast adjusted for visibility
- [ ] ngrok tunnel for remote access (if needed)
- [ ] Door mechanism properly calibrated
- [ ] Network isolated from untrusted devices
- [ ] Error logs monitored
