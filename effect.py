import cv2
import numpy as np


def draw_explosion_effect(frame, x, y):
    """Tạo hiệu ứng nổ khi ngón tay vẫy hoặc nắm tay."""
    num_particles = 30
    for _ in range(num_particles):
        offset_x = np.random.randint(-30, 30)
        offset_y = np.random.randint(-30, 30)
        radius = np.random.randint(5, 15)
        color = (np.random.randint(200, 255), np.random.randint(100, 150), np.random.randint(0, 50))  # Tia lửa
        cv2.circle(frame, (x + offset_x, y + offset_y), radius, color, -1)


def draw_snow_effect(frame, x, y):
    """Tạo hiệu ứng bão tuyết xung quanh ngón tay."""
    num_snowflakes = 50
    for _ in range(num_snowflakes):
        offset_x = np.random.randint(-40, 40)
        offset_y = np.random.randint(-40, 40)
        size = np.random.randint(2, 6)
        color = (255, 255, 255)  # Màu trắng tuyết
        cv2.circle(frame, (x + offset_x, y + offset_y), size, color, -1)


def draw_sparkle_effect(frame, x, y):
    """Tạo hiệu ứng nhấp nháy ánh sáng (Sparkle)."""
    num_sparkles = 10
    for _ in range(num_sparkles):
        offset_x = np.random.randint(-30, 30)
        offset_y = np.random.randint(-30, 30)
        sparkle_x = x + offset_x
        sparkle_y = y + offset_y
        color = (np.random.randint(200, 255), np.random.randint(200, 255), np.random.randint(200, 255))  # Màu sắc ngẫu nhiên
        radius = np.random.randint(3, 6)  # Kích thước điểm sáng
        cv2.circle(frame, (sparkle_x, sparkle_y), radius, color, -1)


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






def draw_rainbow_effect(frame, x, y):
    """Tạo hiệu ứng cầu vồng cong theo vị trí ngón tay."""
    num_colors = 7  # Số màu cầu vồng
    radius = 100  # Bán kính của cầu vồng
    angle_step = np.pi / 10  # Các bước góc để tạo độ cong cho cầu vồng


    # Vẽ các cung cầu vồng với các màu khác nhau
    for i in range(num_colors):
        color = get_rainbow_color(i)
        angle = angle_step * i


        # Tính toán vị trí các điểm trên đường cong cầu vồng
        offset_x = int(radius * np.cos(angle))
        offset_y = int(radius * np.sin(angle))


        # Vẽ các cung cầu vồng theo vị trí ngón tay
        # cv2.arcLine(frame, (x, y), (x + offset_x, y + offset_y), color, 10)

        center = (x, y)
        axes = (abs(offset_x), abs(offset_y))  # size of the arc
        angle = 0  # rotation of the ellipse
        startAngle = 0
        endAngle = 90  # adjust based on desired curve
        cv2.ellipse(frame, center, axes, angle, startAngle, endAngle, color, 10)



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
