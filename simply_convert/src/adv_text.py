import json
from src.read_ini import config


_TXT_PATH = config.get("File Path", "TXT_PATH")
_player_name = config.get("Info", "player_name")
_KEY_MASSAGE = config.get("Text Key", "KEY_MASSAGE")
_KEY_CLIP = config.get("Text Key", "KEY_CLIP")
_KEY_NAME = config.get("Text Key", "KEY_NAME")
_KEY_NARRATION = config.get("Text Key", "KEY_NARRATION")
_KEY_TITLE = config.get("Text Key", "KEY_TITLE")
_KEY_CHOICE = config.get("Text Key", "KEY_CHOICE")


def extract(filename: str) -> list[str]:
    dial_list: list[str] = []
    with open(f"{_TXT_PATH}/{filename}", "r", encoding="utf8") as f:
        for line in f:
            if "text" in line:
                dial_list.append(line)
    dial_list.sort(key=lambda x: float(get_clip(x)["_startTime"]))
    return dial_list


def get_text(content: str) -> str:
    if _KEY_MASSAGE in content:
        text = (
            content[1:-2]
            .split(_KEY_MASSAGE)[1]
            .split(f"\u0020{_KEY_NAME}")[0]
            .replace("{user}", _player_name)
        )
    elif _KEY_NARRATION in content:
        text = content[1:-2].split(_KEY_NARRATION)[1].split(f"\u0020{_KEY_CLIP}")[0]
    elif _KEY_CHOICE in content:
        text = content[1:-2].split(f"{_KEY_CHOICE}\u0020")[1].split(f"\u0020{_KEY_CLIP}")[0]
    return text


def get_name(content: str) -> str:
    if _KEY_CHOICE in content:
        name = _player_name
    else:
        name = content[1:-2].split(f"\u0020{_KEY_NAME}")[1].split(f"\u0020{_KEY_CLIP}")[0].split("\u0020")[0]
    return name


def get_clip(content: str):
    clip = content[1:-2].split(f"\u0020{_KEY_CLIP}")[1].replace("\\", "")
    data = json.loads(clip)
    return data


def to_time(clip_time: float) -> str:
    H = clip_time // 3600
    M = (clip_time - H * 3600) // 60
    S = clip_time - H * 3600 - M * 60
    format_time = "%d:%02d:%05.2f" % (H, M, S)
    return format_time


def end_time(startTime: float, duration: float) -> str:
    end_ = startTime + duration
    endTime = to_time(end_)
    return endTime
