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

- Arduino Uno — main controller, receives serial signal from Python
- Breadboard — circuit assembly
- Piezo Buzzer — audio alert, pulsed at 2500 Hz
- LED (Red) — visual alert indicator
- Resistor (220Ω) — current limiting for LED
- Jumper Wires (x5) — electrical connections
- USB Cable — power and serial communication
- Logitech C270 Webcam — camera input
