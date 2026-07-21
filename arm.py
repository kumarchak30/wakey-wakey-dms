import cv2
import mediapipe as mp
import time
import serial

# --- Serial Setup ---
# Replace with your port from step 2
arduino = serial.Serial('/dev/cu.usbmodem2101', 9600, timeout=1)
time.sleep(2)  # wait for Arduino to reset after connection

# --- MediaPipe Setup ---
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

LEFT_EYE  = [33,  160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

CLOSED_TIME_THRESHOLD = 5.0

def eye_aspect_ratio(landmarks, eye_indices, img_w, img_h):
    pts = [(landmarks[i].x * img_w, landmarks[i].y * img_h) for i in eye_indices]
    v1 = abs(pts[1][1] - pts[5][1])
    v2 = abs(pts[2][1] - pts[4][1])
    h  = abs(pts[0][0] - pts[3][0])
    return (v1 + v2) / (2.0 * h) if h != 0 else 0

# --- Camera Setup ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

# --- Calibration ---
print("Calibrating... keep eyes open for 3 seconds")
left_samples  = []
right_samples = []
calib_start   = time.time()

while time.time() - calib_start < 3.0:
    ret, frame = cap.read()
    if not ret:
        continue

    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    remaining = 3.0 - (time.time() - calib_start)

    if results.multi_face_landmarks:
        lm = results.multi_face_landmarks[0].landmark
        left_ear  = eye_aspect_ratio(lm, LEFT_EYE,  w, h)
        right_ear = eye_aspect_ratio(lm, RIGHT_EYE, w, h)
        left_samples.append(left_ear)
        right_samples.append(right_ear)
        cv2.putText(frame, f"L-EAR: {left_ear:.2f}  R-EAR: {right_ear:.2f}", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    else:
        cv2.putText(frame, "No face detected - look at camera!", (30, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.putText(frame, f"Calibrating: {remaining:.1f}s - keep eyes open!", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.imshow("Driver Monitor", frame)
    cv2.waitKey(1)

if left_samples and right_samples:
    left_baseline  = sum(left_samples)  / len(left_samples)
    right_baseline = sum(right_samples) / len(right_samples)
    LEFT_EAR_THRESHOLD  = left_baseline  * 0.75
    RIGHT_EAR_THRESHOLD = right_baseline * 0.75
    AVG_EAR_THRESHOLD   = ((left_baseline + right_baseline) / 2.0) * 0.75
    print(f"Left  baseline: {left_baseline:.2f} | Threshold: {LEFT_EAR_THRESHOLD:.2f}")
    print(f"Right baseline: {right_baseline:.2f} | Threshold: {RIGHT_EAR_THRESHOLD:.2f}")
    print(f"Avg   threshold: {AVG_EAR_THRESHOLD:.2f}")
else:
    LEFT_EAR_THRESHOLD  = 0.20
    RIGHT_EAR_THRESHOLD = 0.22
    AVG_EAR_THRESHOLD   = 0.21
    print("Calibration failed - using default thresholds")

print("Calibration complete! Starting detection...")
time.sleep(1)

# --- Main Loop ---
eye_closed_start = None
alert_active     = False

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    h, w = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    eyes_closed = False

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:

            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
            )
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_LEFT_EYE,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )
            mp_drawing.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_RIGHT_EYE,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_contours_style()
            )

            lm = face_landmarks.landmark
            left_ear  = eye_aspect_ratio(lm, LEFT_EYE,  w, h)
            right_ear = eye_aspect_ratio(lm, RIGHT_EYE, w, h)
            avg_ear   = (left_ear + right_ear) / 2.0

            print(f"Left EAR: {left_ear:.2f} | Right EAR: {right_ear:.2f} | Avg: {avg_ear:.2f}")

            left_color  = (0, 0, 255) if left_ear  < LEFT_EAR_THRESHOLD  else (0, 255, 0)
            right_color = (0, 0, 255) if right_ear < RIGHT_EAR_THRESHOLD else (0, 255, 0)
            avg_color   = (0, 0, 255) if avg_ear   < AVG_EAR_THRESHOLD   else (0, 255, 0)

            eyes_closed = avg_ear < AVG_EAR_THRESHOLD

            cv2.putText(frame, f"L-EAR: {left_ear:.2f}",  (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, left_color,  2)
            cv2.putText(frame, f"R-EAR: {right_ear:.2f}", (30, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, right_color, 2)
            cv2.putText(frame, f"AVG:   {avg_ear:.2f}",   (30, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, avg_color,   2)

            status = "CLOSED" if eyes_closed else "OPEN"
            cv2.putText(frame, f"Eyes: {status}", (30, 170),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, avg_color, 2)

    else:
        cv2.putText(frame, "No face detected", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2)

    # --- Drowsiness Timer + Arduino Signal ---
    if eyes_closed:
        if eye_closed_start is None:
            eye_closed_start = time.time()
        elapsed = time.time() - eye_closed_start

        cv2.putText(frame, f"Closed for: {elapsed:.1f}s", (30, 210),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        if elapsed >= CLOSED_TIME_THRESHOLD:
            if not alert_active:
                arduino.write(b'1')  # trigger buzzer + LED
                alert_active = True
                print("ALERT SENT TO ARDUINO")
            cv2.putText(frame, "DROWSINESS ALERT!", (30, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    else:
        if alert_active:
            arduino.write(b'0')  # turn off buzzer + LED
            print("ALERT CLEARED")
        eye_closed_start = None
        alert_active     = False

    cv2.imshow("Driver Monitor", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
arduino.write(b'0')
arduino.close()
cap.release()
cv2.destroyAllWindows()

#Team 2