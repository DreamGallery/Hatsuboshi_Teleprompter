import re
import sys
import json
from src.config import (
    player as _player,
    TXT_PATH as _TXT_PATH,
)


def adv_subtitle(adv_line: str) -> dict:
    content = re.sub(r"<.*?>", "", adv_line[1:-1]).split(" ")
    category_key = content.pop(0)
    new_content = []
    for item in content:
        if "=" in item:
            new_content.append(item)
        else:
            new_content[-1] = f"{new_content[-1]} {item}"
    data = {}
    for item in new_content:
        key = item.split("=")[0]
        if key == "clip":
            value = json.loads(item.split("=")[1].replace("\\", ""))
        else:
            value = item.split("=")[1]
        data[key] = value
    adv_subtitle_line = {category_key: data}
    return adv_subtitle_line


def get_category(adv_line: str) -> str:
    content = adv_line[1:-1]
    category = content.split().pop(0)
    return category


def get_clip(adv_line: str) -> dict:
    adv_subtitle_line = adv_subtitle(adv_line)
    category = get_category(adv_line)
    clip_data = adv_subtitle_line.get(category, {}).get("clip", {})
    if not clip_data:
        print("unable to access the clip data.")
        sys.exit(1)
    return clip_data


def get_name(adv_line: str) -> str:
    subtitle_line = adv_subtitle(adv_line)
    category = get_category(adv_line)
    name = subtitle_line.get(category, {}).get("name", "")
    if name == "{user}":
        name = _player
    return name


def get_text(adv_line: str) -> str:
    subtitle_line = adv_subtitle(adv_line)
    category = get_category(adv_line)
    text = subtitle_line.get(category, {}).get("text", "")
    if "{user}" in text:
        text = text.replace("{user}", _player)
    return text


def extract(filename: str) -> list[str]:
    adv_text_list: list[str] = []
    with open(f"{_TXT_PATH}/{filename}", "r", encoding="utf8") as fp:
        for line in fp:
            if "message" in line or "narration" in line:
                adv_text_list.append(line.strip())
    adv_text_list.sort(key=lambda x: float(get_clip(x).get("_startTime")))
    return adv_text_list
