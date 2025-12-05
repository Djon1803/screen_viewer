from fastapi.responses import StreamingResponse
from src.schemas import MonitorsOut, Monitor


from mss import mss
from PIL import Image
import io


class Screen:
    """Базовый класс интерфейса экрана"""

    def monitors(self) -> MonitorsOut:
        """Возвращает список мониторов"""
        raise NotImplementedError

    def screenshot(self, number_monitor: int) -> StreamingResponse:
        """Возвращает кадр выбранного монитора"""
        raise NotImplementedError


class ScreenMssPIL(Screen):
    def monitors(self) -> MonitorsOut:
        _monitors: list = []
        with mss() as sct:
            _monitors = sct.monitors

        count = len(_monitors)
        monitors = []
        id = 0
        for _monitor in _monitors:
            monitor = Monitor(id=id, width=_monitor["width"], height=_monitor["height"])
            monitors.append(monitor)
            id += 1
        return MonitorsOut(count=count, monitors=monitors)

    def screenshot(self, number_monitor: int) -> StreamingResponse:
        with mss() as sct:
            count = len(sct.monitors)

            if number_monitor < 0:
                number_monitor = 0
            elif number_monitor >= count:
                number_monitor = count - 1

            monitor = sct.monitors[number_monitor]
            raw = sct.grab(monitor)

            # создаём PNG через Pillow
            img = Image.frombytes("RGB", raw.size, raw.rgb)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()
            return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")


import cv2
import numpy as np


class ScreenMssJPEG(Screen):
    """Экран с MSS + OpenCV для оптимального JPEG"""

    def monitors(self) -> MonitorsOut:
        """Получаем список мониторов"""
        monitors_list = []
        with mss() as sct:
            _monitors = sct.monitors
            for idx, mon in enumerate(_monitors):
                monitor = Monitor(id=idx, width=mon["width"], height=mon["height"])
                monitors_list.append(monitor)
        return MonitorsOut(count=len(monitors_list), monitors=monitors_list)

    def screenshot(self, number_monitor: int) -> StreamingResponse:
        """Делаем скриншот и возвращаем JPEG"""
        with mss() as sct:
            monitors_count = len(sct.monitors)
            # Ограничиваем номер монитора
            number_monitor = max(0, min(number_monitor, monitors_count - 1))
            monitor = sct.monitors[number_monitor]
            raw = sct.grab(monitor)

            # MSS отдаёт BGRA → BGR для OpenCV
            frame = np.array(raw)[:, :, :3]

            # Сжимаем в JPEG (качество 70)
            ret, jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            buf = io.BytesIO(jpeg.tobytes())
            buf.seek(0)

            return StreamingResponse(buf, media_type="image/jpeg")


class ScreenMssGen(Screen):
    """Экран с MSS + OpenCV для MJPEG потока"""

    def monitors(self) -> MonitorsOut:
        monitors_list = []
        with mss() as sct:
            for idx, mon in enumerate(sct.monitors):
                monitor = Monitor(id=idx, width=mon["width"], height=mon["height"])
                monitors_list.append(monitor)
        return MonitorsOut(count=len(monitors_list), monitors=monitors_list)

    def mjpeg_generator(self, monitor_id: int):
        with mss() as sct:
            monitor = sct.monitors[monitor_id]
            while True:
                frame = np.array(sct.grab(monitor))[:, :, :3]  # BGR
                ret, jpeg = cv2.imencode(
                    ".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                )
                if not ret:
                    continue
                # формируем кадр MJPEG
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpeg.tobytes() + b"\r\n"

    def screenshot(self, monitor_id: int) -> StreamingResponse:
        """Возвращает поток MJPEG"""
        return StreamingResponse(
            self.mjpeg_generator(monitor_id),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )


import dxcam


class ScreenDxcam(Screen):
    """Захват экрана через DXcam (DirectX Desktop Duplication API) — быстрый и лёгкий"""

    def __init__(self):
        # один DXCamera на экземпляр — по умолчанию захват основного монитора
        self.camera = dxcam.create()

    def monitors(self) -> MonitorsOut:
        # DXcam не даёт напрямую список мониторов, но можно обойти:
        # Получить список выходов/устройств через dxcam.output_info() или device_info()
        # Но для простоты — вернём 1 монитор (твой основной)
        mon = (
            self.camera.get_current_output()
            if hasattr(self.camera, "get_current_output")
            else None
        )
        # Если нужно — можно расширить через dxcam.output_info()
        return (
            MonitorsOut(count=1, monitors=[Monitor(id=0, width=mon[0], height=mon[1])])
            if mon
            else MonitorsOut(count=1, monitors=[Monitor(id=0, width=0, height=0)])
        )

    def screenshot(self, number_monitor: int) -> StreamingResponse:
        # DXcam захватывает RGB-кадр как numpy array
        frame = self.camera.grab()
        if frame is None:
            # если кадр не обновился — можно вернуть ошибку или предыдущий кадр
            return StreamingResponse(
                io.BytesIO(b""), media_type="application/octet-stream"
            )

        # Опционально: сжать в JPEG, чтобы меньше трафика
        # frame — numpy.ndarray с shape (H, W, 3), dtype=uint8, format RGB

        # Конвертируем RGB -> BGR для OpenCV, если нужно
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # Кодируем в JPEG
        ret, jpeg = cv2.imencode(".jpg", frame_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if not ret:
            # fallback: отдаём сырое RGB
            buf = io.BytesIO(frame.tobytes())
            return StreamingResponse(buf, media_type="application/octet-stream")

        buf = io.BytesIO(jpeg.tobytes())
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/jpeg")
