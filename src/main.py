import os, sys

sys.path.insert(1, os.path.join(sys.path[0], ".."))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn
from src.config import settings
from src.screenshots.router import router as screenshot_router

# Папка для скриншотов
os.makedirs("shots", exist_ok=True)

app = FastAPI(title="Screen-Viewer", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(screenshot_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
    )
