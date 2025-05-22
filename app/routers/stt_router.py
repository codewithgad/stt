import os
import ffmpeg
import whisper
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
import numpy as np
import tempfile

router = APIRouter()

model = whisper.load_model("medium") 

async def convert_webm_to_wav(webm_data: bytes) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
        webm_file.write(webm_data)
        webm_path = webm_file.name
    
    wav_path = webm_path.replace(".webm", ".wav")
    
    try:
        (
            ffmpeg
            .input(webm_path)
            .output(wav_path, ac=1, ar=16000)
            .overwrite_output()
            .run(quiet=True)
        )
        
        with open(wav_path, "rb") as wav_file:
            wav_data = wav_file.read()
        
        return wav_data
    finally:
        if os.path.exists(webm_path):
            os.unlink(webm_path)
        if os.path.exists(wav_path):
            os.unlink(wav_path)

@router.websocket("/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_bytes()
            
            wav_data = await convert_webm_to_wav(data)
            
            with tempfile.NamedTemporaryFile(suffix=".wav") as temp_audio:
                temp_audio.write(wav_data)
                temp_audio.flush()
                
                result = model.transcribe(temp_audio.name, fp16=False)
                transcript = result["text"]
            
            await websocket.send_text(transcript)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in transcription: {e}")
        await websocket.close(code=1011, reason=str(e))