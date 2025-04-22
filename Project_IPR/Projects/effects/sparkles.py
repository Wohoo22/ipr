import cv2
import numpy as np

class SparklesEffect:
    def draw_sparkles(self, frame, x, y, intensity=0.5):
        """Draw sparkling effect at specified position"""
        sparkle_count = int(15 * intensity)
        max_size = int(90 * intensity)
        
        for _ in range(sparkle_count):
            sparkle_x = x + np.random.randint(-30, 30)
            sparkle_y = y + np.random.randint(-30, 30)
            size = np.random.randint(2, max_size)
            color = (255, 255, np.random.randint(200, 255))
            alpha = np.random.uniform(0.3, 0.8)
            
            # Create a temporary image for blending
            overlay = frame.copy()
            cv2.circle(overlay, (sparkle_x, sparkle_y), size, color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            
        return frame