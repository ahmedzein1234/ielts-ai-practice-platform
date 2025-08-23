from fastapi import WebSocket
from typing import Dict, List, Optional
import structlog
import json
import asyncio

logger = structlog.get_logger()

class WebSocketManager:
    """Manages WebSocket connections for real-time tutoring"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Connect a new WebSocket client"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info("WebSocket connected", user_id=user_id)
        
        # Send welcome message
        await self.send_message(user_id, {
            "type": "connection_established",
            "data": {
                "message": "Connected to AI Tutor",
                "user_id": user_id,
                "timestamp": asyncio.get_event_loop().time()
            }
        })
    
    def disconnect(self, user_id: str):
        """Disconnect a WebSocket client"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]
        
        logger.info("WebSocket disconnected", user_id=user_id)
    
    async def disconnect_all(self):
        """Disconnect all WebSocket clients"""
        for user_id in list(self.active_connections.keys()):
            await self.disconnect(user_id)
        
        logger.info("All WebSocket connections closed")
    
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
    
    async def send_tutor_response(self, user_id: str, response: dict):
        """Send a tutor response to a user"""
        message = {
            "type": "tutor_response",
            "data": response,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(user_id, message)
    
    async def send_recommendations(self, user_id: str, recommendations: list):
        """Send recommendations to a user"""
        message = {
            "type": "recommendations",
            "data": recommendations,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(user_id, message)
    
    async def send_learning_path(self, user_id: str, learning_path: dict):
        """Send learning path to a user"""
        message = {
            "type": "learning_path",
            "data": learning_path,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(user_id, message)
    
    async def send_progress_update(self, user_id: str, progress: dict):
        """Send progress update to a user"""
        message = {
            "type": "progress_update",
            "data": progress,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(user_id, message)
    
    async def send_notification(self, user_id: str, notification: dict):
        """Send a notification to a user"""
        message = {
            "type": "notification",
            "data": notification,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_message(user_id, message)
    
    def set_user_session(self, user_id: str, session_id: str):
        """Set the session ID for a user"""
        self.user_sessions[user_id] = session_id
        logger.debug("User session set", user_id=user_id, session_id=session_id)
    
    def get_user_session(self, user_id: str) -> Optional[str]:
        """Get the session ID for a user"""
        return self.user_sessions.get(user_id)
    
    async def handle_message(self, user_id: str, message: dict):
        """Handle incoming WebSocket message"""
        try:
            message_type = message.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await self.send_message(user_id, {
                    "type": "pong",
                    "data": {"timestamp": asyncio.get_event_loop().time()}
                })
            
            elif message_type == "chat":
                # Handle chat message (will be processed by main.py)
                logger.debug("Chat message received", user_id=user_id, message_length=len(message.get("message", "")))
            
            elif message_type == "get_recommendations":
                # Handle recommendation request (will be processed by main.py)
                logger.debug("Recommendation request received", user_id=user_id)
            
            elif message_type == "get_learning_path":
                # Handle learning path request (will be processed by main.py)
                logger.debug("Learning path request received", user_id=user_id)
            
            elif message_type == "session_start":
                # Handle session start
                session_id = message.get("session_id")
                if session_id:
                    self.set_user_session(user_id, session_id)
                    await self.send_message(user_id, {
                        "type": "session_started",
                        "data": {"session_id": session_id}
                    })
            
            elif message_type == "session_end":
                # Handle session end
                session_id = self.get_user_session(user_id)
                if session_id:
                    await self.send_message(user_id, {
                        "type": "session_ended",
                        "data": {"session_id": session_id}
                    })
                    del self.user_sessions[user_id]
            
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
