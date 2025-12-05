from fastapi.responses import StreamingResponse
from screenshots.utils import ScreenMssPIL


from schemas import MonitorsOut, SelectOut

screen = ScreenMssPIL()


class ScreenshotService:
    async def get_monitors(self) -> MonitorsOut:
        return screen.get_monitors()

    async def select_screen(self, monitor_id: int, quality: int) -> SelectOut:
        screen.select_screen(monitor_id=monitor_id, quality=quality)
        return SelectOut(ok=True)

    async def get_screenshot(self) -> StreamingResponse:
        return screen.screenshot()
