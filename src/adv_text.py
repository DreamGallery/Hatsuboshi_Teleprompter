import json
from src.read_ini import config


_player_name = config.get("Info", "player_name")


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


def get_clip_data(parsed_line: str) -> dict:
    clip_data = json.loads(parsed_line.get("clip", {}).replace("\\", ""))
    return clip_data


def get_name(parsed_line: str) -> str:
    name = ""
    if parsed_line.get("__tag__") == "choicegroup":
        name = _player_name
    elif parsed_line.get("__tag__") == "message":
        name = parsed_line.get("name", "")
    return name


def get_text(parsed_line: str) -> str:
    text = ""
    if parsed_line.get("__tag__") == "choicegroup":
        if isinstance(parsed_line.get("choices", {}), list):
            for index, choice in enumerate(parsed_line.get("choices", [])):
                text += f"Choice{index+1}: {choice.get('text', '')}\u0020"
        elif isinstance(parsed_line.get("choices", {}), dict):
            text += f"Choice: {parsed_line.get('choices', {}).get('text', '')}"
    elif parsed_line.get("__tag__") == "message":
        text = parsed_line.get("text", "")
    return text
