import cv2
import mediapipe as mp
from effect import draw_explosion_effect, draw_snow_effect, draw_sparkle_effect, draw_heart_effect, draw_moving_light_effect, draw_rainbow_effect


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


            # Áp dụng hiệu ứng dựa trên biến current_effect_idx
            if effects[current_effect_idx] == 'explosion':
                draw_explosion_effect(frame, x, y)
            elif effects[current_effect_idx] == 'snow':
                draw_snow_effect(frame, x, y)
            elif effects[current_effect_idx] == 'sparkle':
                draw_sparkle_effect(frame, x, y)
            elif effects[current_effect_idx] == 'heart':
                draw_heart_effect(frame, x, y, heart_image)  # Truyền heart_image vào đây
            elif effects[current_effect_idx] == 'moving_light':
                draw_moving_light_effect(frame, x, y)
            elif effects[current_effect_idx] == 'rainbow':  # Hiệu ứng cầu vồng
                draw_rainbow_effect(frame, x, y)


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
    elif key == ord('4'):  # Phím '4' để chọn hiệu ứng trái tim
        current_effect_idx = 3
    elif key == ord('5'):  # Phím '5' để chọn hiệu ứng ánh sáng chuyển động
        current_effect_idx = 4
    elif key == ord('6'):  # Phím '6' để chọn hiệu ứng cầu vồng
        current_effect_idx = 5
    elif key == ord('q'):  # Nhấn 'q' để thoát
        break


# Giải phóng tài nguyên khi thoát
cap.release()
cv2.destroyAllWindows()
