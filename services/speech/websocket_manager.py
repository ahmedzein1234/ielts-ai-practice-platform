"""WebSocket connection manager for Speech Service."""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set

import structlog
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from .config import settings
from .models import (
    AudioChunkMessage, AudioFormat, ConnectMessage, DisconnectMessage,
    ErrorMessage, MessageType, PingMessage, PongMessage, SessionInfo,
    TranscriptionMessage, WebSocketMessage
)
from .stt import stt_service

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections and sessions."""
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, SessionInfo] = {}
        self.user_sessions: Dict[str, Set[str]] = {}  # user_id -> set of session_ids
        self.connection_count = 0
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        session_id = str(uuid.uuid4())
        self.active_connections[session_id] = websocket
        self.connection_count += 1
        
        logger.info(
            "WebSocket connected",
            session_id=session_id,
            connection_count=self.connection_count
        )
        
        return session_id
    
    def disconnect(self, session_id: str) -> None:
        """Remove a WebSocket connection."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            self.connection_count -= 1
            
            # Clean up session info
            if session_id in self.sessions:
                session = self.sessions[session_id]
                if session.user_id and session.user_id in self.user_sessions:
                    self.user_sessions[session.user_id].discard(session_id)
                    if not self.user_sessions[session.user_id]:
                        del self.user_sessions[session.user_id]
                del self.sessions[session_id]
            
            logger.info(
                "WebSocket disconnected",
                session_id=session_id,
                connection_count=self.connection_count
            )
    
    async def send_message(self, session_id: str, message: WebSocketMessage) -> bool:
        """Send a message to a specific connection."""
        if session_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[session_id]
            await websocket.send_text(message.model_dump_json())
            return True
        except Exception as e:
            logger.error(
                "Failed to send message",
                session_id=session_id,
                error=str(e)
            )
            return False
    
    async def send_error(self, session_id: str, error_code: str, 
                        error_message: str, details: Optional[Dict] = None) -> None:
        """Send an error message to a connection."""
        error_msg = ErrorMessage(
            session_id=session_id,
            error_code=error_code,
            error_message=error_message,
            details=details
        )
        await self.send_message(session_id, error_msg)
    
    async def broadcast(self, message: WebSocketMessage, 
                       exclude_session: Optional[str] = None) -> None:
        """Broadcast a message to all connections."""
        for session_id in list(self.active_connections.keys()):
            if session_id != exclude_session:
                await self.send_message(session_id, message)
    
    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information."""
        return self.sessions.get(session_id)
    
    def update_session_activity(self, session_id: str) -> None:
        """Update session last activity timestamp."""
        if session_id in self.sessions:
            self.sessions[session_id].last_activity = datetime.utcnow()
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """Get all sessions for a user."""
        return list(self.user_sessions.get(user_id, set()))
    
    def get_connection_stats(self) -> Dict:
        """Get connection statistics."""
        return {
            "active_connections": self.connection_count,
            "active_sessions": len(self.sessions),
            "unique_users": len(self.user_sessions)
        }


class WebSocketHandler:
    """Handles WebSocket message processing."""
    
    def __init__(self, manager: ConnectionManager):
        """Initialize the WebSocket handler."""
        self.manager = manager
        self.logger = structlog.get_logger()
    
    async def handle_websocket(self, websocket: WebSocket) -> None:
        """Handle a WebSocket connection."""
        session_id = await self.manager.connect(websocket)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_text()
                
                try:
                    # Parse message
                    message_data = json.loads(data)
                    message_type = message_data.get("type")
                    
                    if not message_type:
                        await self.manager.send_error(
                            session_id, "INVALID_MESSAGE", "Missing message type"
                        )
                        continue
                    
                    # Handle different message types
                    if message_type == MessageType.CONNECT:
                        await self._handle_connect(session_id, message_data)
                    elif message_type == MessageType.AUDIO_CHUNK:
                        await self._handle_audio_chunk(session_id, message_data)
                    elif message_type == MessageType.PING:
                        await self._handle_ping(session_id, message_data)
                    elif message_type == MessageType.DISCONNECT:
                        await self._handle_disconnect(session_id, message_data)
                        break
                    else:
                        await self.manager.send_error(
                            session_id, "UNKNOWN_MESSAGE_TYPE", 
                            f"Unknown message type: {message_type}"
                        )
                
                except json.JSONDecodeError:
                    await self.manager.send_error(
                        session_id, "INVALID_JSON", "Invalid JSON format"
                    )
                except ValidationError as e:
                    await self.manager.send_error(
                        session_id, "VALIDATION_ERROR", 
                        f"Message validation failed: {str(e)}"
                    )
                except Exception as e:
                    self.logger.error(
                        "Error processing message",
                        session_id=session_id,
                        error=str(e)
                    )
                    await self.manager.send_error(
                        session_id, "INTERNAL_ERROR", 
                        "Internal server error"
                    )
        
        except WebSocketDisconnect:
            self.logger.info("WebSocket disconnected", session_id=session_id)
        except Exception as e:
            self.logger.error(
                "WebSocket error",
                session_id=session_id,
                error=str(e)
            )
        finally:
            self.manager.disconnect(session_id)
    
    async def _handle_connect(self, session_id: str, message_data: Dict) -> None:
        """Handle connection message."""
        try:
            connect_msg = ConnectMessage(**message_data)
            
            # Create session info
            session_info = SessionInfo(
                session_id=session_id,
                user_id=connect_msg.user_id,
                question_id=connect_msg.question_id,
                connected_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                audio_format=connect_msg.audio_format,
                sample_rate=connect_msg.sample_rate,
                language=connect_msg.language
            )
            
            self.manager.sessions[session_id] = session_info
            
            # Track user sessions
            if connect_msg.user_id:
                if connect_msg.user_id not in self.manager.user_sessions:
                    self.manager.user_sessions[connect_msg.user_id] = set()
                self.manager.user_sessions[connect_msg.user_id].add(session_id)
            
            self.logger.info(
                "Session connected",
                session_id=session_id,
                user_id=connect_msg.user_id,
                question_id=connect_msg.question_id,
                audio_format=connect_msg.audio_format.value,
                sample_rate=connect_msg.sample_rate
            )
            
            # Send confirmation
            await self.manager.send_message(session_id, connect_msg)
            
        except Exception as e:
            await self.manager.send_error(
                session_id, "CONNECT_ERROR", f"Failed to establish session: {str(e)}"
            )
    
    async def _handle_audio_chunk(self, session_id: str, message_data: Dict) -> None:
        """Handle audio chunk message."""
        try:
            audio_msg = AudioChunkMessage(**message_data)
            
            # Update session activity
            self.manager.update_session_activity(session_id)
            
            # Get session info
            session_info = self.manager.get_session_info(session_id)
            if not session_info:
                await self.manager.send_error(
                    session_id, "NO_SESSION", "No active session found"
                )
                return
            
            # Update session stats
            session_info.total_chunks += 1
            
            # Process audio with STT
            try:
                response = stt_service.transcribe_base64(
                    audio_msg.audio_data,
                    sample_rate=session_info.sample_rate,
                    language=session_info.language
                )
                
                # Create transcription message
                transcription_msg = TranscriptionMessage(
                    session_id=session_id,
                    user_id=session_info.user_id,
                    text=response.text,
                    confidence=response.confidence,
                    start_time=0.0,  # Will be calculated from segments
                    end_time=response.segments[-1]["end"] if response.segments else 0.0,
                    is_final=audio_msg.is_final,
                    language=response.language,
                    segments=response.segments
                )
                
                # Send transcription result
                await self.manager.send_message(session_id, transcription_msg)
                
                self.logger.info(
                    "Audio processed",
                    session_id=session_id,
                    chunk_index=audio_msg.chunk_index,
                    text_length=len(response.text),
                    confidence=response.confidence,
                    processing_time=response.processing_time
                )
                
            except Exception as e:
                await self.manager.send_error(
                    session_id, "STT_ERROR", f"Speech recognition failed: {str(e)}"
                )
            
        except Exception as e:
            await self.manager.send_error(
                session_id, "AUDIO_ERROR", f"Failed to process audio: {str(e)}"
            )
    
    async def _handle_ping(self, session_id: str, message_data: Dict) -> None:
        """Handle ping message."""
        try:
            ping_msg = PingMessage(**message_data)
            pong_msg = PongMessage(
                session_id=session_id,
                user_id=ping_msg.user_id
            )
            await self.manager.send_message(session_id, pong_msg)
            
        except Exception as e:
            await self.manager.send_error(
                session_id, "PING_ERROR", f"Failed to respond to ping: {str(e)}"
            )
    
    async def _handle_disconnect(self, session_id: str, message_data: Dict) -> None:
        """Handle disconnect message."""
        try:
            disconnect_msg = DisconnectMessage(**message_data)
            self.logger.info(
                "Session disconnecting",
                session_id=session_id,
                reason=disconnect_msg.reason
            )
            
        except Exception as e:
            self.logger.error(
                "Error handling disconnect",
                session_id=session_id,
                error=str(e)
            )


# Global instances
connection_manager = ConnectionManager()
websocket_handler = WebSocketHandler(connection_manager)
