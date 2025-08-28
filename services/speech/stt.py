"""Speech-to-Text service using faster-whisper."""

import base64
import io
import time
from typing import Any, Dict, List, Optional

import numpy as np
import soundfile as sf
from faster_whisper import WhisperModel

from .config import settings
from .models import STTRequest, STTResponse, SpeechAnalysisRequest, SpeechAnalysisResponse
from .enhanced_analysis import EnhancedSpeechAnalyzer


class STTService:
    """Speech-to-Text service using faster-whisper."""
    
    def __init__(self):
        """Initialize the STT service."""
        self.model: Optional[WhisperModel] = None
        self.enhanced_analyzer = EnhancedSpeechAnalyzer()
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
                    "no_speech_prob": segment.no_speech_prob
                })
            
            processing_time = time.time() - start_time
            
            return STTResponse(
                text=text,
                confidence=confidence,
                language=info.language,
                processing_time=processing_time,
                segments=segment_data
            )
            
        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")
    
    def transcribe_base64(self, base64_data: str, sample_rate: int = 16000, language: Optional[str] = None) -> STTResponse:
        """Transcribe base64 encoded audio data."""
        try:
            audio_data = self._base64_to_audio(base64_data)
            request = STTRequest(
                audio_data=audio_data,
                sample_rate=sample_rate,
                language=language or "en"
            )
            return self.transcribe(request)
        except Exception as e:
            raise RuntimeError(f"Base64 transcription failed: {e}")
    
    def analyze_speech(self, request: SpeechAnalysisRequest) -> SpeechAnalysisResponse:
        """Perform comprehensive speech analysis including transcription and enhanced analysis."""
        if not self.model:
            raise RuntimeError("Whisper model not loaded")
        
        start_time = time.time()
        
        try:
            # First, transcribe the audio
            stt_response = self.transcribe(STTRequest(
                audio_data=request.audio_data,
                sample_rate=request.sample_rate,
                language=request.language
            ))
            
            # Decode audio for analysis
            audio = self._decode_audio(request.audio_data, request.sample_rate)
            duration = len(audio) / request.sample_rate
            
            # Perform enhanced analysis
            pronunciation = None
            fluency = None
            accent = None
            
            if request.include_pronunciation:
                pronunciation = self.enhanced_analyzer.analyze_pronunciation(
                    audio, stt_response.text, request.sample_rate
                )
            
            if request.include_fluency:
                fluency = self.enhanced_analyzer.analyze_fluency(
                    audio, stt_response.text, duration
                )
            
            if request.include_accent:
                accent = self.enhanced_analyzer.analyze_accent(
                    audio, stt_response.text
                )
            
            # Calculate overall score
            overall_score = 6.0
            band_level = "Band 6"
            detailed_feedback = []
            
            if pronunciation and fluency and accent:
                overall_score, band_level = self.enhanced_analyzer.calculate_overall_score(
                    pronunciation, fluency, accent
                )
                detailed_feedback = self.enhanced_analyzer.generate_detailed_feedback(
                    pronunciation, fluency, accent
                )
            
            # Create enhanced response
            from .models import EnhancedSTTResponse
            enhanced_response = EnhancedSTTResponse(
                text=stt_response.text,
                confidence=stt_response.confidence,
                language=stt_response.language,
                processing_time=stt_response.processing_time,
                segments=stt_response.segments,
                pronunciation=pronunciation,
                fluency=fluency,
                accent=accent,
                overall_score=overall_score,
                band_level=band_level,
                detailed_feedback=detailed_feedback
            )
            
            # Generate recommendations and practice suggestions
            recommendations = self._generate_recommendations(
                pronunciation, fluency, accent, request.target_band
            )
            practice_suggestions = self._generate_practice_suggestions(
                pronunciation, fluency, accent
            )
            
            return SpeechAnalysisResponse(
                transcription=stt_response,
                analysis=enhanced_response,
                recommendations=recommendations,
                practice_suggestions=practice_suggestions
            )
            
        except Exception as e:
            raise RuntimeError(f"Speech analysis failed: {e}")
    
    def _generate_recommendations(
        self, 
        pronunciation, 
        fluency, 
        accent, 
        target_band: Optional[float]
    ) -> List[str]:
        """Generate improvement recommendations based on analysis."""
        recommendations = []
        
        if target_band:
            recommendations.append(f"Target IELTS Band: {target_band}")
        
        if pronunciation and pronunciation.overall_score < 7.0:
            recommendations.append("Focus on pronunciation improvement")
        
        if fluency and fluency.words_per_minute < 120:
            recommendations.append("Practice speaking at natural pace")
        
        if fluency and fluency.filler_frequency > 3:
            recommendations.append("Work on reducing filler words")
        
        if accent and accent.comprehensibility < 0.8:
            recommendations.append("Improve accent comprehensibility")
        
        if not recommendations:
            recommendations.append("Continue practicing to maintain current level")
        
        return recommendations[:5]
    
    def _generate_practice_suggestions(
        self, 
        pronunciation, 
        fluency, 
        accent
    ) -> List[str]:
        """Generate specific practice suggestions."""
        suggestions = []
        
        if pronunciation:
            suggestions.append("Practice minimal pairs for better pronunciation")
            suggestions.append("Record yourself and compare with native speakers")
        
        if fluency:
            suggestions.append("Practice speaking without pauses")
            suggestions.append("Use tongue twisters to improve fluency")
        
        if accent:
            suggestions.append("Listen to native speakers and mimic their patterns")
            suggestions.append("Practice stress and intonation patterns")
        
        suggestions.append("Join conversation groups for regular practice")
        suggestions.append("Use the AI tutor for personalized feedback")
        
        return suggestions[:5]


# Global STT service instance
stt_service = STTService()
