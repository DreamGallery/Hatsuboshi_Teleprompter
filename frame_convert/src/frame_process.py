import cv2, cv2.typing
import sys
import threading
from src.config import VIDEO_PATH as _VIDEO_PATH
from src.text_match import to_binary_adaptive
from concurrent.futures import ThreadPoolExecutor, wait


_lock = threading.Lock()
_current_count = 0


class FrameProcess(object):
    fps: float

    def one_task(
        self,
        image_list: list[tuple[str, cv2.typing.MatLike]],
        frame: cv2.typing.MatLike,
        width: int,
        height: int,
        milliseconds: float,
        total_fps: int,
    ) -> None:
        global _current_count
        seconds = "%.4f" % (milliseconds // 1000 + (milliseconds % 1000) / 1000)
        name = seconds[:-1]
        # Modify the following content if your resolution ratio is not 16:9
        img = frame[
            (height * 7 // 9) : (height * 8 // 9),
            (width * 1 // 16) : (width * 15 // 16),
        ]
        binary = to_binary_adaptive(img, 11, 0)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        binary_opn = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        _lock.acquire()
        image_list.append((name, binary_opn))
        _current_count += 1
        percent = round(_current_count / total_fps * 100)
        print(
            f"\rPre-Progress:({_current_count}/{total_fps})" + "{}%: ".format(percent),
            "▮" * (percent // 2),
            end="",
        )
        sys.stdout.flush()
        _lock.release()

    def to_frame(self, filename: str) -> list[tuple[str, cv2.typing.MatLike]]:
        image_list: list[tuple[str, cv2.typing.MatLike]] = []
        video_path = f"{_VIDEO_PATH}/{filename}"
        vc = cv2.VideoCapture(video_path)
        self.fps = vc.get(cv2.CAP_PROP_FPS)
        width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_fps = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        executor = ThreadPoolExecutor(max_workers=20)
        frame_tasks = []
        while vc.isOpened():
            status, frame = vc.read()
            if not status:
                break
            milliseconds = vc.get(cv2.CAP_PROP_POS_MSEC)
            frame_tasks.append(
                executor.submit(self.one_task, image_list, frame, width, height, milliseconds, total_fps)
            )
        vc.release()
        wait(frame_tasks, return_when="ALL_COMPLETED")
        print("\u0020", "Pre-Progress finished")
        return image_list
