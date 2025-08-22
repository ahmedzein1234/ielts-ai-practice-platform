"""Image processing utilities for OCR service."""

import io
from typing import Tuple

import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from .config import settings


class ImageProcessor:
    """Image preprocessing for better OCR results."""
    
    @staticmethod
    def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
        """Load image from bytes."""
        try:
            # Convert bytes to PIL Image
            image_pil = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image_pil.mode != 'RGB':
                image_pil = image_pil.convert('RGB')
            
            # Convert to numpy array
            image_np = np.array(image_pil)
            
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            return image_bgr
            
        except Exception as e:
            raise ValueError(f"Failed to load image: {e}")
    
    @staticmethod
    def resize_image(image: np.ndarray, max_size: int = None) -> np.ndarray:
        """Resize image while maintaining aspect ratio."""
        if max_size is None:
            max_size = settings.max_image_size
        
        h, w = image.shape[:2]
        
        # Check if resizing is needed
        if max(h, w) <= max_size:
            return image
        
        # Calculate new dimensions
        if h > w:
            new_h = max_size
            new_w = int(w * (max_size / h))
        else:
            new_w = max_size
            new_h = int(h * (max_size / w))
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized
    
    @staticmethod
    def enhance_image(image: np.ndarray) -> np.ndarray:
        """Enhance image for better OCR results."""
        try:
            # Convert to PIL for enhancement
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_pil = Image.fromarray(image_rgb)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image_pil)
            image_pil = enhancer.enhance(1.2)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image_pil)
            image_pil = enhancer.enhance(1.1)
            
            # Apply slight blur to reduce noise
            image_pil = image_pil.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Convert back to numpy array
            image_np = np.array(image_pil)
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            
            return image_bgr
            
        except Exception:
            # Return original image if enhancement fails
            return image
    
    @staticmethod
    def preprocess_for_ocr(image: np.ndarray, engine: str = "paddleocr") -> np.ndarray:
        """Preprocess image specifically for OCR."""
        try:
            # Resize if too large
            processed = ImageProcessor.resize_image(image)
            
            # Different preprocessing for different engines
            if engine == "paddleocr":
                # PaddleOCR works well with enhanced images
                processed = ImageProcessor.enhance_image(processed)
                
            elif engine == "trocr":
                # TrOCR might work better with less preprocessing
                # Just ensure it's not too large
                pass
            
            return processed
            
        except Exception:
            # Return original image if preprocessing fails
            return image
    
    @staticmethod
    def get_image_info(image: np.ndarray) -> dict:
        """Get image information."""
        h, w = image.shape[:2]
        channels = image.shape[2] if len(image.shape) == 3 else 1
        
        return {
            "width": w,
            "height": h,
            "channels": channels,
            "size": image.size,
            "dtype": str(image.dtype)
        }
    
    @staticmethod
    def validate_image(image_bytes: bytes) -> Tuple[bool, str]:
        """Validate image file."""
        try:
            # Check file size
            if len(image_bytes) > settings.max_file_size:
                return False, f"File too large: {len(image_bytes)} bytes (max: {settings.max_file_size})"
            
            # Try to load image
            image_pil = Image.open(io.BytesIO(image_bytes))
            
            # Check format
            format_lower = image_pil.format.lower() if image_pil.format else "unknown"
            supported_lower = [fmt.lower() for fmt in settings.supported_formats]
            
            if image_pil.format and format_lower not in supported_lower:
                return False, f"Unsupported format: {image_pil.format} (supported: {settings.supported_formats})"
            
            # Check dimensions
            w, h = image_pil.size
            if max(w, h) > settings.max_image_size * 2:  # Allow some headroom
                return False, f"Image too large: {w}x{h} (max: {settings.max_image_size})"
            
            # Check if image has content
            if w < 10 or h < 10:
                return False, f"Image too small: {w}x{h}"
            
            return True, "Valid image"
            
        except Exception as e:
            return False, f"Invalid image: {e}"
    
    @staticmethod
    def extract_text_regions(image: np.ndarray) -> list:
        """Extract potential text regions from image."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to get binary image
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by area and aspect ratio
            text_regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = w * h
                aspect_ratio = w / h if h > 0 else 0
                
                # Filter based on size and aspect ratio
                if area > 100 and 0.1 < aspect_ratio < 10:
                    text_regions.append((x, y, w, h))
            
            return text_regions
            
        except Exception:
            return []
