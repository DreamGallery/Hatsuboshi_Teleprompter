import os
from src.adv_text import *
from src.events import AssEvents
from src.gakuen_parser import parse_messages
from src.read_ini import config
from src.ass_part import script_info, garbage, style, event


ASS_PATH = config.get("File Path", "ASS_PATH")
TXT_PATH = config.get("File Path", "TXT_PATH")


def generate_ass(filename: str):
    content = script_info + "\n" + garbage + "\n" + style + "\n" + event
    with open(f"{TXT_PATH}/{filename}", "r", encoding="utf8") as f:
        gakuen_txt = f.read()
        parsed_lines = parse_messages(gakuen_txt)
    try:
        for line in parsed_lines:
            if line["__tag__"] in ["message", "narration", "choicegroup"]:
                dial_event = AssEvents()
                dial_event.from_dialogue(line)
                content = (
                    content
                    + f"{dial_event.echo_dialogue()}"
                    + "\n"
                    + f"{dial_event.echo_comment()}"
                    + "\n"
                )
        with open(
            f"{ASS_PATH}/{os.path.splitext(filename)[0]}.ass", "w", encoding="utf8"
        ) as fp:
            fp.write(content)
        print(
            f"{filename} has been successfully converted to {os.path.splitext(filename)[0]}.ass"
        )
    except Exception as e:
        print(f"{filename} convert failed. Info: {e}")

    return


if __name__ == "__main__":
    for filepath, dirnames, filenames in os.walk(TXT_PATH):
        for filename in filenames:
            if not filename.endswith(".txt") or not filename.startswith("adv_"):
                continue
            generate_ass(filename)
