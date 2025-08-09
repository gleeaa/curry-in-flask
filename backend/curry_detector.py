import cv2
import numpy as np
from scipy import ndimage
from skimage import feature, filters

class AdvancedCurryDetector:
    def __init__(self):
        # Color ranges for different curry types
        self.color_profiles = {
            'yellow': {'lower': np.array([20, 100, 100]), 'upper': np.array([30, 255, 255])},
            'red': {'lower': np.array([0, 100, 100]), 'upper': np.array([10, 255, 255])},
            'brown': {'lower': np.array([10, 60, 60]), 'upper': np.array([20, 160, 160])}
        }
        
        # Texture analysis parameters
        self.texture_params = {
            'gloss_threshold': 200,  # Value for reflection detection
            'grain_size': 3,         # For particle analysis
            'viscosity_factor': 0.7  # Weight for flow pattern analysis
        }

    def analyze_thickness(self, frame):
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # 1. Color-based segmentation
        color_mask = self._get_color_mask(hsv)
        color_coverage = np.sum(color_mask) / color_mask.size
        
        # 2. Reflection analysis (glossiness)
        reflection_ratio = self._analyze_reflections(gray)
        
        # 3. Texture and grain analysis
        texture_score = self._analyze_texture(gray)
        
        # 4. Flow pattern analysis (viscosity)
        viscosity_score = self._analyze_viscosity(gray)
        
        # Combine factors with weighted average
        thickness_score = (
            0.4 * color_coverage + 
            0.2 * (1 - reflection_ratio) + 
            0.3 * texture_score + 
            0.1 * viscosity_score
        )
        
        # Convert to percentage (0-100 scale)
        final_percentage = np.clip(thickness_score * 100, 0, 100)
        
        # Generate visualization masks
        vis_masks = self._generate_visualizations(frame, color_mask, gray)
        
        return {
            'percentage': round(float(final_percentage), 2),
            'masks': vis_masks,
            'metrics': {
                'color_coverage': round(float(color_coverage * 100), 2),
                'reflection_ratio': round(float(reflection_ratio * 100), 2),
                'texture_score': round(float(texture_score * 100), 2),
                'viscosity_score': round(float(viscosity_score * 100), 2)
            }
        }

    def _get_color_mask(self, hsv):
        combined_mask = np.zeros((hsv.shape[0], hsv.shape[1]), dtype=np.uint8)
        for _, profile in self.color_profiles.items():
            if isinstance(profile['lower'], list):
                # Handle red color range (wraps around 0)
                mask1 = cv2.inRange(hsv, profile['lower'][0], profile['upper'][0])
                mask2 = cv2.inRange(hsv, profile['lower'][1], profile['upper'][1])
                mask = mask1 | mask2
            else:
                mask = cv2.inRange(hsv, profile['lower'], profile['upper'])
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Apply morphological operations
        kernel = np.ones((5,5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        return combined_mask

    def _analyze_reflections(self, gray):
        # Detect specular highlights
        _, reflection_mask = cv2.threshold(gray, self.texture_params['gloss_threshold'], 255, cv2.THRESH_BINARY)
        reflection_area = np.sum(reflection_mask > 0)
        return reflection_area / reflection_mask.size

    def _analyze_texture(self, gray):
        # Analyze grain patterns using edge detection
        edges = feature.canny(gray, sigma=2)
        
        # Calculate density of particles
        labeled, num_features = ndimage.label(edges)
        particle_density = num_features / gray.size
        
        # Normalize to 0-1 range
        return 1 - np.exp(-particle_density * 100)

    def _analyze_viscosity(self, gray):
        # Detect flow patterns using oriented gradients
        gx = filters.sobel_h(gray)
        gy = filters.sobel_v(gray)
        magnitude = np.sqrt(gx**2 + gy**2)
        
        # Viscous liquids have more uniform flow patterns
        flow_uniformity = np.std(magnitude) / 255
        return self.texture_params['viscosity_factor'] * (1 - flow_uniformity)

    def _generate_visualizations(self, frame, color_mask, gray):
        # Create color mask visualization
        color_vis = cv2.bitwise_and(frame, frame, mask=color_mask)
        
        # Create reflection visualization
        _, reflection_mask = cv2.threshold(gray, self.texture_params['gloss_threshold'], 255, cv2.THRESH_BINARY)
        reflection_vis = cv2.cvtColor(reflection_mask, cv2.COLOR_GRAY2BGR)
        
        # Create texture visualization
        edges = feature.canny(gray, sigma=2)
        texture_vis = cv2.cvtColor((edges * 255).astype(np.uint8), cv2.COLOR_GRAY2BGR)
        
        return {
            'color_mask': color_vis,
            'reflection_mask': reflection_vis,
            'texture_mask': texture_vis
        }
