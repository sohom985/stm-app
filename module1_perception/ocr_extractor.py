"""
OCR (Optical Character Recognition) Extractor
This module reads text from product images using Tesseract OCR
Think of it as: Teaching the computer to "read" text from pictures!
"""

import pytesseract
from PIL import Image
import cv2
import numpy as np
import os
import sys

# Add parent directory to path so we can import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OCR_LANGUAGE, OCR_CONFIG, RAW_DATA_DIR

class OCRExtractor:
    """
    Extracts text from product images
    Like a human reading a label, but automated!
    """
    
    def __init__(self):
        """Initialize the OCR extractor"""
        print("🔤 OCR Extractor initialized!")
        self.language = OCR_LANGUAGE
        self.config = OCR_CONFIG
        
        # Check if Tesseract is installed
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract OCR is ready!")
        except Exception as e:
            print("❌ Tesseract not found! We'll install it later.")
            print(f"   Error: {e}")
    
    def preprocess_image(self, image_path):
        """
        Prepare the image for better OCR results
        Like cleaning glasses before reading!
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image ready for OCR
        """
        print(f"🖼️  Loading image: {image_path}")
        
        # Read image using OpenCV
        image = cv2.imread(image_path)
        
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to grayscale (remove colors, easier to read)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding (make text darker, background lighter)
        # This is like increasing contrast to make text clearer
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Remove noise (clean up the image)
        denoised = cv2.medianBlur(threshold, 3)
        
        print("✅ Image preprocessed successfully!")
        return denoised
    
    def extract_text(self, image_path, preprocess=True):
        """
        Extract all text from an image
        
        Args:
            image_path: Path to the product image
            preprocess: Whether to clean the image first (default: True)
            
        Returns:
            Dictionary with extracted text and metadata
        """
        print(f"\n📖 Extracting text from: {os.path.basename(image_path)}")
        
        try:
            if preprocess:
                # Clean the image first
                processed_image = self.preprocess_image(image_path)
            else:
                # Use original image
                processed_image = cv2.imread(image_path)
            
            # Convert OpenCV format to PIL format (Tesseract needs PIL)
            pil_image = Image.fromarray(processed_image)
            
            # Extract text with Tesseract
            extracted_text = pytesseract.image_to_string(
                pil_image,
                lang=self.language,
                config=self.config
            )
            
            # Also get detailed data (text + position + confidence)
            detailed_data = pytesseract.image_to_data(
                pil_image,
                lang=self.language,
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Count words found
            word_count = len([w for w in extracted_text.split() if w.strip()])
            
            print(f"✅ Extracted {word_count} words!")
            
            return {
                'raw_text': extracted_text.strip(),
                'word_count': word_count,
                'detailed_data': detailed_data,
                'image_path': image_path,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error extracting text: {e}")
            return {
                'raw_text': '',
                'word_count': 0,
                'detailed_data': None,
                'image_path': image_path,
                'success': False,
                'error': str(e)
            }
    
    def extract_structured_text(self, image_path):
        """
        Extract text with position information
        Useful for knowing WHERE on the label each text appears
        
        Returns:
            List of text blocks with positions
        """
        result = self.extract_text(image_path, preprocess=True)
        
        if not result['success']:
            return []
        
        detailed = result['detailed_data']
        structured_blocks = []
        
        # Group text by lines
        n_boxes = len(detailed['text'])
        for i in range(n_boxes):
            # Filter out empty text
            if int(detailed['conf'][i]) > 0:  # conf = confidence score
                text = detailed['text'][i].strip()
                if text:
                    block = {
                        'text': text,
                        'x': detailed['left'][i],
                        'y': detailed['top'][i],
                        'width': detailed['width'][i],
                        'height': detailed['height'][i],
                        'confidence': float(detailed['conf'][i]) / 100.0  # Convert to 0-1 scale
                    }
                    structured_blocks.append(block)
        
        print(f"✅ Found {len(structured_blocks)} text blocks with positions")
        return structured_blocks
    
    def extract_from_multiple_images(self, image_folder):
        """
        Process multiple product images at once
        
        Args:
            image_folder: Folder containing product images
            
        Returns:
            Dictionary mapping filenames to extracted text
        """
        print(f"\n📁 Processing all images in: {image_folder}")
        
        results = {}
        
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = [
            f for f in os.listdir(image_folder)
            if os.path.splitext(f.lower())[1] in image_extensions
        ]
        
        print(f"Found {len(image_files)} images to process")
        
        for i, filename in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] Processing: {filename}")
            image_path = os.path.join(image_folder, filename)
            results[filename] = self.extract_text(image_path)
        
        print(f"\n✅ Processed {len(results)} images!")
        return results


# Test the OCR extractor
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTING OCR EXTRACTOR")
    print("=" * 60)
    
    extractor = OCRExtractor()
    
    print("\n✅ OCR Extractor is ready to use!")
    print("📝 To use it, you'll need to:")
    print("   1. Install Tesseract OCR")
    print("   2. Place product images in data/raw/")
    print("   3. Run the extraction!")