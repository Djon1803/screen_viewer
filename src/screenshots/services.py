from fastapi.responses import StreamingResponse
import io
from src.screenshots.utils import ScreenMssPIL, ScreenMssJPEG, ScreenMssGen, ScreenDxcam
from src.schemas import MonitorsOut, Monitor

screen = ScreenDxcam()


class ScreenshotService:
    async def get_monitors(self) -> MonitorsOut:
        return screen.monitors()

    async def get_screenshot(self, number_monitor: int) -> StreamingResponse:
        return screen.screenshot(number_monitor)
