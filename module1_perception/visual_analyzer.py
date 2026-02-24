"""
Visual Analyzer Module
Detects health-related visual cues in product images
Like recognizing symbols: hearts, leaves, medical crosses, etc.
"""

import cv2
import numpy as np
from PIL import Image
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import IMAGE_SIZE, VISUAL_CONFIDENCE_THRESHOLD

class VisualAnalyzer:
    """
    Analyzes images for health-related visual cues
    Detects symbols like hearts, nature imagery, medical symbols, etc.
    """
    
    def __init__(self):
        """Initialize the visual analyzer"""
        print("👁️  Visual Analyzer initialized!")
        self.image_size = IMAGE_SIZE
        self.confidence_threshold = VISUAL_CONFIDENCE_THRESHOLD
        
        # Define health-related visual categories we're looking for
        self.visual_categories = {
            'medical': ['cross', 'plus sign', 'stethoscope', 'pill', 'capsule'],
            'nature': ['leaf', 'plant', 'green', 'organic', 'natural'],
            'fitness': ['muscle', 'dumbbell', 'running', 'athletic', 'sport'],
            'heart_health': ['heart', 'cardiovascular', 'pulse'],
            'science': ['molecule', 'atom', 'laboratory', 'beaker', 'scientific'],
            'wellness': ['yoga', 'meditation', 'zen', 'balance', 'harmony']
        }
        
        print(f"✅ Monitoring {len(self.visual_categories)} visual categories")
    
    def detect_color_patterns(self, image_path):
        """
        Analyze dominant colors in the image
        Certain colors are associated with health marketing:
        - Green = natural, organic
        - White = clean, pure
        - Blue = medical, scientific
        
        Args:
            image_path: Path to product image
            
        Returns:
            Dictionary with dominant colors and percentages
        """
        print(f"🎨 Analyzing colors in: {os.path.basename(image_path)}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Could not load image'}
        
        # Convert BGR to RGB (OpenCV uses BGR by default)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize for faster processing
        image_small = cv2.resize(image_rgb, (100, 100))
        
        # Flatten the image to a list of pixels
        pixels = image_small.reshape(-1, 3)
        
        # Calculate average color
        avg_color = np.mean(pixels, axis=0)
        
        # Detect dominant health-associated colors
        health_colors = {
            'green': self._is_green(avg_color),
            'white': self._is_white(avg_color),
            'blue': self._is_blue(avg_color)
        }
        
        # Count how many pixels are each health color
        color_counts = {
            'green': np.sum([self._is_green(p) for p in pixels]),
            'white': np.sum([self._is_white(p) for p in pixels]),
            'blue': np.sum([self._is_blue(p) for p in pixels])
        }
        
        total_pixels = len(pixels)
        color_percentages = {
            color: (count / total_pixels) * 100 
            for color, count in color_counts.items()
        }
        
        print(f"✅ Color analysis complete!")
        print(f"   Green: {color_percentages['green']:.1f}%")
        print(f"   White: {color_percentages['white']:.1f}%")
        print(f"   Blue: {color_percentages['blue']:.1f}%")
        
        return {
            'average_color': avg_color.tolist(),
            'health_color_present': health_colors,
            'color_percentages': color_percentages,
            'dominant_health_color': max(color_percentages, key=color_percentages.get)
        }
    
    def _is_green(self, rgb):
        """Check if color is greenish (nature/organic indicator)"""
        r, g, b = rgb
        return g > r and g > b and g > 100
    
    def _is_white(self, rgb):
        """Check if color is whitish (clean/pure indicator)"""
        r, g, b = rgb
        return r > 200 and g > 200 and b > 200
    
    def _is_blue(self, rgb):
        """Check if color is blueish (medical/scientific indicator)"""
        r, g, b = rgb
        return b > r and b > g and b > 100
    
    def detect_shapes(self, image_path):
        """
        Detect common health-related shapes
        - Circles (pills, symbols)
        - Crosses (medical symbols)
        - Hearts (cardiovascular health)
        
        Args:
            image_path: Path to product image
            
        Returns:
            Dictionary with detected shapes
        """
        print(f"🔍 Detecting shapes in: {os.path.basename(image_path)}")
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Could not load image'}
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours (outlines of shapes)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze shapes
        circles = 0
        rectangles = 0
        
        for contour in contours:
            # Get shape properties
            area = cv2.contourArea(contour)
            if area < 100:  # Ignore tiny shapes
                continue
            
            # Approximate the shape
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            
            # Count vertices to identify shape
            vertices = len(approx)
            
            if vertices > 8:  # Many vertices = likely a circle
                circles += 1
            elif vertices == 4:  # Four vertices = rectangle/square
                rectangles += 1
        
        print(f"✅ Found {circles} circular shapes, {rectangles} rectangular shapes")
        
        return {
            'circles': circles,
            'rectangles': rectangles,
            'total_shapes': len(contours)
        }
    
    def analyze_image_composition(self, image_path):
        """
        Analyze overall image composition for health signaling
        
        Returns:
            Dictionary with visual cues detected
        """
        print(f"\n📊 Analyzing composition: {os.path.basename(image_path)}")
        
        # Get color analysis
        color_result = self.detect_color_patterns(image_path)
        
        # Get shape analysis
        shape_result = self.detect_shapes(image_path)
        
        # Determine visual health signals
        health_signals = []
        
        # Check for nature/organic signaling (green colors)
        if color_result.get('color_percentages', {}).get('green', 0) > 20:
            health_signals.append({
                'type': 'nature',
                'description': 'Significant green coloring suggests natural/organic positioning',
                'confidence': min(color_result['color_percentages']['green'] / 100, 1.0)
            })
        
        # Check for medical/scientific signaling (blue/white colors)
        if color_result.get('color_percentages', {}).get('blue', 0) > 15:
            health_signals.append({
                'type': 'medical',
                'description': 'Blue coloring suggests medical/scientific positioning',
                'confidence': min(color_result['color_percentages']['blue'] / 100, 1.0)
            })
        
        # Check for clean/pure signaling (white background)
        if color_result.get('color_percentages', {}).get('white', 0) > 40:
            health_signals.append({
                'type': 'purity',
                'description': 'White background suggests clean/pure positioning',
                'confidence': min(color_result['color_percentages']['white'] / 100, 1.0)
            })
        
        # Check for pill/capsule shapes (circular)
        if shape_result.get('circles', 0) > 5:
            health_signals.append({
                'type': 'pharmaceutical',
                'description': 'Multiple circular shapes suggest pharmaceutical imagery',
                'confidence': min(shape_result['circles'] / 20, 1.0)
            })
        
        print(f"✅ Detected {len(health_signals)} health-related visual signals")
        
        return {
            'image_path': image_path,
            'color_analysis': color_result,
            'shape_analysis': shape_result,
            'health_signals': health_signals,
            'total_signals': len(health_signals)
        }
    
    def analyze_multiple_images(self, image_folder):
        """
        Analyze all images in a folder
        
        Args:
            image_folder: Path to folder containing images
            
        Returns:
            Dictionary mapping filenames to analysis results
        """
        print(f"\n📁 Analyzing all images in: {image_folder}")
        
        results = {}
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [
            f for f in os.listdir(image_folder)
            if os.path.splitext(f.lower())[1] in image_extensions
        ]
        
        print(f"Found {len(image_files)} images to analyze")
        
        for i, filename in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Analyzing: {filename}")
            image_path = os.path.join(image_folder, filename)
            results[filename] = self.analyze_image_composition(image_path)
        
        print(f"\n✅ Analyzed {len(results)} images!")
        return results


# Test the visual analyzer
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING VISUAL ANALYZER")
    print("=" * 60)
    
    analyzer = VisualAnalyzer()
    
    print("\n✅ Visual Analyzer is ready!")
    print("📝 This module detects health-related visual cues:")
    print("   - Color patterns (green=nature, blue=medical, white=pure)")
    print("   - Shapes (circles, crosses, hearts)")
    print("   - Overall health positioning signals")