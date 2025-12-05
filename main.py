import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from screenshots.router import router as screenshot_router


app = FastAPI(title="Screen-Viewer", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(screenshot_router)

parser = argparse.ArgumentParser()
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()

if __name__ == "__main__":
    import uvicorn
    from main import app  # прямой импорт

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=args.port,
        log_config=None,  # отключаем встроенный логгер uvicorn
        access_log=False,
    )
