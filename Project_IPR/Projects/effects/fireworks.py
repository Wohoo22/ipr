import cv2
import numpy as np

class FireworksEffect:
    def __init__(self):
        self.colors = [
            (255, 0, 0), (0, 255, 0), (0, 0, 255),
            (255, 255, 0), (255, 0, 255), (0, 255, 255)
        ]
        
    def draw_firework(self, frame, x, y, size=50):
        """Draw a firework explosion at the specified position"""
        # Draw central burst
        cv2.circle(frame, (x, y), int(size/10), (255, 255, 255), -1)
        
        # Create particles
        particle_count = int(size/5)
        for _ in range(particle_count):
            angle = np.random.uniform(0, 2 * np.pi)
            radius = np.random.randint(size//2, size)
            end_x = int(x + radius * np.cos(angle))
            end_y = int(y + radius * np.sin(angle))
            color = self.colors[np.random.randint(0, len(self.colors))]
            thickness = np.random.randint(1, 3)
            cv2.line(frame, (x, y), (end_x, end_y), color, thickness)
            
        return frame