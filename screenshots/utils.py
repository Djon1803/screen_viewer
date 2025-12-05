import threading
import time
from schemas import MonitorsOut, Monitor
import ctypes
import io
from PIL import Image, ImageDraw
from fastapi.responses import StreamingResponse
from mss import mss


class ScreenMssPIL:
    def __init__(self, monitor_id: int = 0, update_interval: float = 1.0):
        self.quality = 70
        self.monitor_id = monitor_id
        self.update_interval = update_interval  # время между обновлениями
        self._cache_lock = threading.Lock()
        self._cached_image: bytes = None  # кэш в виде JPEG байтов
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._update_cache_loop, daemon=True)
        self._thread.start()

    def get_monitors(self) -> MonitorsOut:
        _monitors: list = []
        with mss() as sct:
            _monitors = sct.monitors
        count = len(_monitors)
        monitors = [
            Monitor(id=i, width=mon["width"], height=mon["height"])
            for i, mon in enumerate(_monitors)
        ]
        return MonitorsOut(count=count, monitors=monitors)

    @staticmethod
    def _get_cursor_position():
        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return pt.x, pt.y

    @staticmethod
    def _draw_cursor(img: Image.Image, x: int, y: int, size: int = 15):
        draw = ImageDraw.Draw(img)
        triangle = [(x, y), (x + 5, y + size + 5), (x + size + 2, y + size // 2 + 5)]
        draw.polygon(triangle, fill="red", outline="white")

    def _update_cache_loop(self):
        """Фоновый поток, который обновляет кэш каждую секунду"""
        while not self._stop_event.is_set():
            with mss() as sct:
                count = len(sct.monitors)
                monitor_id = max(0, min(self.monitor_id, count - 1))
                monitor = sct.monitors[monitor_id]
                raw = sct.grab(monitor)

            img = Image.frombytes("RGB", raw.size, raw.rgb)

            cursor_x, cursor_y = self._get_cursor_position()
            cursor_x -= monitor["left"]
            cursor_y -= monitor["top"]

            if 0 <= cursor_x < monitor["width"] and 0 <= cursor_y < monitor["height"]:
                self._draw_cursor(img, cursor_x, cursor_y, size=15)

            quality = self.quality
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            buf.seek(0)

            # сохраняем в кэш
            with self._cache_lock:
                self._cached_image = buf.read()

            time.sleep(self.update_interval)

    def select_screen(self, monitor_id: int, quality: int):
        with mss() as sct:
            count = len(sct.monitors)

        monitor_id = max(0, min(monitor_id, count - 1))
        quality = max(5, min(quality, 100))

        self.monitor_id = monitor_id
        self.quality = quality

    def screenshot(self) -> StreamingResponse:
        """Отдаём последний кэшированный скриншот"""
        with self._cache_lock:
            if self._cached_image is None:
                # если кэш ещё пустой, ждём чуть-чуть и пробуем снова
                time.sleep(0.1)
            buf = io.BytesIO(self._cached_image)
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    def stop(self):
        """Остановить фоновый поток"""
        self._stop_event.set()
        self._thread.join()
