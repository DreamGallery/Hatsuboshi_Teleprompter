import sys
import cv2.typing
from src.config import (
    FONT_PATH as _FONT_PATH,
    font_size as _font_size,
    stroke_width as _stroke_width,
    kerning as _kerning,
    threshold as _threshold,
)
from src.frame_process import FrameProcess
from src.ass_events import AssEvents
from src.time_format import format_time
from src.text_match import draw_text, compare


def timeline_fix(
    event: AssEvents,
    image_list: list[tuple[str, cv2.typing.MatLike]],
    start_file_index: int,
    stream: FrameProcess,
) -> int:
    text = event.Text
    binary, mask = draw_text(text, _FONT_PATH, _font_size, _stroke_width, _kerning)
    for frame_pack in image_list[start_file_index:]:
        if compare(frame_pack[1], binary, _threshold, mask=mask):
            start_time = float(frame_pack[0][:-1])
            event.Start = format_time(start_time)
            break
        else:
            start_file_index = start_file_index + 1

    if start_file_index >= len(image_list):
        print("can't find subtitle text in target files, please check or adjust parameter")
        sys.exit(1)

    index_plus = int(event.Duration * stream.fps - 2)
    start_file_index = start_file_index + index_plus

    try:
        for frame_pack in image_list[start_file_index:]:
            if compare(frame_pack[1], binary, _threshold, mask=mask):
                start_file_index = start_file_index + 1
            else:
                end_time = float(frame_pack[0][:-1])
                event.End = format_time(end_time)
                break
    except IndexError:
        print(
            IndexError,
            "\nfile start index plus index convert by time duration exceeds the number of all files",
        )
        sys.exit(1)

    end_file_index = start_file_index
    return end_file_index
