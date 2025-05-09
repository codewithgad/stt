from fastapi import FastAPI
from app.routers import stt_router

app = FastAPI()
app.include_router(stt_router.router, prefix="/stt")

@app.get("/")
async def root():
    return {"message": "Welcome to the STT API!"}
