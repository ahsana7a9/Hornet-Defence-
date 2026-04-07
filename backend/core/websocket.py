import logging

logger = logging.getLogger(__name__)

try:
    import socketio
    sio = socketio.AsyncServer(cors_allowed_origins="*")
    logger.info("[WebSocket] Socket.IO server initialized")
except ImportError:
    logger.warning("[WebSocket] python-socketio not installed — WebSocket disabled")
    sio = None
