import json
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.auth.jwt import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/reports/{report_id}/stream")
async def verification_stream(websocket: WebSocket, report_id: str, token: str = Query(None)):
    """
    WebSocket endpoint for real-time claim verification updates.
    Auth via query param ?token=... (WS headers are unreliable in browsers).
    """
    # 1. Validate token
    if not token:
        await websocket.close(code=4001, reason="Authentication required")
        return

    user_id = decode_access_token(token)
    if not user_id:
        await websocket.close(code=4001, reason="Invalid token")
        return

    # 2. Accept connection
    await websocket.accept()
    logger.info(f"WebSocket connected: report={report_id}, user={user_id}")

    try:
        # 3. Subscribe to Redis pub/sub channel
        from redis.asyncio import from_url
        from app.config import settings
        
        redis = from_url(settings.REDIS_URL)
        pubsub = redis.pubsub()
        channel = f"report:{report_id}"
        await pubsub.subscribe(channel)
        logger.info(f"Subscribed to {channel}")

        async def listen_to_redis():
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        data = message["data"].decode("utf-8")
                        await websocket.send_text(data)
                        logger.info(f"Sent WS message: {data[:50]}...")
            except Exception as e:
                logger.error(f"Redis listen error: {e}")

        # Task for listening to Redis
        redis_task = asyncio.create_task(listen_to_redis())

        # Keep connection open and handle client-side disconnects or pings
        while True:
            try:
                # We don't expect text from client, but receiving text is how we detect closure
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json({"type": "ping"})
            except WebSocketDisconnect:
                break
        
        redis_task.cancel()
        await pubsub.unsubscribe(channel)
        await redis.close()

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: report={report_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({"type": "error", "code": "WORKER_FAILED", "message": str(e)})
    finally:
        logger.info(f"WebSocket cleanup: report={report_id}")
