from fastapi import WebSocket
from typing import Dict, List, Optional, Any
import structlog
import json
import asyncio
import base64
import io
from datetime import datetime
import numpy as np

logger = structlog.get_logger()

class EnhancedWebSocketManager:
    """Enhanced WebSocket manager for multi-modal AI tutoring"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.user_contexts: Dict[str, Dict[str, Any]] = {}  # user_id -> context
        self.audio_buffers: Dict[str, List[bytes]] = {}  # user_id -> audio_chunks
        self.speech_analyzers: Dict[str, Any] = {}  # user_id -> speech_analyzer
        self.typing_indicators: Dict[str, bool] = {}  # user_id -> is_typing
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_contexts[user_id] = {
            "personality": {
                "teaching_style": "conversational",
                "interaction_mode": "multi-modal",
                "difficulty_level": "intermediate",
                "feedback_style": "constructive",
                "pace": "moderate"
            },
            "session_start": datetime.utcnow(),
            "message_count": 0,
            "last_activity": datetime.utcnow(),
            "preferences": {},
            "learning_goals": []
        }
        self.audio_buffers[user_id] = []
        self.typing_indicators[user_id] = False
        
        logger.info("Enhanced WebSocket connected", user_id=user_id)
        
        # Send welcome message with enhanced capabilities
        await self.send_message(user_id, {
            "type": "connection_established",
            "data": {
                "message": "Connected to Enhanced AI Tutor",
                "user_id": user_id,
                "capabilities": [
                    "text_chat",
                    "voice_interaction", 
                    "speech_analysis",
                    "multi_modal_responses",
                    "real_time_feedback",
                    "adaptive_learning",
                    "progress_tracking"
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        })
    
    def disconnect(self, user_id: str):
        """Disconnect a WebSocket client"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
            
        if user_id in self.user_contexts:
            del self.user_contexts[user_id]
            
        if user_id in self.audio_buffers:
            del self.audio_buffers[user_id]
            
        if user_id in self.speech_analyzers:
            del self.speech_analyzers[user_id]
            
        if user_id in self.typing_indicators:
            del self.typing_indicators[user_id]
        
        logger.info("Enhanced WebSocket disconnected", user_id=user_id)
    
    async def disconnect_all(self):
        """Disconnect all WebSocket clients"""
        for user_id in list(self.active_connections.keys()):
            self.disconnect(user_id)
        
        logger.info("All enhanced WebSocket connections closed")
    
    async def send_message(self, user_id: str, message: dict):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
                logger.debug("Message sent", user_id=user_id, message_type=message.get("type"))
            except Exception as e:
                logger.error("Failed to send message", user_id=user_id, error=str(e))
                await self.disconnect(user_id)
    
    async def broadcast_message(self, message: dict, exclude_user: Optional[str] = None):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            if user_id != exclude_user:
                await self.send_message(user_id, message)
    
    def get_connected_users(self) -> List[str]:
        """Get list of connected user IDs"""
        return list(self.active_connections.keys())
    
    def is_connected(self, user_id: str) -> bool:
        """Check if a user is connected"""
        return user_id in self.active_connections
    
    async def send_multi_modal_response(self, user_id: str, response: dict):
        """Send a multi-modal tutor response"""
        message = {
            "type": "tutor_response",
            "data": {
                **response,
                "context": self.user_contexts.get(user_id, {}),
                "session_info": {
                    "session_id": self.user_sessions.get(user_id),
                    "message_count": self.user_contexts.get(user_id, {}).get("message_count", 0)
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_speech_analysis(self, user_id: str, analysis: dict):
        """Send speech analysis results"""
        message = {
            "type": "speech_analysis",
            "data": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_progress_insight(self, user_id: str, insight: dict):
        """Send progress insights"""
        message = {
            "type": "progress_insight",
            "data": insight,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_audio_response(self, user_id: str, audio_data: bytes, audio_format: str = "wav"):
        """Send audio response"""
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        message = {
            "type": "audio_response",
            "data": {
                "audio": audio_base64,
                "format": audio_format,
                "duration": len(audio_data) / 16000  # Approximate duration
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_interactive_exercise(self, user_id: str, exercise: dict):
        """Send interactive exercise"""
        message = {
            "type": "interactive_exercise",
            "data": exercise,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_adaptive_feedback(self, user_id: str, feedback: dict):
        """Send adaptive feedback"""
        message = {
            "type": "adaptive_feedback",
            "data": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_typing_indicator(self, user_id: str, is_typing: bool):
        """Send typing indicator"""
        message = {
            "type": "typing_indicator",
            "data": {"is_typing": is_typing},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    async def send_connection_status(self, user_id: str, status: str):
        """Send connection status update"""
        message = {
            "type": "connection_status",
            "data": {"status": status},
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_message(user_id, message)
    
    def update_user_context(self, user_id: str, context_updates: Dict[str, Any]):
        """Update user context"""
        if user_id in self.user_contexts:
            self.user_contexts[user_id].update(context_updates)
            self.user_contexts[user_id]["last_activity"] = datetime.utcnow()
            logger.debug("User context updated", user_id=user_id, updates=context_updates)
    
    def increment_message_count(self, user_id: str):
        """Increment message count for user"""
        if user_id in self.user_contexts:
            self.user_contexts[user_id]["message_count"] += 1
    
    async def process_audio_chunk(self, user_id: str, audio_chunk: bytes):
        """Process incoming audio chunk"""
        if user_id in self.audio_buffers:
            self.audio_buffers[user_id].append(audio_chunk)
            
            # Analyze audio level
            audio_level = self.analyze_audio_level(audio_chunk)
            
            # Send audio level update
            await self.send_message(user_id, {
                "type": "audio_level",
                "data": {"level": audio_level},
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def analyze_audio_level(self, audio_chunk: bytes) -> float:
        """Analyze audio level from chunk"""
        try:
            # Convert bytes to numpy array (assuming 16-bit PCM)
            audio_array = np.frombuffer(audio_chunk, dtype=np.int16)
            if len(audio_array) > 0:
                # Calculate RMS (Root Mean Square) for audio level
                rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                # Normalize to 0-100 range
                level = min(100.0, (rms / 32768.0) * 100.0)
                return float(level)
        except Exception as e:
            logger.error("Error analyzing audio level", error=str(e))
        
        return 0.0
    
    async def handle_message(self, user_id: str, message: dict):
        """Handle incoming WebSocket message with enhanced capabilities"""
        try:
            message_type = message.get("type")
            self.increment_message_count(user_id)
            
            if message_type == "ping":
                # Respond to ping with pong
                await self.send_message(user_id, {
                    "type": "pong",
                    "data": {"timestamp": datetime.utcnow().isoformat()}
                })
            
            elif message_type == "user_message":
                # Handle text message
                await self.handle_text_message(user_id, message)
            
            elif message_type == "audio_message":
                # Handle audio message
                await self.handle_audio_message(user_id, message)
            
            elif message_type == "voice_start":
                # Handle voice recording start
                await self.handle_voice_start(user_id, message)
            
            elif message_type == "voice_stop":
                # Handle voice recording stop
                await self.handle_voice_stop(user_id, message)
            
            elif message_type == "typing_start":
                # Handle typing start
                self.typing_indicators[user_id] = True
                await self.broadcast_typing_indicator(user_id, True)
            
            elif message_type == "typing_stop":
                # Handle typing stop
                self.typing_indicators[user_id] = False
                await self.broadcast_typing_indicator(user_id, False)
            
            elif message_type == "personality_update":
                # Handle personality update
                await self.handle_personality_update(user_id, message)
            
            elif message_type == "session_start":
                # Handle session start
                session_id = message.get("session_id")
                if session_id:
                    self.user_sessions[user_id] = session_id
                    await self.send_message(user_id, {
                        "type": "session_started",
                        "data": {"session_id": session_id}
                    })
            
            elif message_type == "session_end":
                # Handle session end
                session_id = self.user_sessions.get(user_id)
                if session_id:
                    await self.send_message(user_id, {
                        "type": "session_ended",
                        "data": {"session_id": session_id}
                    })
                    del self.user_sessions[user_id]
            
            elif message_type == "get_recommendations":
                # Handle recommendation request
                await self.handle_recommendation_request(user_id, message)
            
            elif message_type == "get_learning_path":
                # Handle learning path request
                await self.handle_learning_path_request(user_id, message)
            
            else:
                logger.warning("Unknown message type", user_id=user_id, message_type=message_type)
                await self.send_message(user_id, {
                    "type": "error",
                    "data": {"message": "Unknown message type"}
                })
                
        except Exception as e:
            logger.error("Error handling message", user_id=user_id, error=str(e))
            await self.send_message(user_id, {
                "type": "error",
                "data": {"message": "Failed to process message"}
            })
    
    async def handle_text_message(self, user_id: str, message: dict):
        """Handle text message from user"""
        text = message.get("message", "")
        personality = message.get("personality", {})
        
        # Update user context
        self.update_user_context(user_id, {
            "last_message": text,
            "personality": personality
        })
        
        logger.debug("Text message received", user_id=user_id, message_length=len(text))
        
        # This will be processed by the main application logic
        # The response will be sent via send_multi_modal_response
    
    async def handle_audio_message(self, user_id: str, message: dict):
        """Handle audio message from user"""
        audio_data = message.get("audio_data")
        if audio_data:
            # Decode base64 audio data
            try:
                audio_bytes = base64.b64decode(audio_data)
                await self.process_audio_chunk(user_id, audio_bytes)
                
                # Store in buffer for processing
                if user_id in self.audio_buffers:
                    self.audio_buffers[user_id].append(audio_bytes)
                
                logger.debug("Audio message received", user_id=user_id, audio_size=len(audio_bytes))
                
            except Exception as e:
                logger.error("Error processing audio data", user_id=user_id, error=str(e))
    
    async def handle_voice_start(self, user_id: str, message: dict):
        """Handle voice recording start"""
        self.audio_buffers[user_id] = []
        await self.send_message(user_id, {
            "type": "voice_started",
            "data": {"message": "Voice recording started"},
            "timestamp": datetime.utcnow().isoformat()
        })
        logger.info("Voice recording started", user_id=user_id)
    
    async def handle_voice_stop(self, user_id: str, message: dict):
        """Handle voice recording stop"""
        if user_id in self.audio_buffers:
            # Process complete audio buffer
            complete_audio = b''.join(self.audio_buffers[user_id])
            
            # Send for speech analysis
            await self.send_message(user_id, {
                "type": "voice_processing",
                "data": {"message": "Processing voice input..."},
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Clear buffer
            self.audio_buffers[user_id] = []
            
            logger.info("Voice recording stopped", user_id=user_id, audio_size=len(complete_audio))
    
    async def handle_personality_update(self, user_id: str, message: dict):
        """Handle personality update"""
        personality = message.get("personality", {})
        self.update_user_context(user_id, {"personality": personality})
        
        await self.send_message(user_id, {
            "type": "personality_updated",
            "data": {"personality": personality},
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info("Personality updated", user_id=user_id, personality=personality)
    
    async def handle_recommendation_request(self, user_id: str, message: dict):
        """Handle recommendation request"""
        logger.debug("Recommendation request received", user_id=user_id)
        # This will be processed by the main application logic
    
    async def handle_learning_path_request(self, user_id: str, message: dict):
        """Handle learning path request"""
        logger.debug("Learning path request received", user_id=user_id)
        # This will be processed by the main application logic
    
    async def broadcast_typing_indicator(self, user_id: str, is_typing: bool):
        """Broadcast typing indicator to other users"""
        await self.broadcast_message({
            "type": "user_typing",
            "data": {"user_id": user_id, "is_typing": is_typing},
            "timestamp": datetime.utcnow().isoformat()
        }, exclude_user=user_id)
    
    def get_user_context(self, user_id: str) -> Dict[str, Any]:
        """Get user context"""
        return self.user_contexts.get(user_id, {})
    
    def get_session_info(self, user_id: str) -> Dict[str, Any]:
        """Get session information for user"""
        context = self.user_contexts.get(user_id, {})
        return {
            "session_id": self.user_sessions.get(user_id),
            "message_count": context.get("message_count", 0),
            "session_start": context.get("session_start"),
            "last_activity": context.get("last_activity"),
            "personality": context.get("personality", {})
        }

# Backward compatibility
WebSocketManager = EnhancedWebSocketManager
