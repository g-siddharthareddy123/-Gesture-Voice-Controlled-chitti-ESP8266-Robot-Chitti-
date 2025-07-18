import cv2
import mediapipe as mp
import time
import math

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
cap = cv2.VideoCapture(0)

tip_ids = [4, 8, 12, 16, 20]

def distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def get_finger_status(hand_landmarks):
    lm = hand_landmarks.landmark
    fingers = [1 if lm[tip_ids[0]].x < lm[tip_ids[0] - 1].x else 0]  # Thumb
    for i in range(1, 5):  # Index to Pinky
        fingers.append(1 if lm[tip_ids[i]].y < lm[tip_ids[i] - 2].y else 0)
    return fingers

def gesture_from_landmarks(hand_landmarks):
    fingers = get_finger_status(hand_landmarks)
    
    if fingers == [0, 1, 0, 0, 0]:   # New gesture for RIGHT
        return "RIGHT ✌️"
    if fingers == [0, 0, 0, 0, 0]:
        return "FORWARD ➡️"
    elif fingers == [1, 0, 0, 0, 0]:
        return "LEFT 👈"
    elif fingers == [0, 1, 1, 0, 0]:
        return "BACK ⬅️"
    elif fingers == [1, 1, 1, 1, 1]:
        return "STOP ✋"
    return "UNKNOWN ❓"

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:
    prev_time = 0
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break
        image = cv2.flip(image, 1)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                command = gesture_from_landmarks(hand)
                cv2.putText(image, f'Gesture: {command}', (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time + 1e-5)
        prev_time = curr_time
        cv2.putText(image, f'FPS: {int(fps)}', (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Hand Gesture Control", image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
