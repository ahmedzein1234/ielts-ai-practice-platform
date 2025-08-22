"""Speech-to-Text service using faster-whisper."""

import base64
import io
import time
from typing import Any, Dict, List, Optional

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from .config import settings
from .models import STTRequest, STTResponse


class STTService:
    """Speech-to-Text service using faster-whisper."""
    
    def __init__(self):
        """Initialize the STT service."""
        self.model: Optional[WhisperModel] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the Whisper model."""
        try:
            self.model = WhisperModel(
                model_size_or_path=settings.whisper_model,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type,
                download_root="./models"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def _decode_audio(self, audio_data: bytes, sample_rate: int) -> np.ndarray:
        """Decode audio data to numpy array."""
        try:
            # Try to read as various audio formats
            audio_io = io.BytesIO(audio_data)
            
            # Try soundfile first
            try:
                audio, sr = sf.read(audio_io)
                if sr != sample_rate:
                    # Resample if needed (simplified - in production use librosa)
                    audio = self._resample_audio(audio, sr, sample_rate)
                return audio.astype(np.float32)
            except Exception:
                pass
            
            # Try librosa as fallback
            try:
                import librosa
                audio_io.seek(0)
                audio, sr = librosa.load(audio_io, sr=sample_rate)
                return audio.astype(np.float32)
            except Exception:
                pass
            
            raise ValueError("Unsupported audio format")
            
        except Exception as e:
            raise ValueError(f"Failed to decode audio: {e}")
    
    def _resample_audio(self, audio: np.ndarray, src_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate."""
        if src_sr == target_sr:
            return audio
        
        try:
            import librosa
            return librosa.resample(audio, orig_sr=src_sr, target_sr=target_sr)
        except ImportError:
            # Simple resampling (not recommended for production)
            ratio = target_sr / src_sr
            new_length = int(len(audio) * ratio)
            return np.interp(
                np.linspace(0, len(audio), new_length),
                np.arange(len(audio)),
                audio
            )
    
    def _base64_to_audio(self, base64_data: str) -> bytes:
        """Convert base64 string to audio bytes."""
        try:
            return base64.b64decode(base64_data)
        except Exception as e:
            raise ValueError(f"Invalid base64 audio data: {e}")
    
    def transcribe(self, request: STTRequest) -> STTResponse:
        """Transcribe audio data."""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        start_time = time.time()
        
        try:
            # Decode audio
            audio = self._decode_audio(request.audio_data, request.sample_rate)
            
            # Prepare transcription options
            options = {
                "language": request.language,
                "task": request.task,
                "beam_size": 5,
                "best_of": 5,
                "patience": 1,
                "length_penalty": 1.0,
                "repetition_penalty": 1.0,
                "no_speech_threshold": 0.6,
                "log_prob_threshold": -1.0,
                "compression_ratio_threshold": 2.4,
                "condition_on_previous_text": True,
                "initial_prompt": None,
                "word_timestamps": True,
            }
            
            # Remove None values
            options = {k: v for k, v in options.items() if v is not None}
            
            # Transcribe
            segments, info = self.model.transcribe(audio, **options)
            
            # Process results
            text = " ".join([segment.text for segment in segments])
            confidence = np.mean([segment.avg_logprob for segment in segments]) if segments else 0.0
            
            # Convert confidence from log probability to 0-1 scale
            confidence = max(0.0, min(1.0, (confidence + 1.0) / 2.0))
            
            # Prepare segments
            segment_data = []
            for segment in segments:
                segment_data.append({
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "avg_logprob": segment.avg_logprob,
                    "no_speech_prob": segment.no_speech_prob,
                    "words": [
                        {
                            "start": word.start,
                            "end": word.end,
                            "word": word.word,
                            "probability": word.probability
                        }
                        for word in segment.words
                    ] if hasattr(segment, 'words') and segment.words else []
                })
            
            processing_time = time.time() - start_time
            
            return STTResponse(
                text=text,
                confidence=confidence,
                language=info.language,
                segments=segment_data,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            raise RuntimeError(f"Transcription failed: {e}")
    
    def transcribe_base64(self, base64_audio: str, sample_rate: int = 16000, 
                         language: Optional[str] = None) -> STTResponse:
        """Transcribe base64 encoded audio."""
        audio_data = self._base64_to_audio(base64_audio)
        request = STTRequest(
            audio_data=audio_data,
            sample_rate=sample_rate,
            language=language
        )
        return self.transcribe(request)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information."""
        if not self.model:
            return {"status": "not_loaded"}
        
        return {
            "model_size": settings.whisper_model,
            "device": settings.whisper_device,
            "compute_type": settings.whisper_compute_type,
            "status": "loaded"
        }


# Global STT service instance
stt_service = STTService()
