# combined_control.py (Optimized for Low Frame Drop + Async Commands + Voice Control)

import cv2
import mediapipe as mp
import time
import threading
import queue
import speech_recognition as sr
from utils.send_command import send_to_esp

mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 30)

# Finger tip landmarks
TIP_IDS = [4, 8, 12, 16, 20]

# Thread-safe queue for commands
command_queue = queue.Queue()
last_command = ""

# Background thread to send commands
def command_sender():
    while True:
        command = command_queue.get()
        if command == "__exit__":
            break
        send_to_esp(command)

threading.Thread(target=command_sender, daemon=True).start()

# Background thread for voice recognition
def voice_listener():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙️ Voice control ready. Say a command.")
        while True:
            try:
                audio = recognizer.listen(source, timeout=5)
                voice_text = recognizer.recognize_google(audio).lower()
                print(f"🔊 Heard: {voice_text}")
                if "forward" in voice_text:
                    command_queue.put("forward")
                elif "back" in voice_text:
                    command_queue.put("back")
                elif "left" in voice_text:
                    command_queue.put("left")
                elif "right" in voice_text:
                    command_queue.put("right")
                elif "stop" in voice_text:
                    command_queue.put("stop")
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                print("❌ Could not understand.")
            except sr.RequestError:
                print("⚠️ Could not request results.")

threading.Thread(target=voice_listener, daemon=True).start()

def get_fingers_status(hand_landmarks):
    fingers = []
    # Thumb
    fingers.append(1 if hand_landmarks.landmark[TIP_IDS[0]].x < hand_landmarks.landmark[TIP_IDS[0] - 1].x else 0)
    # Other 4 fingers
    for i in range(1, 5):
        fingers.append(1 if hand_landmarks.landmark[TIP_IDS[i]].y < hand_landmarks.landmark[TIP_IDS[i] - 2].y else 0)
    return fingers

prev_time = 0

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
) as hands:
    while True:
        success, image = cap.read()
        if not success:
            continue

        image = cv2.flip(image, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)

        gesture = ""
        command = ""

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            fingers = get_fingers_status(hand)

            # Use exact gesture mapping per user specification
            if fingers == [1, 1, 1, 1, 1]:
                command = "forward"; gesture = "FORWARD 🚗"
            elif fingers == [0, 1, 1, 0, 0]:
                command = "back"; gesture = "BACK 🔙"
            elif fingers == [1, 0, 0, 0, 0]:
                command = "left"; gesture = "LEFT ↩️"
            elif fingers == [1, 1, 0, 0, 0]:
                command = "right"; gesture = "RIGHT ↪️"
            elif fingers == [0, 0, 0, 0, 0]:
                command = "stop"; gesture = "STOP ✋"
            else:
                gesture = "UNKNOWN 🤷"

            if command and command != last_command:
                command_queue.put(command)
                last_command = command

            cv2.putText(image, gesture, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # FPS Display
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time + 1e-5)
        prev_time = curr_time
        cv2.putText(image, f'FPS: {int(fps)}', (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("🤖 ESP Robot Control", image)
        if cv2.waitKey(1) & 0xFF == 27:
            command_queue.put("__exit__")
            break

cap.release()
cv2.destroyAllWindows()
