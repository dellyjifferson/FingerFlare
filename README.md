# Hand-Controlled LEDs

A beginner-friendly **computer vision + Arduino robotics project** where
a webcam detects the position of the five fingers on a hand and controls
five physical LEDs connected to an Arduino Uno.

The project demonstrates a complete hardware/software pipeline:

``` text
Hand
  ↓
Webcam
  ↓
Python + OpenCV
  ↓
MediaPipe Hand Landmarker
  ↓
Finger-state detection
  ↓
Serial communication over USB
  ↓
Arduino Uno
  ↓
5 LEDs
```

## Project Demo

The goal is simple:

-   Open a finger → its corresponding LED turns **ON**
-   Close a finger → its corresponding LED turns **OFF**
-   Open the whole hand → all five LEDs turn **ON**
-   Close the whole hand → all five LEDs turn **OFF**

For example:

``` text
Hand state: 11111
LEDs:       ● ● ● ● ●
```

and:

``` text
Hand state: 10101
LEDs:       ● ○ ● ○ ●
```

------------------------------------------------------------------------

## Features

-   Real-time hand detection using a webcam
-   Five individual finger states
-   MediaPipe hand landmark detection
-   OpenCV camera processing
-   Arduino control through USB serial communication
-   Five independently controlled LEDs
-   Simple binary command protocol
-   Beginner-friendly hardware
-   Suitable for robotics and STEM workshops

------------------------------------------------------------------------

## Hardware Required

### Electronics

  Component                  Quantity
  ------------------------ ----------
  Arduino Uno                       1
  LEDs                              5
  220 Ω--330 Ω resistors            5
  Breadboard                        1
  Jumper wires                Several
  USB cable                         1

### Computer

-   Laptop or desktop computer
-   Webcam
-   Python 3
-   Arduino IDE

No Raspberry Pi or additional microcontroller is required.

------------------------------------------------------------------------

## Circuit

Each LED is connected to one Arduino digital pin through a resistor.

  Finger     Arduino Pin LED
  -------- ------------- -------
  Thumb               D2 LED 1
  Index               D3 LED 2
  Middle              D4 LED 3
  Ring                D5 LED 4
  Pinky               D6 LED 5

Basic connection:

``` text
Arduino pin ─── 220Ω/330Ω resistor ─── LED ─── GND
```

The LED's longer leg (anode) goes toward the resistor/Arduino output,
while the shorter leg (cathode) goes toward GND.

> **Important:** Never connect an LED directly to an Arduino digital pin
> without a current-limiting resistor.

------------------------------------------------------------------------

## Software Requirements

The project uses:

-   **Python 3**
-   **OpenCV** --- camera and image processing
-   **MediaPipe** --- hand landmark detection
-   **PySerial** --- communication between Python and Arduino
-   **Arduino IDE** --- programming the Arduino

------------------------------------------------------------------------

## Project Structure

Recommended repository structure:

``` text
hand-controlled-leds/
│
├── README.md
│
├── arduino/
│   └── hand_led_controller/
│       └── hand_led_controller.ino
│
├── python/
│   ├── main.py
│   ├── serial_test.py
│   ├── camera_test.py
│   ├── requirements.txt
│   │
│   └── models/
│       └── hand_landmarker.task
│
└── docs/
    ├── wiring.png
    └── project-diagram.png
```

The exact filenames can be changed, but keeping Arduino and Python code
separated makes the project easier to understand and maintain.

------------------------------------------------------------------------

# Installation

## 1. Install Arduino IDE

Install the Arduino IDE on your computer.

Open Arduino IDE and connect the Arduino Uno through USB.

Select:

``` text
Tools → Board → Arduino Uno
```

Then select the correct serial port:

``` text
Tools → Port → COM10
```

The port number may be different on another computer.

Examples:

``` text
COM3
COM10
COM15
```

On Linux, the Arduino may appear as:

``` text
/dev/ttyUSB0
```

or:

``` text
/dev/ttyACM0
```

------------------------------------------------------------------------

## 2. Upload the Arduino Code

The Arduino receives a five-character command:

``` text
11111
```

Each character controls one LED.

``` text
1 = ON
0 = OFF
```

The first character controls LED 1, the second controls LED 2, and so
on.

Example:

``` text
10101
```

means:

``` text
LED 1 → ON
LED 2 → OFF
LED 3 → ON
LED 4 → OFF
LED 5 → ON
```

Use the following Arduino sketch:

``` cpp
const int ledPins[] = {2, 3, 4, 5, 6};

const int NUMBER_OF_LEDS = 5;

char buffer[6];
int index = 0;

void setup() {

  Serial.begin(9600);

  for (int i = 0; i < NUMBER_OF_LEDS; i++) {

    pinMode(ledPins[i], OUTPUT);

    digitalWrite(ledPins[i], LOW);
  }

  Serial.println("Arduino ready");
}

void loop() {

  while (Serial.available() > 0) {

    char incoming = Serial.read();

    if (incoming == '\n' || incoming == '\r') {

      if (index == 5) {

        buffer[5] = '\0';

        for (int i = 0; i < NUMBER_OF_LEDS; i++) {

          if (buffer[i] == '1') {

            digitalWrite(
              ledPins[i],
              HIGH
            );

          } else if (buffer[i] == '0') {

            digitalWrite(
              ledPins[i],
              LOW
            );
          }
        }

        Serial.print("Received: ");
        Serial.println(buffer);
      }

      index = 0;
    }

    else {

      if (index < 5) {

        if (incoming == '0' || incoming == '1') {

          buffer[index] = incoming;

          index++;
        }
      }
    }
  }
}
```

Upload the sketch to the Arduino.

------------------------------------------------------------------------

# 3. Test the Arduino

Before using Python, test the electronics independently.

Open:

``` text
Tools → Serial Monitor
```

Set the baud rate to:

``` text
9600
```

Set the line ending to:

``` text
Newline
```

Send:

``` text
11111
```

All five LEDs should turn on.

Then send:

``` text
00000
```

All five LEDs should turn off.

Try:

``` text
10101
```

The LEDs should behave like:

``` text
ON  OFF  ON  OFF  ON
```

If this test does not work, troubleshoot the Arduino circuit before
continuing.

------------------------------------------------------------------------

# Python Setup

## 1. Create a virtual environment

From the `python` directory:

### Windows

``` powershell
python -m venv .venv
```

Activate it:

``` powershell
.venv\Scripts\activate
```

### Linux/macOS

``` bash
python3 -m venv .venv
```

Activate it:

``` bash
source .venv/bin/activate
```

------------------------------------------------------------------------

## 2. Install Python Dependencies

Create `requirements.txt`:

``` text
opencv-python
mediapipe
pyserial
```

Then install everything:

``` bash
pip install -r requirements.txt
```

Or install directly:

``` bash
pip install opencv-python mediapipe pyserial
```

------------------------------------------------------------------------

# MediaPipe Hand Model

The Hand Landmarker requires a MediaPipe hand model file.

Download the official **Hand Landmarker** model and place it at:

``` text
python/models/hand_landmarker.task
```

The final structure should look like:

``` text
python/
├── main.py
├── requirements.txt
└── models/
    └── hand_landmarker.task
```

------------------------------------------------------------------------

# Camera Test

Before running the complete application, test the webcam.

Create `camera_test.py`:

``` python
import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open camera.")
    exit()

print("Camera started.")
print("Press Q to quit.")

while True:

    success, frame = camera.read()

    if not success:
        print("ERROR: Could not read frame.")
        break

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()
```

Run:

``` bash
python camera_test.py
```

If the camera does not open, try changing:

``` python
cv2.VideoCapture(0)
```

to:

``` python
cv2.VideoCapture(1)
```

------------------------------------------------------------------------

# Serial Communication Test

Before combining computer vision and Arduino control, test Python →
Arduino separately.

Create `serial_test.py`:

``` python
import serial
import time

PORT = "COM10"
BAUD_RATE = 9600

print("Opening Arduino...")

arduino = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=1
)

time.sleep(2)

print("Arduino connected!")
print("Sending commands...")
print()

commands = [
    "11111",
    "00000",
    "10101",
    "01010",
    "11111",
    "00000"
]

for command in commands:

    print("Sending:", command)

    arduino.write((command + "\n").encode())

    time.sleep(2)

arduino.close()

print("Test finished.")
```

Change:

``` python
PORT = "COM10"
```

to the Arduino port on your computer.

Run:

``` bash
python serial_test.py
```

The LEDs should respond to each command.

> **Important:** Close the Arduino Serial Monitor before running Python.
> A serial port normally cannot be used by both the Serial Monitor and
> Python at the same time.

------------------------------------------------------------------------

# Running the Complete Project

Make sure:

1.  Arduino is connected.
2.  Correct Arduino code has been uploaded.
3.  Arduino Serial Monitor is closed.
4.  Webcam is connected.
5.  `hand_landmarker.task` exists.
6.  Python virtual environment is activated.
7.  `main.py` contains the correct Arduino port.

At the top of `main.py`:

``` python
ARDUINO_PORT = "COM10"
```

Then run:

``` bash
python main.py
```

A camera window should appear.

Place your hand in front of the camera.

The program should display something similar to:

``` text
Finger state: 11111
Fingers open: 5
```

and the five LEDs should turn on.

Close your fingers and the corresponding LEDs should turn off.

Press:

``` text
Q
```

to stop the program.

------------------------------------------------------------------------

# How It Works

## 1. Webcam

OpenCV captures frames from the webcam.

``` text
Webcam
   ↓
Video frame
```

## 2. MediaPipe

MediaPipe detects the hand and provides 21 landmarks.

``` text
Hand
 ↓
21 landmarks
```

These landmarks describe important points such as:

-   Wrist
-   Finger joints
-   Fingertips

## 3. Finger Detection

The Python program analyzes the landmarks and determines whether each
finger is open or closed.

The result is represented by five binary values:

``` text
[Thumb, Index, Middle, Ring, Pinky]
```

For example:

``` text
[1, 1, 1, 1, 1]
```

becomes:

``` text
11111
```

while:

``` text
[1, 0, 1, 0, 1]
```

becomes:

``` text
10101
```

## 4. Serial Communication

Python sends the command to the Arduino through USB:

``` text
Python
  ↓
USB
  ↓
COM10
  ↓
Arduino
```

The command contains five characters followed by a newline:

``` text
11111\n
```

## 5. Arduino

The Arduino reads the command and controls the five digital pins.

``` text
Command: 10101

D2 → HIGH
D3 → LOW
D4 → HIGH
D5 → LOW
D6 → HIGH
```

Result:

``` text
● ○ ● ○ ●
```

------------------------------------------------------------------------

# Command Protocol

The project uses a very simple protocol.

``` text
Position 1 → Thumb
Position 2 → Index
Position 3 → Middle
Position 4 → Ring
Position 5 → Pinky
```

Each position contains:

``` text
1 = ON
0 = OFF
```

Examples:

  Command   Thumb   Index   Middle   Ring   Pinky
  --------- ------- ------- -------- ------ -------
  `00000`   OFF     OFF     OFF      OFF    OFF
  `10000`   ON      OFF     OFF      OFF    OFF
  `01000`   OFF     ON      OFF      OFF    OFF
  `00100`   OFF     OFF     ON       OFF    OFF
  `00010`   OFF     OFF     OFF      ON     OFF
  `00001`   OFF     OFF     OFF      OFF    ON
  `11111`   ON      ON      ON       ON     ON
  `10101`   ON      OFF     ON       OFF    ON

------------------------------------------------------------------------

# Troubleshooting

## Python cannot connect to COM10

Check:

``` text
Arduino IDE
→ Tools
→ Port
```

Confirm that the Arduino is actually on `COM10`.

Then update:

``` python
ARDUINO_PORT = "COM10"
```

Also make sure the Arduino Serial Monitor is closed.

------------------------------------------------------------------------

## LEDs work in Serial Monitor but not Python

Run:

``` bash
python serial_test.py
```

If this works, the serial connection is correct and the issue is in the
main computer-vision program.

------------------------------------------------------------------------

## Camera works but LEDs don't react

Check the terminal output.

You should see:

``` text
Finger state: [1, 1, 1, 1, 1]
Sending to Arduino: 11111
```

If the finger state changes but the LEDs do not, investigate the serial
connection.

------------------------------------------------------------------------

## MediaPipe cannot find the model

Make sure this file exists:

``` text
models/hand_landmarker.task
```

and that the path in Python matches:

``` python
model_asset_path="models/hand_landmarker.task"
```

------------------------------------------------------------------------

## Hand detection is unstable

For the initial version:

-   Face the palm toward the camera.
-   Keep the wrist visible.
-   Use good lighting.
-   Keep fingers separated.
-   Keep the hand reasonably close to the camera.
-   Avoid placing the hand directly against a visually complex
    background.

The finger-classification algorithm can later be improved using landmark
angles and additional geometric checks.

------------------------------------------------------------------------

# Learning Objectives

This project introduces several important STEM and programming concepts.

### Electronics

-   Digital outputs
-   LEDs
-   Resistors
-   Breadboards
-   Ground
-   GPIO pins

### Programming

-   Python
-   C/C++
-   Functions
-   Lists
-   Conditions
-   Loops
-   State changes
-   Serial protocols

### Computer Vision

-   Webcam image capture
-   Hand detection
-   Landmark detection
-   Geometric analysis
-   Real-time processing

### Robotics

-   Microcontroller programming
-   Computer-to-microcontroller communication
-   Physical outputs
-   Hardware/software integration

------------------------------------------------------------------------

# Future Improvements

The project can be expanded considerably.

## Gesture Control

Add special gestures:

``` text
✊ → All LEDs OFF
🖐️ → All LEDs ON
☝️ → Special mode
✌️ → Mode 2
🤟 → Mode 3
```

## Servo Motor

Add a servo:

``` text
Open hand → Servo opens
Closed hand → Servo closes
```

## RGB LEDs

Replace the five normal LEDs with RGB LEDs and use gestures to control
colors.

## Buzzer

Add sound feedback when a gesture is detected.

## Robot Control

The same system can eventually control:

-   Motors
-   Servos
-   Robotic arms
-   Smart home devices
-   Small robots

The architecture becomes:

``` text
Hand
 ↓
Computer Vision
 ↓
Gesture Recognition
 ↓
Arduino
 ↓
Motors / Servos / LEDs / Sensors
```

------------------------------------------------------------------------

# Educational Project

This project is particularly suitable for a beginner robotics workshop
because participants can see the entire path from a physical human
action to a computer decision and finally to a physical electronic
response.

The project can be presented as:

> **"Controlling physical electronics using computer vision and hand
> gestures."**

It combines:

**Artificial Intelligence + Computer Vision + Programming +
Electronics + Robotics**

------------------------------------------------------------------------

# Credits

Built as a hands-on educational project combining:

-   Arduino
-   Python
-   OpenCV
-   MediaPipe
-   Computer Vision
-   Electronics
-   Robotics
