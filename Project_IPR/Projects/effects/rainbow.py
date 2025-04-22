import cv2
import numpy as np
from collections import deque

class RainbowEffect:
    def __init__(self, max_length=30, trail_width=5, color_cycle_speed=0.1):
        """
        Initialize the RainbowEffect with configurable parameters.
        
        Args:
            max_length (int): Maximum number of points in the trail
            trail_width (int): Base width of the trail
            color_cycle_speed (float): Speed of color cycling (0-1)
        """
        self.trail = deque(maxlen=max_length)
        self.base_width = trail_width
        self.color_cycle_speed = color_cycle_speed
        self.color_offset = 0
        
        # More vibrant rainbow colors with additional hues
        self.rainbow_colors = [
            (255, 0, 0),      # Red
            (255, 95, 0),     # Orange-Red
            (255, 127, 0),    # Orange
            (255, 191, 0),    # Gold
            (255, 255, 0),    # Yellow
            (191, 255, 0),    # Chartreuse
            (0, 255, 0),      # Green
            (0, 255, 127),   # Spring Green
            (0, 255, 255),    # Cyan
            (0, 127, 255),   # Azure
            (0, 0, 255),      # Blue
            (75, 0, 130),     # Indigo
            (128, 0, 128),    # Purple
            (148, 0, 211),    # Violet
            (255, 0, 255)     # Magenta
        ]
        
        # Pre-compute color gradients for smoother transitions
        self.color_gradients = self._create_color_gradients()

    def _create_color_gradients(self):
        """Create smooth color gradients between the rainbow colors"""
        gradients = []
        for i in range(len(self.rainbow_colors)):
            c1 = np.array(self.rainbow_colors[i])
            c2 = np.array(self.rainbow_colors[(i + 1) % len(self.rainbow_colors)])
            steps = 10
            gradient = [tuple(c1 + (c2 - c1) * t/steps) for t in range(steps)]
            gradients.extend(gradient)
        return gradients

    def update_trail(self, x, y):
        """
        Add a new point to the trail.
        
        Args:
            x (int): X coordinate of the new point
            y (int): Y coordinate of the new point
        """
        self.trail.append((x, y))
        self.color_offset = (self.color_offset + self.color_cycle_speed) % len(self.color_gradients)

    def draw_rainbow_trail(self, frame):
        """
        Draw the rainbow trail on the frame.
        
        Args:
            frame (numpy.ndarray): The image frame to draw on
            
        Returns:
            numpy.ndarray: The frame with rainbow trail drawn
        """
        if len(self.trail) < 2:
            return frame
            
        # Draw each segment with appropriate color and thickness
        for i in range(1, len(self.trail)):
            # Calculate dynamic thickness (thicker at the start)
            thickness = max(1, int(self.base_width * (1 - i/len(self.trail)) + 1))
            
            # Get color with cycling effect
            color_index = int((i * len(self.color_gradients) / len(self.trail) + self.color_offset) % len(self.color_gradients))
            color = self.color_gradients[color_index]
            
            # Draw anti-aliased line
            cv2.line(frame, self.trail[i-1], self.trail[i], color, thickness, 
                    lineType=cv2.LINE_AA)
            
            # Add glow effect by drawing a semi-transparent thicker line
            if thickness > 2:
                glow_color = (*color, 50)  # Add alpha for blending
                overlay = frame.copy()
                cv2.line(overlay, self.trail[i-1], self.trail[i], color, thickness+2, 
                         lineType=cv2.LINE_AA)
                cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        return frame

    def clear_trail(self):
        """Clear all points from the trail."""
        self.trail.clear()
        self.color_offset = 0

    def get_current_length(self):
        """Get the current length of the trail."""
        return len(self.trail)

    def set_max_length(self, length):
        """Set the maximum length of the trail."""
        self.trail = deque(self.trail, maxlen=length)