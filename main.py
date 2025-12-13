import cv2
import mediapipe as mp
import math
import time
import json
import os
import webbrowser
import pyautogui

def load_config():
    default_config = {
        "max_digit": 6,
        "blink_threshold": 0.24,
        "input_delay": 1.0,
        "reset_delay": 3.0,
        "commands": [
            {"name": "DEFAULT LOGIN", "code": [0, 1, 0, 1, 0, 1], "action_id": "login"}
        ]
    }
    
    if not os.path.exists('config.json'):
        return default_config
    
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception:
        return default_config

CONFIG = load_config()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

def calculate_distance(p1, p2):
    return math.sqrt((p2.x - p1.x)**2 + (p2.y - p1.y)**2)

def get_blink_ratio(landmarks, indices):
    left = landmarks[indices[0]]
    right = landmarks[indices[1]]
    top = landmarks[indices[2]]
    bottom = landmarks[indices[3]]
    eye_width = calculate_distance(left, right)
    eye_height = calculate_distance(top, bottom)
    if eye_width == 0: return 0
    return eye_height / eye_width

RIGHT_EYE = [362, 263, 386, 374]
LEFT_EYE = [33, 133, 159, 145]

system_state = "STANDBY" 
input_sequence = []
wink_active = False
state_timer = 0
last_input_time = 0

triggered_command_name = "" 
triggered_action_id = ""

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret: break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape
    
    hands_results = hands.process(rgb_frame)
    face_results = face_mesh.process(rgb_frame)
    current_time = time.time()

    # ==========================================================
    # Logic 1 : Activation Mode (Thumbs Up)
    # ==========================================================
    if system_state == "STANDBY":
        cv2.rectangle(frame, (0, 0), (w, h), (10, 10, 10), -1) 
        cv2.putText(frame, "COMMAND CENTER", (w//2 - 160, h//2 - 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 200, 0), 2)
        cv2.putText(frame, "Give Thumbs Up for Activation!", (w//2 - 250, h//2 + 20), cv2.FONT_HERSHEY_PLAIN, 1.5, (200, 200, 200), 1)

        if hands_results.multi_hand_landmarks:
            for hand_landmarks in hands_results.multi_hand_landmarks:
                lm = hand_landmarks.landmark
                thumb_up = lm[4].y < lm[3].y
                others_down = (lm[8].y > lm[6].y) and (lm[12].y > lm[10].y)
                
                if thumb_up and others_down:
                    system_state = "INPUT"
                    input_sequence = []
                    CONFIG = load_config() 
                    print(">>> Entering Input mode <<<")

    # ==========================================================
    # Logic 2 : Input Mode (Wink Detection)
    # ==========================================================
    elif system_state == "INPUT":
        in_cooldown = False 

        if face_results.multi_face_landmarks:
            landmarks = face_results.multi_face_landmarks[0].landmark
            
            ratio_left = get_blink_ratio(landmarks, LEFT_EYE)
            ratio_right = get_blink_ratio(landmarks, RIGHT_EYE)
            left_closed = ratio_left < CONFIG['blink_threshold']
            right_closed = ratio_right < CONFIG['blink_threshold']

            in_cooldown = (current_time - last_input_time) < CONFIG['input_delay']

            if not wink_active:
                input_val = None
                if not in_cooldown:
                    if left_closed and right_closed: wink_active = True 
                    elif right_closed and not left_closed: input_val = 1
                    elif left_closed and not right_closed: input_val = 0
                
                if input_val is not None and len(input_sequence) < CONFIG['max_digit']:
                    input_sequence.append(input_val)
                    wink_active = True
                    last_input_time = current_time
                    print(f"Input: {input_val}")
            else:
                if not left_closed and not right_closed: wink_active = False

            if len(input_sequence) == CONFIG['max_digit']:
                found_match = False
                for command in CONFIG['commands']:
                    if input_sequence == command['code']:
                        system_state = "SUCCESS"
                        triggered_command_name = command['name']
                        triggered_action_id = command['action_id']
                        found_match = True
                        print(f">>> Excecution Command : {triggered_command_name}")
                        break 
                
                if not found_match:
                    system_state = "FAIL"
                
                state_timer = current_time

        cv2.rectangle(frame, (0, h-80), (w, h), (20, 20, 20), -1)
        
        status_text = "WAIT..." if in_cooldown else "READY"
        status_color = (0, 255, 255) if in_cooldown else (0, 255, 0)
        cv2.putText(frame, status_text, (w//2 - 40, h-90), cv2.FONT_HERSHEY_PLAIN, 1.5, status_color, 2)

        center_x = w // 2
        start_x = center_x - ((CONFIG['max_digit'] * 40) // 2) + 20
        for i in range(CONFIG['max_digit']):
            x = start_x + (i * 40)
            if i < len(input_sequence):
                cv2.circle(frame, (x, h-40), 12, (0, 255, 255), -1)
                cv2.putText(frame, str(input_sequence[i]), (x-5, h-35), cv2.FONT_HERSHEY_PLAIN, 1.2, (0,0,0), 2)
            else:
                cv2.circle(frame, (x, h-40), 12, (100, 100, 100), 2)

    # ==========================================================
    # Logic 3 : Result Mode (Success / Fail)
    # ==========================================================
    elif system_state in ["SUCCESS", "FAIL"]:
        if system_state == "SUCCESS":
            cv2.rectangle(frame, (0, 0), (w, h), (0, 255, 0), -1)
            cv2.putText(frame, "CODE RECIVED:", (w//2 - 180, h//2 - 40), 
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)
            cv2.putText(frame, triggered_command_name, (w//2 - 200, h//2 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 3)
            
            # -- Action Logics --
            # 1. Play YouTube Video
            if triggered_action_id == "play_youtube":
                url_video = "https://youtu.be/ic98J9ZbtQ0?si=hwPOz62g-sBY4uvc" # Change this to your desired video URL
                
                cv2.putText(frame, "Opening & Fullscreen...", (w//2 - 180, h//2 + 80), 
                            cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 0), 2)
                cv2.imshow('Multi-Command Eye System', frame) 
                cv2.waitKey(100) 
                
                webbrowser.open(url_video)
                print(f">>> Opening : {url_video}")
                time.sleep(5) 

                print(">>> Pressing F to Fullscreen...")
                pyautogui.press('f')

            # 2. Terminate Application
            elif triggered_action_id == "terminate_app":
                cv2.putText(frame, "Terminating Application...", (w//2 - 200, h//2 + 80), 
                            cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 0), 2)
                cv2.imshow('Multi-Command Eye System', frame) 
                cv2.waitKey(100) 
                
                print(">>> Terminating Application...")
                cap.release()
                cv2.destroyAllWindows()
                exit(0)
                
            # Add more actions here as needed
            # elif triggered_action_id == ...

        else:
            cv2.rectangle(frame, (0, 0), (w, h), (0, 0, 255), -1)
            cv2.putText(frame, "CODE NOT RECIVED", (w//2 - 220, h//2), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3)

        if current_time - state_timer > CONFIG['reset_delay']: 
            system_state = "STANDBY"
            input_sequence = []

    cv2.imshow('Multi-Command Eye System', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()