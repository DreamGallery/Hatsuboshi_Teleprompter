import os
from src.ass_format import (
    script_info,
    garbage,
    style,
    event,
)
from src.config import (
    ASS_PATH,
    adv_file,
    video,
)
from src.adv_text import *
from src.timeline_fix import timeline_fix
from src.ass_events import AssEvents
from src.frame_process import FrameProcess

stream = FrameProcess()
image_list = stream.to_frame(video)

dial_list = extract(adv_file)

current_count = 0
start_file_index = 0
content = script_info + "\n" + garbage + "\n" + style + "\n" + event
print("ASS-Generate-Progress start")

image_list.sort(key=lambda x: float(x[0]))

for dial in dial_list:
    dial_event = AssEvents()
    dial_event.from_dialogue(dial)
    next_file_index = timeline_fix(dial_event, image_list, start_file_index, stream)
    start_file_index = next_file_index
    content = content + f"{dial_event.echo_dialogue()}" + "\n" + f"{dial_event.echo_comment()}" + "\n"
    current_count = current_count + 1
    percent = round(current_count / len(dial_list) * 100)
    print(
        f"ASS-Generate-Progress:({'{:0>3d}'.format(current_count)}/{'{:0>3d}'.format(len(dial_list))})"
        + "{:>3d}%: ".format(percent),
        "▮" * (percent // 2),
        end="",
    )
    print("\u0020", dial_event.Text, dial_event.Start, dial_event.End)

try:
    title, ext = os.path.splitext(video)
    with open(f"{ASS_PATH}/{title}.ass", "w", encoding="utf8") as fp:
        fp.write(content)
    print(f"{adv_file} has been successfully converted to {title}.ass")
except Exception as e:
    print(f"\n{title} convert failed. Info: {e}")
