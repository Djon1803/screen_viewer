import sys
import os

from fastapi import APIRouter, Query
from fastapi.responses import FileResponse

from screenshots.services import ScreenshotService
from schemas import MonitorsOut, SelectOut

router = APIRouter(prefix="", tags=["Shots"])

service = ScreenshotService()


def resource_path(relative_path):
    """Получить путь к ресурсу при упаковке в exe"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


@router.get(
    "/",
    description="Передача файла страницы",
    response_class=FileResponse,
)
async def screenshot():
    index_file = resource_path("index.html")
    return FileResponse(index_file, media_type="text/html")


@router.get(
    "/monitors",
    description="Получение кол-во мониторов",
    response_model=MonitorsOut,
)
async def screenshot():
    return await service.get_monitors()


@router.post(
    "/select_screen",
    description="Выбор монитора и качества",
    response_model=SelectOut,
)
async def select_screen(
    monitor_id: int = Query(...),
    quality: int = Query(...),
):
    return await service.select_screen(monitor_id=monitor_id, quality=quality)


@router.get(
    "/screenshot",
    description="Получение скрина монитора",
)
async def screenshot():
    return await service.get_screenshot()
