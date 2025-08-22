"""OCR engines implementation with PaddleOCR and TrOCR."""

import io
import time
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from .config import settings
from .models import OCREngine, OCRRequest, OCRResponse, TextRegion


class BaseOCREngine:
    """Base class for OCR engines."""
    
    def __init__(self):
        """Initialize the OCR engine."""
        self.engine_name = "base"
        self.is_loaded = False
    
    def load_model(self) -> None:
        """Load the OCR model."""
        raise NotImplementedError
    
    def process_image(self, image: np.ndarray, request: OCRRequest) -> OCRResponse:
        """Process image and extract text."""
        raise NotImplementedError
    
    def get_info(self) -> Dict[str, Any]:
        """Get engine information."""
        return {
            "engine": self.engine_name,
            "loaded": self.is_loaded
        }


class PaddleOCREngine(BaseOCREngine):
    """PaddleOCR engine implementation."""
    
    def __init__(self):
        """Initialize PaddleOCR engine."""
        super().__init__()
        self.engine_name = "paddleocr"
        self.ocr = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load PaddleOCR model."""
        try:
            from paddleocr import PaddleOCR
            
            self.ocr = PaddleOCR(
                use_angle_cls=settings.paddle_use_angle_cls,
                lang=settings.paddle_lang,
                use_gpu=settings.paddle_use_gpu,
                use_space_char=settings.paddle_use_space_char,
                show_log=False
            )
            self.is_loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load PaddleOCR: {e}")
    
    def process_image(self, image: np.ndarray, request: OCRRequest) -> OCRResponse:
        """Process image with PaddleOCR."""
        if not self.is_loaded:
            raise RuntimeError("PaddleOCR model not loaded")
        
        start_time = time.time()
        
        try:
            # Run OCR
            results = self.ocr.ocr(image, cls=settings.paddle_use_angle_cls)
            
            # Process results
            regions = []
            all_text = []
            total_confidence = 0.0
            valid_regions = 0
            
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        bbox, (text, confidence) = line
                        
                        if confidence >= request.min_confidence:
                            region = TextRegion(
                                text=text,
                                confidence=confidence,
                                bbox=bbox,
                                word_count=len(text.split())
                            )
                            regions.append(region)
                            all_text.append(text)
                            total_confidence += confidence
                            valid_regions += 1
            
            # Combine text
            combined_text = " ".join(all_text)
            avg_confidence = total_confidence / valid_regions if valid_regions > 0 else 0.0
            
            # Count lines and words
            line_count = len(regions)
            word_count = sum(len(text.split()) for text in all_text)
            
            processing_time = time.time() - start_time
            
            return OCRResponse(
                text=combined_text,
                confidence=avg_confidence,
                regions=regions,
                word_count=word_count,
                line_count=line_count,
                processing_time=processing_time,
                engine_used=OCREngine.PADDLEOCR,
                language=request.language,
                image_dimensions=(image.shape[1], image.shape[0])
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            raise RuntimeError(f"PaddleOCR processing failed: {e}")


class TrOCREngine(BaseOCREngine):
    """TrOCR engine implementation for handwritten text."""
    
    def __init__(self):
        """Initialize TrOCR engine."""
        super().__init__()
        self.engine_name = "trocr"
        self.processor = None
        self.model = None
        self.load_model()
    
    def load_model(self) -> None:
        """Load TrOCR model."""
        try:
            from transformers import TrOCRProcessor, VisionEncoderDecoderModel
            
            self.processor = TrOCRProcessor.from_pretrained(settings.trocr_model)
            self.model = VisionEncoderDecoderModel.from_pretrained(settings.trocr_model)
            
            # Move to device if specified
            if settings.trocr_device != "cpu":
                import torch
                device = torch.device(settings.trocr_device)
                self.model.to(device)
            
            self.is_loaded = True
        except Exception as e:
            raise RuntimeError(f"Failed to load TrOCR: {e}")
    
    def process_image(self, image: np.ndarray, request: OCRRequest) -> OCRResponse:
        """Process image with TrOCR."""
        if not self.is_loaded:
            raise RuntimeError("TrOCR model not loaded")
        
        start_time = time.time()
        
        try:
            # Convert numpy array to PIL Image
            if len(image.shape) == 3:
                image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            else:
                image_pil = Image.fromarray(image)
            
            # Process with TrOCR
            pixel_values = self.processor(image_pil, return_tensors="pt").pixel_values
            
            if settings.trocr_device != "cpu":
                import torch
                device = torch.device(settings.trocr_device)
                pixel_values = pixel_values.to(device)
            
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            # Create single region for the entire image
            h, w = image.shape[:2]
            bbox = [[0, 0], [w, 0], [w, h], [0, h]]
            
            region = TextRegion(
                text=generated_text,
                confidence=0.8,  # TrOCR doesn't provide confidence scores
                bbox=bbox,
                word_count=len(generated_text.split())
            )
            
            processing_time = time.time() - start_time
            
            return OCRResponse(
                text=generated_text,
                confidence=0.8,
                regions=[region],
                word_count=len(generated_text.split()),
                line_count=1,
                processing_time=processing_time,
                engine_used=OCREngine.TROCR,
                language=request.language,
                image_dimensions=(w, h)
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            raise RuntimeError(f"TrOCR processing failed: {e}")


class MockOCREngine(BaseOCREngine):
    """Mock OCR engine for development and testing."""
    
    def __init__(self, engine_name: str):
        """Initialize mock OCR engine."""
        super().__init__()
        self.engine_name = engine_name
        self.is_loaded = True
    
    def load_model(self) -> None:
        """Mock model loading."""
        self.is_loaded = True
    
    def process_image(self, image: np.ndarray, request: OCRRequest) -> OCRResponse:
        """Mock image processing."""
        import time
        
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Mock text extraction
        mock_text = "This is mock OCR text extracted from the image. " \
                   "The actual OCR engines (PaddleOCR/TrOCR) are not installed. " \
                   "Install the required dependencies to enable real OCR processing."
        
        # Create mock region
        h, w = image.shape[:2]
        bbox = [[0, 0], [w, 0], [w, h], [0, h]]
        
        region = TextRegion(
            text=mock_text,
            confidence=0.95,
            bbox=bbox,
            word_count=len(mock_text.split())
        )
        
        processing_time = time.time() - start_time
        
        return OCRResponse(
            text=mock_text,
            confidence=0.95,
            regions=[region],
            word_count=len(mock_text.split()),
            line_count=1,
            processing_time=processing_time,
            engine_used=OCREngine.PADDLEOCR if self.engine_name == "paddleocr" else OCREngine.TROCR,
            language=request.language,
            image_dimensions=(w, h)
        )


class OCREngineManager:
    """Manages multiple OCR engines."""
    
    def __init__(self):
        """Initialize OCR engine manager."""
        self.engines: Dict[str, BaseOCREngine] = {}
        self._load_engines()
    
    def _load_engines(self) -> None:
        """Load available OCR engines."""
        try:
            # Load PaddleOCR
            paddle_engine = PaddleOCREngine()
            self.engines["paddleocr"] = paddle_engine
        except Exception as e:
            print(f"Failed to load PaddleOCR: {e}")
            # Add a mock engine for development
            mock_engine = MockOCREngine("paddleocr")
            self.engines["paddleocr"] = mock_engine
        
        try:
            # Load TrOCR
            trocr_engine = TrOCREngine()
            self.engines["trocr"] = trocr_engine
        except Exception as e:
            print(f"Failed to load TrOCR: {e}")
            # Add a mock engine for development
            mock_engine = MockOCREngine("trocr")
            self.engines["trocr"] = mock_engine
    
    def get_engine(self, engine_name: str) -> BaseOCREngine:
        """Get OCR engine by name."""
        if engine_name not in self.engines:
            raise ValueError(f"OCR engine '{engine_name}' not available")
        
        engine = self.engines[engine_name]
        if not engine.is_loaded:
            raise RuntimeError(f"OCR engine '{engine_name}' not loaded")
        
        return engine
    
    def get_available_engines(self) -> List[str]:
        """Get list of available engines."""
        return [name for name, engine in self.engines.items() if engine.is_loaded]
    
    def get_engines_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all engines."""
        return {name: engine.get_info() for name, engine in self.engines.items()}
    
    def process_image(self, image: np.ndarray, request: OCRRequest) -> OCRResponse:
        """Process image with specified engine."""
        engine = self.get_engine(request.engine.value)
        return engine.process_image(image, request)


# Global OCR engine manager
ocr_manager = OCREngineManager()
