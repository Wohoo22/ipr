from PIL import Image, ImageSequence
import cv2
import numpy as np

class FireEffect:
    def __init__(self):
        # Load and prepare fire GIF frames
        self.fire_frames = self._load_fire_gif("images/fire.gif")
        self.frame_index = 0
        
    def _load_fire_gif(self, gif_path):
        """Load and process GIF frames"""
        try:
            gif = Image.open(gif_path)
            fire_frames = []
            
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert("RGBA")
                frame_np = cv2.cvtColor(np.array(frame), cv2.COLOR_RGBA2BGRA)
                fire_frames.append(self._remove_black_background(frame_np))
                
            return fire_frames
        except Exception as e:
            print(f"Error loading fire GIF: {str(e)}")
            return []
            
    def _remove_black_background(self, image):
        """Convert black pixels to transparent"""
        bgr = image[:, :, :3]
        alpha = image[:, :, 3]
        
        # Create mask where pixels are nearly black
        black_mask = (bgr[:, :, 0] < 80) & (bgr[:, :, 1] < 80) & (bgr[:, :, 2] < 80)
        
        # Smooth transparency for better blending
        alpha[black_mask] = 0
        image[:, :, 3] = alpha
        return image
        
    def draw_fire(self, frame, x, y, size=200):
        """Draw animated fire effect at specified position with adjustable size"""
        if not self.fire_frames:
            return frame
            
        # Get current frame and resize
        fire_frame = self.fire_frames[self.frame_index]
        fire_resized = cv2.resize(fire_frame, (size, size), interpolation=cv2.INTER_AREA)
        
        # Calculate position (centered)
        x1, y1 = x - size // 2, y - size // 2
        x2, y2 = x1 + size, y1 + size
        
        # Check boundaries
        if x1 < 0 or y1 < 0 or x2 >= frame.shape[1] or y2 >= frame.shape[0]:
            return frame
            
        # Blend with background
        bgr = fire_resized[:, :, :3]
        alpha = fire_resized[:, :, 3] / 255.0  # Normalize
        
        for c in range(3):  # BGR channels
            frame[y1:y2, x1:x2, c] = (1 - alpha) * frame[y1:y2, x1:x2, c] + (alpha * bgr[:, :, c])
        
        # Update frame index for animation
        self.frame_index = (self.frame_index + 1) % len(self.fire_frames)
        return frame