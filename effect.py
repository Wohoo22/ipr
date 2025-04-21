import cv2
import numpy as np
import time
import random
import math
import os

def current_milli_time():
    return round(time.time() * 1000)

# Load the explosion icon once globally (with alpha channel)
explosion_icon = cv2.imread("explosion_icon.png", cv2.IMREAD_UNCHANGED)

# Global particle list
explosion_particles = []

class ExplosionParticle:
    def __init__(self, x, y, is_more):
        size = 90 if is_more else 30
        self.x = x + np.random.randint(-size, size)
        self.y = y + np.random.randint(-size, size)
        self.size = np.random.uniform(0.3, 0.6)
        self.birth_time = current_milli_time()
        self.lifetime = np.random.randint(500, 1500)  # milliseconds

    def age(self):
        return current_milli_time() - self.birth_time

    def is_alive(self):
        return self.age() < self.lifetime

    def draw(self, frame):
        age_ratio = self.age() / self.lifetime
        scale = 1 + age_ratio * 1.5  # increase size as it ages
        alpha = max(1.0 - age_ratio, 0)

        resized_icon = cv2.resize(
            explosion_icon, 
            (0, 0), 
            fx=self.size * scale, 
            fy=self.size * scale, 
            interpolation=cv2.INTER_AREA
        )

        icon_h, icon_w = resized_icon.shape[:2]
        x1 = int(self.x - icon_w // 2)
        y1 = int(self.y - icon_h // 2)

        # Ensure bounds
        if x1 < 0 or y1 < 0 or x1 + icon_w > frame.shape[1] or y1 + icon_h > frame.shape[0]:
            return

        # Separate alpha channel and color
        icon_rgb = resized_icon[:, :, :3]
        icon_alpha = resized_icon[:, :, 3] / 255.0 * alpha

        for c in range(3):
            frame[y1:y1+icon_h, x1:x1+icon_w, c] = (
                icon_alpha * icon_rgb[:, :, c] +
                (1 - icon_alpha) * frame[y1:y1+icon_h, x1:x1+icon_w, c]
            ).astype(np.uint8)

def draw_explosion_effect(frame, x, y, last_time_hand_open_after_close):
    def more_explosion():
        second_since_last = (current_milli_time() - last_time_hand_open_after_close) / 1000
        return second_since_last < 1.5

    global explosion_particles
    is_more = more_explosion()
    num_new_particles = 15 if is_more else 3

    # Add new particles
    for _ in range(num_new_particles):
        explosion_particles.append(ExplosionParticle(x, y, is_more))

    # Draw and keep alive particles
    alive_particles = []
    for particle in explosion_particles:
        if particle.is_alive():
            particle.draw(frame)
            alive_particles.append(particle)

    explosion_particles = alive_particles  # Update list

# Load snowflake icon with alpha channel
snowflake_icon = cv2.imread("snowflake_icon.png", cv2.IMREAD_UNCHANGED)

class RealisticSnowflake:
    def __init__(self, width, height):
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.size_scale = random.uniform(0.3, 0.8)
        self.speed = random.uniform(1, 2)
        self.wind = random.uniform(-0.5, 0.5)
        self.angle = random.uniform(0, 360)
        self.spin_speed = random.uniform(-1, 1)

    def update(self, width, height):
        self.y += self.speed
        self.x += self.wind
        self.angle = (self.angle + self.spin_speed) % 360

        # Reset if below screen
        if self.y > height:
            self.y = random.uniform(-20, -10)
            self.x = random.randint(0, width)
            self.speed = random.uniform(1, 2)
            self.wind = random.uniform(-0.5, 0.5)
            self.angle = random.uniform(0, 360)

    def draw(self, frame):
        # Resize and rotate the snowflake
        scaled_icon = cv2.resize(
            snowflake_icon, 
            (0, 0), 
            fx=self.size_scale, 
            fy=self.size_scale, 
            interpolation=cv2.INTER_AREA
        )

        (h, w) = scaled_icon.shape[:2]
        center = (w // 2, h // 2)

        # Rotate with transparency
        M = cv2.getRotationMatrix2D(center, self.angle, 1.0)
        rotated = cv2.warpAffine(scaled_icon, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

        x1 = int(self.x - w // 2)
        y1 = int(self.y - h // 2)

        if x1 < 0 or y1 < 0 or x1 + w > frame.shape[1] or y1 + h > frame.shape[0]:
            return

        icon_rgb = rotated[:, :, :3]
        icon_alpha = rotated[:, :, 3] / 255.0

        for c in range(3):
            frame[y1:y1+h, x1:x1+w, c] = (
                icon_alpha * icon_rgb[:, :, c] +
                (1 - icon_alpha) * frame[y1:y1+h, x1:x1+w, c]
            ).astype(np.uint8)

class RealisticSnowEffect:
    def __init__(self, width, height, num_snowflakes=100):
        self.snowflakes = [RealisticSnowflake(width, height) for _ in range(num_snowflakes)]
        self.width = width
        self.height = height

    def update_and_draw(self, frame):
        for flake in self.snowflakes:
            flake.update(self.width, self.height)
            flake.draw(frame)

# Initialize globally once
realistic_snow = None

def draw_snow_effect(frame, x, y, last_time_index_finger_spin):
    global realistic_snow

    def snow_rain():
        return (current_milli_time() - last_time_index_finger_spin) / 1000 < 1

    h, w = frame.shape[:2]
    if realistic_snow is None:
        realistic_snow = RealisticSnowEffect(w, h, num_snowflakes=100)

    if snow_rain():
        realistic_snow.update_and_draw(frame)

    # Local snow burst around finger
    for _ in range(30):
        offset_x = np.random.randint(-40, 40)
        offset_y = np.random.randint(-40, 40)
        scale = np.random.uniform(0.2, 0.6)
        angle = np.random.uniform(0, 360)

        icon = cv2.resize(snowflake_icon, (0, 0), fx=scale, fy=scale)
        (ih, iw) = icon.shape[:2]
        center = (iw // 2, ih // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(icon, M, (iw, ih), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))

        x1 = int(x + offset_x - iw // 2)
        y1 = int(y + offset_y - ih // 2)

        if 0 <= x1 <= w - iw and 0 <= y1 <= h - ih:
            icon_rgb = rotated[:, :, :3]
            icon_alpha = rotated[:, :, 3] / 255.0
            for c in range(3):
                frame[y1:y1+ih, x1:x1+iw, c] = (
                    icon_alpha * icon_rgb[:, :, c] +
                    (1 - icon_alpha) * frame[y1:y1+ih, x1:x1+iw, c]
                ).astype(np.uint8)

# Load sparkle images once
sparkle_images = [
    cv2.imread(os.path.join("sparkles", f), cv2.IMREAD_UNCHANGED)
    for f in os.listdir("sparkles")
    if f.endswith(".png")
]

def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    """Overlay `img_overlay` onto `img` at (x, y) with alpha mask."""
    h, w = img_overlay.shape[:2]
    if x < 0 or y < 0 or x + w > img.shape[1] or y + h > img.shape[0]:
        return  # skip if out of bounds

    roi = img[y:y+h, x:x+w]
    alpha = alpha_mask.astype(float) / 255
    for c in range(3):
        roi[..., c] = roi[..., c] * (1 - alpha) + img_overlay[..., c] * alpha

    img[y:y+h, x:x+w] = roi

def draw_sparkle_effect(frame, x, y, index_finger_history):
    """Vẽ hiệu ứng sparkle dùng ảnh với nhấp nháy và kích thước ngẫu nhiên."""

    def draw_sparkles(px, py, num_sparkles):
        for _ in range(num_sparkles):
            if not sparkle_images:
                continue

            sparkle = random.choice(sparkle_images)

            # Resize random
            scale = random.uniform(0.2, 0.6)
            new_w = int(sparkle.shape[1] * scale)
            new_h = int(sparkle.shape[0] * scale)
            sparkle_resized = cv2.resize(sparkle, (new_w, new_h), interpolation=cv2.INTER_AREA)

            # Random transparency (blink effect)
            alpha = sparkle_resized[..., 3]
            blink_factor = random.uniform(0.2, 1.0)
            alpha = (alpha * blink_factor).astype(np.uint8)

            # Position
            offset_x = random.randint(-30, 30)
            offset_y = random.randint(-30, 30)
            pos_x = int(px + offset_x)
            pos_y = int(py + offset_y)

            overlay_image_alpha(frame, sparkle_resized, pos_x, pos_y, alpha)

    draw_sparkles(x, y, 5)
    for hx, hy in reversed(index_finger_history):
        draw_sparkles(hx, hy, 2)

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
