import sys
import json
from src.read_ini import config


_COMMON_CATEGORY = ["message", "narration"]
_TXT_PATH = config.get("File Path", "TXT_PATH")
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


def adv_common(adv_line: str):
    content = adv_line[1:-1].split(" ")
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
    adv_common_line_dict = {category_key: data}
    return adv_common_line_dict


def adv_choice(adv_line: str):
    def _adv_choice_split(adv_line: str):
        content = adv_line[1:-1].split(" ")
        category_key = content.pop(0)
        new_content = []
        for index, item in enumerate(content):
            if not item.startswith("[") and item.endswith("]"):
                new_content.pop()
                new_content.append(f"{content[index-1]} {item}")
            else:
                new_content.append(item)
        return category_key, new_content

    category_key, new_content = _adv_choice_split(adv_line)
    data = {}
    for item in new_content:
        key = item.split("=", 1)[0]
        if key == "clip":
            value = json.loads(item.split("=")[1].replace("\\", ""))
        else:
            value = item.split("=", 1)[1:]
            if value[0].startswith("[") and value[0].endswith("]"):
                temp_category_key, temp_new_content = _adv_choice_split(value[0])
                value = [
                    {
                        temp_category_key: {
                            temp_new_content[0].split("=")[0]: temp_new_content[0].split("=")[1]
                        }
                    }
                ]
            if key in data.keys():
                data[key].extend(value)
                continue
        data[key] = value
    adv_choice_line_dict = {category_key: data}
    return adv_choice_line_dict


def get_clip(adv_line: str) -> dict:
    clip_data = {}
    if "choicegroup" in adv_line:
        adv_line_dict = adv_choice(adv_line)
        clip_data = adv_line_dict.get("choicegroup", {}).get("clip", {})
    else:
        adv_line_dict = adv_common(adv_line)
        for category_key in _COMMON_CATEGORY:
            if category_key in adv_line_dict.keys():
                clip_data = adv_line_dict.get(category_key, {}).get("clip", {})
    if not clip_data:
        print("unable to access the clip data.")
        sys.exit(1)
    return clip_data


def extract(filename: str) -> list[str]:
    adv_text_list: list[str] = []
    with open(f"{_TXT_PATH}/{filename}", "r", encoding="utf8") as f:
        for line in f:
            if "text" in line:
                adv_text_list.append(line.strip())
    adv_text_list.sort(key=lambda x: float(get_clip(x).get("_startTime")))
    return adv_text_list


def get_name(adv_line: str) -> str:
    name = ""
    if "choicegroup" in adv_line:
        name = _player_name
    else:
        adv_line_dict = adv_common(adv_line)
        for category_key in _COMMON_CATEGORY:
            if category_key in adv_line_dict.keys():
                name = adv_line_dict.get(category_key, {}).get("name", "")
    return name


def get_text(adv_line: str) -> str:
    text = ""
    if "choicegroup" in adv_line:
        adv_line_dict = adv_choice(adv_line)
        choice_list = adv_line_dict.get("choicegroup", {}).get("choices")
        for index, choice in enumerate(choice_list):
            text += f"Choice{index+1}: {choice.get('choice',{}).get('text', '')} "
    else:
        adv_line_dict = adv_common(adv_line)
        for category_key in _COMMON_CATEGORY:
            if category_key in adv_line_dict.keys():
                text = adv_line_dict.get(category_key, {}).get("text", "")
    return text
