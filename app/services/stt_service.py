# app/services/stt_service.py
import os
import tempfile
import whisper
import wave
import queue
import pyaudio
from fastapi import WebSocket

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
RECORD_SECONDS = 5  # Duration per transcription chunk

class MicrophoneRecorder:
    def __init__(self, rate=SAMPLE_RATE, chunk_size=CHUNK_SIZE):
        self.rate = rate
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16
        self.channels = 1
        self.frames = []
        self.p = pyaudio.PyAudio()

    def record(self, seconds):
        stream = self.p.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
        )
        frames = []
        for _ in range(0, int(self.rate / self.chunk_size * seconds)):
            data = stream.read(self.chunk_size)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        return frames

    def terminate(self):
        self.p.terminate()

async def transcribe_audio(websocket: WebSocket):
    await websocket.accept()
    recorder = MicrophoneRecorder()
    model = whisper.load_model("base")  # or "tiny", "small", etc.

    try:
        while True:
            frames = recorder.record(RECORD_SECONDS)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                wf = wave.open(f.name, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(recorder.p.get_sample_size(pyaudio.paInt16))
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(b''.join(frames))
                wf.close()

                result = model.transcribe(f.name)
                await websocket.send_text(result["text"])
                os.unlink(f.name)
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        recorder.terminate()
        await websocket.close()
