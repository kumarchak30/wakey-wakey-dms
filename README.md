# wakey-wakey-dms

A real-time driver drowsiness detection system built with Python and Arduino. 
Uses computer vision to track eye closure and triggers an audio/visual alert 
when the driver's eyes remain closed for 5 or more seconds.

## Demo

https://youtube.com/shorts/7IOHP7hZXlQ?feature=share 

## How It Works

A webcam continuously monitors the driver's face using MediaPipe Face Mesh, 
mapping 468 facial landmarks in real time. The system computes an 
**Eye Aspect Ratio (EAR)** — a ratio of the eye's height to width — for both 
eyes on every frame. When the EAR drops below a personalized threshold and 
stays there for 5 seconds, Python sends a signal over USB serial to an Arduino 
Uno, which triggers a pulsed piezo buzzer and an LED. When the driver's eyes 
reopen, all alerts stop automatically.

## Tech Stack

- **Python** — core detection and serial communication logic
- **MediaPipe Face Mesh** — real-time 468-point facial landmark detection
- **OpenCV** — webcam feed and frame rendering
- **PySerial** — serial communication between Python and Arduino
- **Arduino (C++)** — hardware alert control (buzzer + LED)

## Hardware Components

- **Arduino Uno** — main controller, receives serial signal from Python
- **Breadboard** — circuit assembly
- **Piezo Buzzer** — audio alert, pulsed at 2500 Hz
- **LED** — visual alert indicator
- **Resistor (220Ω)** — current limiting for LED
- **Jumper Wires (x5)** — electrical connections
- **USB Cable** — power and serial communication
- **Logitech C270 Webcam** — camera input

## Wiring
- Arduino Pin 13 → 220Ω resistor → LED (+) → LED (-) → GND
- Arduino Pin 8  → Buzzer (+)
- GND            → Buzzer (-)

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/kumarchak30/wakey-wakey.git
cd wakey-wakey
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv drowsy_env
source drowsy_env/bin/activate   # Mac/Linux
drowsy_env\Scripts\activate      # Windows
```

### 3. Install dependencies
```bash
pip install mediapipe==0.10.5 opencv-python pyserial
```

### 4. Upload the Arduino sketch
- Open `/arduino/wakey_wakey.ino` in Arduino IDE
- Upload to your Arduino Uno

### 5. Find your Arduino's port
```bash
ls /dev/cu.*        # Mac
python -m serial.tools.list_ports  # Windows
```

### 6. Update the port in `arm.py`
```python
arduino = serial.Serial('/dev/cu.usbmodem2102', 9600, timeout=1)
```

### 7. Run the system
```bash
python arm.py
```

Keep your eyes open during the **3 second calibration window**, then detection starts.

---

## Known Limitations

- Struggles in low-light or nighttime conditions
- Requires a stable mounting position — vibration affects detection accuracy
- Currently laptop-dependent (no standalone embedded solution)
- Adhesive mounting may weaken in high vehicle interior temperatures

---

## Future Improvements

- Infrared camera support for nighttime detection
- More secure suction or clip-based mounting system
- Compact standalone hardware (Raspberry Pi)
- Head pose detection as an additional distraction signal

---

## Team

Built for EGN2020C — Introduction to Engineering, Spring 2026 at the University of Florida.

**Kumar Chakraborty, Randy Hin, Braden Ross, Rachel Morris, Boaz St. Omer**

Professor Sarah Jayasekaran

---

## License

MIT

