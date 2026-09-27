import cv2
import mediapipe as mp
import serial
import time
import math


# ============================================================
# CONFIGURATION
# ============================================================

# Change this to your Arduino port.
# Windows example:
# COM3
#
# Linux example:
# /dev/ttyUSB0
#
# macOS example:
# /dev/cu.usbmodemXXXX

ARDUINO_PORT = "COM10"

BAUD_RATE = 9600

CAMERA_INDEX = 0


# ============================================================
# CONNECT TO ARDUINO
# ============================================================

try:
    arduino = serial.Serial(
        ARDUINO_PORT,
        BAUD_RATE,
        timeout=1
    )

    # Give Arduino time to reset after opening serial.
    time.sleep(2)

    print("Arduino connected.")

except serial.SerialException as error:
    print("Could not connect to Arduino.")
    print(error)
    print()
    print("Check ARDUINO_PORT in main.py.")
    print("Example: COM3")
    print("Example: /dev/ttyUSB0")

    arduino = None


# ============================================================
# MEDIAPIPE SETUP
# ============================================================

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="models/hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def distance(point1, point2):
    """
    Calculate the 2D distance between two hand landmarks.
    """

    dx = point1.x - point2.x
    dy = point1.y - point2.y

    return math.sqrt(dx * dx + dy * dy)


def is_finger_extended(landmarks, tip, pip, mcp, wrist):
    """
    Determine whether a finger is extended.

    We compare the distance from the fingertip to the wrist
    with the distance from the PIP joint to the wrist.

    If the fingertip is significantly farther from the wrist,
    the finger is probably extended.
    """

    tip_distance = distance(landmarks[tip], landmarks[wrist])
    pip_distance = distance(landmarks[pip], landmarks[wrist])

    return tip_distance > pip_distance * 1.15


def detect_fingers(landmarks, handedness):
    """
    Detect the state of the five fingers.

    Returns:

        [thumb, index, middle, ring, pinky]

    where:

        1 = finger open
        0 = finger closed
    """

    wrist = 0

    # --------------------------------------------------------
    # Index
    # --------------------------------------------------------

    index_open = is_finger_extended(
        landmarks,
        tip=8,
        pip=6,
        mcp=5,
        wrist=wrist
    )

    # --------------------------------------------------------
    # Middle
    # --------------------------------------------------------

    middle_open = is_finger_extended(
        landmarks,
        tip=12,
        pip=10,
        mcp=9,
        wrist=wrist
    )

    # --------------------------------------------------------
    # Ring
    # --------------------------------------------------------

    ring_open = is_finger_extended(
        landmarks,
        tip=16,
        pip=14,
        mcp=13,
        wrist=wrist
    )

    # --------------------------------------------------------
    # Pinky
    # --------------------------------------------------------

    pinky_open = is_finger_extended(
        landmarks,
        tip=20,
        pip=18,
        mcp=17,
        wrist=wrist
    )

    # --------------------------------------------------------
    # Thumb
    # --------------------------------------------------------

    # For the thumb we use the horizontal position.
    #
    # MediaPipe returns handedness, so we can account for
    # whether the detected hand is left or right.

    thumb_tip = landmarks[4]
    thumb_ip = landmarks[3]

    if handedness == "Right":
        thumb_open = thumb_tip.x < thumb_ip.x
    else:
        thumb_open = thumb_tip.x > thumb_ip.x

    return [
        int(thumb_open),
        int(index_open),
        int(middle_open),
        int(ring_open),
        int(pinky_open)
    ]


def make_command(fingers):
    """
    Convert:

        [1, 1, 0, 1, 0]

    into:

        "11010"
    """

    return "".join(str(value) for value in fingers)


def send_to_arduino(command):
    """
    Send the five-bit command to Arduino.
    """

    if arduino is None:
        return

    message = command + "\n"

    arduino.write(message.encode())


def draw_landmarks(frame, landmarks):
    """
    Draw the 21 MediaPipe hand landmarks.
    """

    height, width, _ = frame.shape

    points = []

    for landmark in landmarks:

        x = int(landmark.x * width)
        y = int(landmark.y * height)

        points.append((x, y))

        cv2.circle(
            frame,
            (x, y),
            5,
            (0, 255, 0),
            -1
        )

    # Draw connections between landmarks.

    connections = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 4),

        (0, 5),
        (5, 6),
        (6, 7),
        (7, 8),

        (5, 9),
        (9, 10),
        (10, 11),
        (11, 12),

        (9, 13),
        (13, 14),
        (14, 15),
        (15, 16),

        (13, 17),
        (17, 18),
        (18, 19),
        (19, 20),

        (0, 17)
    ]

    for start, end in connections:

        cv2.line(
            frame,
            points[start],
            points[end],
            (255, 255, 255),
            2
        )


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(CAMERA_INDEX)

if not camera.isOpened():

    print("ERROR: Could not open camera.")

    if arduino:
        arduino.close()

    exit()


# ============================================================
# MAIN PROGRAM
# ============================================================

previous_command = ""

start_time = time.time()

with HandLandmarker.create_from_options(options) as landmarker:

    while True:

        success, frame = camera.read()

        if not success:
            print("Could not read camera frame.")
            break

        # Flip image horizontally so it behaves like a mirror.

        frame = cv2.flip(frame, 1)

        # Convert BGR → RGB.

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        # Create MediaPipe image.

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # MediaPipe video timestamp.

        timestamp_ms = int(
            (time.time() - start_time) * 1000
        )

        # Detect hand.

        result = landmarker.detect_for_video(
            mp_image,
            timestamp_ms
        )

        command = "00000"
        fingers = [0, 0, 0, 0, 0]

        # ----------------------------------------------------
        # HAND DETECTED
        # ----------------------------------------------------

        if result.hand_landmarks:

            landmarks = result.hand_landmarks[0]

            # Determine left/right hand.

            handedness = "Right"

            if result.handedness:

                handedness = (
                    result.handedness[0][0].category_name
                )

            # Detect individual fingers.

            fingers = detect_fingers(
                landmarks,
                handedness
            )

            # Convert to 5-bit command.

            command = make_command(fingers)

            # Draw hand.

            draw_landmarks(
                frame,
                landmarks
            )

        # ----------------------------------------------------
        # SEND ONLY WHEN COMMAND CHANGES
        # ----------------------------------------------------

        if command != previous_command:

            send_to_arduino(command)

            previous_command = command

            print(
                "Finger state:",
                fingers,
                "Command:",
                command
            )

        # ----------------------------------------------------
        # DISPLAY INFORMATION
        # ----------------------------------------------------

        cv2.putText(
            frame,
            "Finger state: " + command,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

        finger_count = sum(fingers)

        cv2.putText(
            frame,
            "Fingers open: " + str(finger_count),
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Press Q to quit",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Show camera.

        cv2.imshow(
            "Hand Controlled LEDs",
            frame
        )

        # Quit.

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

if arduino:
    # Turn all LEDs off before exiting.
    send_to_arduino("00000")
    time.sleep(0.1)

    arduino.close()

print("Program stopped.")