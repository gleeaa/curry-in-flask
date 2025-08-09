import cv2
import numpy as np

class CurryDetector:
    def __init__(self):
        self.curry_profiles = {
            'yellow': {'lower': np.array([15, 100, 100]), 'upper': np.array([25, 255, 255])},
            'red': {'lower': [np.array([0, 100, 100]), np.array([170, 100, 100])], 
                   'upper': [np.array([10, 255, 255]), np.array([180, 255, 255])]},
            'green': {'lower': np.array([40, 80, 80]), 'upper': np.array([80, 255, 255])},
            'brown': {'lower': np.array([10, 50, 50]), 'upper': np.array([20, 200, 200])}
        }
    
    def detect_curry(self, frame):
        # Resize for processing
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        best_mask = None
        max_coverage = 0
        
        for color, profile in self.curry_profiles.items():
            if color == 'red':
                mask = cv2.inRange(hsv, profile['lower'][0], profile['upper'][0]) | \
                       cv2.inRange(hsv, profile['lower'][1], profile['upper'][1])
            else:
                mask = cv2.inRange(hsv, profile['lower'], profile['upper'])
            
            coverage = cv2.countNonZero(mask)
            if coverage > max_coverage:
                max_coverage = coverage
                best_mask = mask
        
        return best_mask
    
    def calculate_thickness(self, frame):
        best_mask = self.detect_curry(frame)
        thickness_mask = cv2.bitwise_and(frame, frame, mask=best_mask)
        gray = cv2.cvtColor(thickness_mask, cv2.COLOR_BGR2GRAY)
        
        _, reflection_mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        
        total_pixels = cv2.countNonZero(best_mask)
        reflection_pixels = cv2.countNonZero(reflection_mask)
        
        base_coverage = (total_pixels / best_mask.size) * 100
        reflection_factor = (reflection_pixels / total_pixels) if total_pixels > 0 else 0
        
        if base_coverage < 5:
            thickness = "Very Thin"
            coverage_percentage = base_coverage * 0.8
        elif base_coverage < 20:
            thickness = "Thin layer"
            coverage_percentage = base_coverage * 0.9
        elif base_coverage < 50:
            thickness = "Medium layer"
            coverage_percentage = base_coverage * 1.1
        elif base_coverage < 80:
            thickness = "Thick layer"
            coverage_percentage = min(100, base_coverage * 1.3)
        else:
            thickness = "Very Thick layer"
            coverage_percentage = min(100, base_coverage * 1.5)
        
        if thickness in ["Thick layer", "Very Thick layer"]:
            reflection_adjustment = 1 - (reflection_factor * 0.3)
        else:
            reflection_adjustment = 1 - (reflection_factor * 0.7)
        
        final_percentage = min(100, coverage_percentage * reflection_adjustment)
        
        # Convert frame and masks to JPEG
        _, frame_jpeg = cv2.imencode('.jpg', frame)
        _, mask_jpeg = cv2.imencode('.jpg', best_mask)
        _, reflection_jpeg = cv2.imencode('.jpg', reflection_mask)
        
        return {
            'percentage': round(final_percentage, 2),
            'thickness': thickness,
            'reflection_ratio': round(reflection_factor, 2),
            'frame': frame_jpeg.tobytes(),
            'mask': mask_jpeg.tobytes(),
            'reflection_mask': reflection_jpeg.tobytes()
        }