from fastapi import APIRouter
from fastapi.responses import StreamingResponse, FileResponse

from src.screenshots.services import ScreenshotService
from src.schemas import MonitorsOut

router = APIRouter(prefix="", tags=["Shots"])

service = ScreenshotService()


@router.get("/", description="Передача файла страницы", response_class=FileResponse)
async def screenshot():
    index = "./src/index.html"
    return FileResponse(index, media_type="text/html")


@router.get(
    "/monitors",
    description="Получение кол-во мониторов",
    response_model=MonitorsOut,
)
async def screenshot():
    return await service.get_monitors()


@router.get(
    "/screenshot/{number_monitor}",
    description="Получение скрина монитора",
)
async def screenshot(number_monitor: int):
    return await service.get_screenshot(number_monitor)
