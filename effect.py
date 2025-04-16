import cv2
import numpy as np
import time
import random

def current_milli_time():
    return round(time.time() * 1000)

def draw_explosion_effect(frame, x, y, last_time_hand_open_after_close):
    """Tạo hiệu ứng nổ khi ngón tay vẫy hoặc nắm tay."""
    def more_explosion():
        second_since_last = (current_milli_time() - last_time_hand_open_after_close) / 1000
        return second_since_last < 1.5

    is_more_explosion = more_explosion()
    num_particles = 100 if is_more_explosion else 30
    for _ in range(num_particles):
        offset_x = np.random.randint(-num_particles, num_particles)
        offset_y = np.random.randint(-num_particles, num_particles)
        radius = np.random.randint(5, 15)
        color = (np.random.randint(200, 255), np.random.randint(100, 150), np.random.randint(0, 50))  # Tia lửa
        if is_more_explosion:
            color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)) 
        cv2.circle(frame, (x + offset_x, y + offset_y), radius, color, -1)


class Snowflake:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size = random.randint(2, 5)
        self.speed = random.uniform(1, 3)
        self.wind = random.uniform(-1, 1)

    def update(self, width, height):
        self.y += self.speed
        self.x += self.wind

        # Nếu rơi xuống dưới màn hình thì reset lại phía trên
        if self.y > height:
            self.y = random.uniform(-10, -5)
            self.x = random.randint(0, width)
            self.speed = random.uniform(1, 3)
            self.wind = random.uniform(-1, 1)

    def draw(self, frame):
        cv2.circle(frame, (int(self.x), int(self.y)), self.size, (255, 255, 255), -1)

class SnowEffect:
    def __init__(self, width, height, num_snowflakes=100):
        self.width = width
        self.height = height
        self.snowflakes = [Snowflake(width, height) for _ in range(num_snowflakes)]

    def update_and_draw(self, frame):
        for flake in self.snowflakes:
            flake.update(self.width, self.height)
            flake.draw(frame)


def draw_snow_effect(frame, x, y, last_time_index_finger_spin):
    def snow_rain():
        second_since_last = (current_milli_time() - last_time_index_finger_spin) / 1000
        return second_since_last < 1.5
    
    is_snow_rain = snow_rain()

    if is_snow_rain:
        h, w = frame.shape[:2]
        snow = SnowEffect(w, h, num_snowflakes=120)
        snow.update_and_draw(frame)

    """Tạo hiệu ứng bão tuyết xung quanh ngón tay."""
    num_snowflakes = 50
    for _ in range(num_snowflakes):
        offset_x = np.random.randint(-40, 40)
        offset_y = np.random.randint(-40, 40)
        size = np.random.randint(2, 6)
        color = (255, 255, 255)  # Màu trắng tuyết
        cv2.circle(frame, (x + offset_x, y + offset_y), size, color, -1)


def draw_sparkle_effect(frame, x, y, index_finger_history):
    """Tạo hiệu ứng nhấp nháy ánh sáng (Sparkle)."""
    def draw_sparkles(x, y, num_sparkles):
        for _ in range(num_sparkles):
            offset_x = np.random.randint(-30, 30)
            offset_y = np.random.randint(-30, 30)
            sparkle_x = x + offset_x
            sparkle_y = y + offset_y
            color = (np.random.randint(200, 255), np.random.randint(200, 255), np.random.randint(200, 255))  # Màu sắc ngẫu nhiên
            radius = np.random.randint(3, 6)  # Kích thước điểm sáng
            cv2.circle(frame, (sparkle_x, sparkle_y), radius, color, -1)
    draw_sparkles(x, y, 10)
    for item in reversed(index_finger_history):
        draw_sparkles(item[0], item[1], 5)




def draw_heart_effect(frame, x, y, heart_image):
    """Chèn sticker trái tim nhỏ vào vị trí (x, y)."""
    # Thay đổi kích thước trái tim cho nhỏ hơn
    heart_height, heart_width = heart_image.shape[:2]
    new_size = (int(heart_width * 0.2), int(heart_height * 0.2))  # Thay đổi tỉ lệ xuống 20% (có thể điều chỉnh)
    resized_heart = cv2.resize(heart_image, new_size)


    heart_height, heart_width = resized_heart.shape[:2]
    top_left_x = x - heart_width // 2
    top_left_y = y - heart_height // 2


    if top_left_x < 0 or top_left_y < 0 or top_left_x + heart_width > frame.shape[1] or top_left_y + heart_height > frame.shape[0]:
        return


    for i in range(heart_height):
        for j in range(heart_width):
            if resized_heart[i, j][3] != 0:  # Kiểm tra alpha channel (kênh trong suốt)
                frame[top_left_y + i, top_left_x + j] = resized_heart[i, j, :3]


def draw_moving_light_effect(frame, x, y):
    """Tạo hiệu ứng ánh sáng chuyển động."""
    num_beams = 12
    max_length = 100
    for i in range(num_beams):
        angle = np.random.uniform(0, 2 * np.pi)
        length = np.random.randint(50, max_length)
        color = (np.random.randint(150, 255), np.random.randint(150, 255), np.random.randint(150, 255))
        beam_x = int(x + length * np.cos(angle))
        beam_y = int(y + length * np.sin(angle))
        cv2.line(frame, (x, y), (beam_x, beam_y), color, 2)



def get_rainbow_color(i):
    """Trả về một màu trong cầu vồng dựa trên chỉ số."""
    rainbow_colors = [
        (255, 0, 0),      # Red
        (255, 127, 0),    # Orange
        (255, 255, 0),    # Yellow
        (0, 255, 0),      # Green
        (0, 0, 255),      # Blue
        (75, 0, 130),     # Indigo
        (148, 0, 211)     # Violet
    ]
    return rainbow_colors[i % len(rainbow_colors)]



# def draw_rainbow_effect(frame, x, y, wrist_z):
#     """Tạo hiệu ứng cầu vồng cong theo vị trí ngón tay."""
#     num_colors = 7      # Số màu cầu vồng
#     base_radius = 60    # Bán kính cơ bản
#     thickness = 10      # Độ dày của mỗi cung

#     for i in range(num_colors):
#         color = get_rainbow_color(i)
#         radius = base_radius + i * thickness

#         center = (x, y)
#         axes = (radius, radius // 2)  # Dạng ellipse để tạo độ cong
#         angle = 0                     # Không xoay
#         start_angle = 180
#         end_angle = 360               # Nửa vòng để tạo hiệu ứng cong

#         cv2.ellipse(frame, center, axes, angle, start_angle, end_angle, color, thickness)

def draw_rainbow_effect(frame, x, y, hand_size):
    """Vẽ cầu vồng với kích thước thay đổi theo độ gần của cổ tay (wrist_z)."""
    num_colors = 7
    base_radius = 60
    thickness = 10

    # Scale cầu vồng: càng gần (wrist_z nhỏ) thì càng to
    scale = max(0.5, 0.025 * hand_size)  # scale nằm trong khoảng 0.5x → 2.5x

    for i in range(num_colors):
        color = get_rainbow_color(i)
        
        radius = int((base_radius + i * thickness) * scale)
        axes = (radius, int(radius * 0.5))  # Dạng ellipse theo tỉ lệ

        center = (x, y)
        angle = 0
        start_angle = 180
        end_angle = 360

        # Tăng độ dày cũng theo scale (giữ được độ đậm đều)
        line_thickness = max(1, int(thickness * scale * 0.7))

        cv2.ellipse(frame, center, axes, angle, start_angle, end_angle, color, line_thickness)



def get_rainbow_color(index):
    """Trả về màu cầu vồng theo chỉ số."""
    rainbow_colors = [
        (148, 0, 211),  # Tím
        (75, 0, 130),   # Chàm
        (0, 0, 255),    # Đỏ
        (255, 127, 0),  # Cam
        (255, 255, 0),  # Vàng
        (0, 255, 0),    # Lục
        (0, 0, 255)     # Lam
    ]
    return rainbow_colors[index % len(rainbow_colors)]
