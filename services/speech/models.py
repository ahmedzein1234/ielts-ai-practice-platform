"""Pydantic models for Speech Service."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """WebSocket message types."""
    
    CONNECT = "connect"
    AUDIO_CHUNK = "audio_chunk"
    TRANSCRIPTION = "transcription"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"
    DISCONNECT = "disconnect"


class AudioFormat(str, Enum):
    """Supported audio formats."""
    
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    OGG = "ogg"
    M4A = "m4a"


class WebSocketMessage(BaseModel):
    """Base WebSocket message model."""
    
    type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ConnectMessage(WebSocketMessage):
    """Connection message."""
    
    type: MessageType = MessageType.CONNECT
    audio_format: AudioFormat = AudioFormat.WAV
    sample_rate: int = 16000
    language: Optional[str] = None
    question_id: Optional[str] = None


class AudioChunkMessage(WebSocketMessage):
    """Audio chunk message."""
    
    type: MessageType = MessageType.AUDIO_CHUNK
    chunk_index: int
    audio_data: str  # Base64 encoded audio
    is_final: bool = False


class TranscriptionMessage(WebSocketMessage):
    """Transcription result message."""
    
    type: MessageType = MessageType.TRANSCRIPTION
    text: str
    confidence: float = Field(ge=0.0, le=1.0)
    start_time: float
    end_time: float
    is_final: bool = False
    language: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None


class ErrorMessage(WebSocketMessage):
    """Error message."""
    
    type: MessageType = MessageType.ERROR
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None


class PingMessage(WebSocketMessage):
    """Ping message."""
    
    type: MessageType = MessageType.PING


class PongMessage(WebSocketMessage):
    """Pong message."""
    
    type: MessageType = MessageType.PONG


class DisconnectMessage(WebSocketMessage):
    """Disconnect message."""
    
    type: MessageType = MessageType.DISCONNECT
    reason: Optional[str] = None


class STTRequest(BaseModel):
    """STT processing request."""
    
    audio_data: bytes
    sample_rate: int = 16000
    language: Optional[str] = None
    task: str = "transcribe"  # transcribe or translate


class STTResponse(BaseModel):
    """STT processing response."""
    
    text: str
    confidence: float
    language: Optional[str] = None
    segments: List[Dict[str, Any]]
    processing_time: float


class SessionInfo(BaseModel):
    """WebSocket session information."""
    
    session_id: str
    user_id: Optional[str] = None
    question_id: Optional[str] = None
    connected_at: datetime
    last_activity: datetime
    audio_format: AudioFormat
    sample_rate: int
    language: Optional[str] = None
    total_chunks: int = 0
    total_duration: float = 0.0
