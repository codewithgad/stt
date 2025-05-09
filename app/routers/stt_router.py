# app/api/routers/stt_router.py
from fastapi import APIRouter, WebSocket
from app.services.stt_service import transcribe_audio

router = APIRouter()

@router.websocket("/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await transcribe_audio(websocket)
