import cv2
import mediapipe as mp
from effect import draw_explosion_effect, draw_snow_effect, draw_sparkle_effect, draw_heart_effect, draw_moving_light_effect, draw_rainbow_effect
import time
from collections import deque
import numpy as np
import math

def current_milli_time():
    return round(time.time() * 1000)

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)


# Mở camera
cap = cv2.VideoCapture(0)


# Biến điều khiển hiệu ứng
effects = ['explosion', 'snow', 'sparkle', 'heart', 'moving_light', 'rainbow']  # Thêm rainbow vào đây
current_effect_idx = 0  # Chỉ số của hiệu ứng hiện tại


# Tải ảnh trái tim (sticker) và ảnh cánh hoa
heart_image = cv2.imread('heart_sticker.png', cv2.IMREAD_UNCHANGED)  # Đọc ảnh PNG có kênh alpha (trong suốt)

# ================ HAND CLOSE OPEN UTILS ==================

is_hand_closed_before = True
last_time_hand_open_after_close = 0

def is_hand_open(landmarks):
    finger_tips = [8, 12, 16, 20]  # các đầu ngón trừ ngón cái
    finger_pips = [6, 10, 14, 18]  # khớp giữa ngón tay

    open_fingers = 0
    for tip, pip in zip(finger_tips, finger_pips):
        if landmarks[tip].y < landmarks[pip].y:
            open_fingers += 1

    return open_fingers >= 3  # ít nhất 3 ngón mở => coi như mở tay

# ================ INDEX FINGER DETECT UTILS ==================

index_finger_history = deque(maxlen=50)
last_time_index_finger_spin = 0

def is_only_index_raised(hand_landmarks):
    fingers = []

    if hand_landmarks.landmark[4].x < hand_landmarks.landmark[3].x:
        fingers.append(1)  # Thumb
    else:
        fingers.append(0)

    fingers.append(int(hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y))   # Index
    fingers.append(int(hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y)) # Middle
    fingers.append(int(hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y)) # Ring
    fingers.append(int(hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y)) # Pinky

    return fingers == [0, 1, 0, 0, 0]

def calculate_angle(p1, p2, center):
    """Tính góc (radian) từ center đến p1 và p2"""
    v1 = p1 - center
    v2 = p2 - center
    angle = math.atan2(v2[1], v2[0]) - math.atan2(v1[1], v1[0])
    angle = (angle + math.pi * 2) % (math.pi * 2)  # Normalize to [0, 2π]
    return angle

def detect_circular_motion(history):
    if len(history) < 40:
        return False

    points = np.array(history)
    center = np.mean(points, axis=0)

    total_angle = 0
    direction_consistency = 0
    last_angle = None

    for i in range(1, len(points)):
        angle = calculate_angle(points[i-1], points[i], center)

        if last_angle is not None:
            delta = angle
            if delta > math.pi:
                delta -= 2 * math.pi
            direction_consistency += delta
            total_angle += abs(delta)
        last_angle = angle

    # Convert total angular movement to degrees
    total_angle_degrees = total_angle * 180 / math.pi
    consistency_degrees = abs(direction_consistency) * 180 / math.pi

    # Criteria: moved at least ~270° and not reversing direction frequently
    return total_angle_degrees > 270 and consistency_degrees > 200

# ================ INDEX FINGER STORE UTILS FOR SPARKLES EFFECT ==================

index_finger_history_for_sparkles = deque(maxlen=50)


def calculate_hand_size(hand_landmarks, image_width, image_height):
    """Tính kích thước tương đối của bàn tay dựa trên khoảng cách giữa các điểm đặc trưng."""

    # Chọn hai điểm cố định để đo (ví dụ: cổ tay và đầu ngón giữa)
    wrist = hand_landmarks.landmark[0]
    middle_finger_tip = hand_landmarks.landmark[12]

    # Tính khoảng cách Euclidean
    x1, y1 = wrist.x * image_width, wrist.y * image_height
    x2, y2 = middle_finger_tip.x * image_width, middle_finger_tip.y * image_height

    distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance  # Khoảng cách pixel

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break


    # Lật ảnh để không bị ngược
    frame = cv2.flip(frame, 1)


    # Chuyển đổi màu từ BGR sang RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    # Dự đoán bàn tay
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Vẽ khung xương bàn tay
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)


            # Lấy tọa độ ngón tay trỏ
            index_finger = hand_landmarks.landmark[8]
            h, w, c = frame.shape
            x = int(index_finger.x * w)
            y = int(index_finger.y * h)

            # ===================== DETECT IS HAND CLOSE AND OPEN =======================

            is_hand_open_after_close = False

            if is_hand_open(hand_landmarks.landmark):
                is_hand_open_after_close = is_hand_closed_before
                is_hand_closed_before = False
            else:
                is_hand_closed_before = True

            if is_hand_open_after_close:
                last_time_hand_open_after_close = current_milli_time()

            # ==================== DETECT INDEX FINGER SPIN ===============================
            if is_only_index_raised(hand_landmarks):
                index_tip = hand_landmarks.landmark[8]
                index_finger_history.append(np.array([index_tip.x, index_tip.y]))

                if detect_circular_motion(index_finger_history):
                    last_time_index_finger_spin = current_milli_time()
                    index_finger_history.clear()
            else:
                index_finger_history.clear()
            # ==================== STORE INDEX FINGER HISTORY FOR SPARKLES EFFECT ===============================

            index_finger_history_for_sparkles.append([x, y])


            # ==================== CALCULATE DEPTH ===============================
            # Lấy tọa độ z của cổ tay (landmark số 0)
            hand_size = calculate_hand_size(hand_landmarks, frame.shape[1], frame.shape[0])

            # Áp dụng hiệu ứng dựa trên biến current_effect_idx
            if effects[current_effect_idx] == 'explosion':
                draw_explosion_effect(frame, x, y, last_time_hand_open_after_close)
            elif effects[current_effect_idx] == 'snow':
                draw_snow_effect(frame, x, y, last_time_index_finger_spin)
            elif effects[current_effect_idx] == 'sparkle':
                draw_sparkle_effect(frame, x, y, index_finger_history_for_sparkles)
            elif effects[current_effect_idx] == 'heart':
                draw_heart_effect(frame, x, y, heart_image)  # Truyền heart_image vào đây
            elif effects[current_effect_idx] == 'moving_light':
                draw_moving_light_effect(frame, x, y)
            elif effects[current_effect_idx] == 'rainbow':  # Hiệu ứng cầu vồng
                draw_rainbow_effect(frame, x, y, hand_size)


    # Hiển thị hình ảnh
    cv2.imshow("Hand Tracking with Effects", frame)


    # Nhấn phím để chuyển đổi hiệu ứng
    key = cv2.waitKey(1) & 0xFF


    if key == ord('1'):  # Phím '1' để chọn hiệu ứng nổ
        current_effect_idx = 0
    elif key == ord('2'):  # Phím '2' để chọn hiệu ứng tuyết
        current_effect_idx = 1
    elif key == ord('3'):  # Phím '3' để chọn hiệu ứng nhấp nháy ánh sáng
        current_effect_idx = 2
    # elif key == ord('4'):  # Phím '4' để chọn hiệu ứng trái tim
    #     current_effect_idx = 3
    elif key == ord('5'):  # Phím '5' để chọn hiệu ứng ánh sáng chuyển động
        current_effect_idx = 4
    elif key == ord('6'):  # Phím '6' để chọn hiệu ứng cầu vồng
        current_effect_idx = 5
    elif key == ord('q'):  # Nhấn 'q' để thoát
        break


# Giải phóng tài nguyên khi thoát
cap.release()
cv2.destroyAllWindows()
