import os
from src.adv_text import *
from src.events import AssEvents
from src.read_ini import config
from src.ass_part import script_info, garbage, style, event


ASS_PATH = config.get("File Path", "ASS_PATH")
TXT_PATH = config.get("File Path", "TXT_PATH")


def generate_ass(filename: str):
    content = script_info + "\n" + garbage + "\n" + style + "\n" + event
    for dial in extract(filename):
        dial_event = AssEvents()
        dial_event.from_dialogue(dial)
        content = content + f"{dial_event.echo_dialogue()}" + "\n" + f"{dial_event.echo_comment()}" + "\n"
    try:
        with open(f"{ASS_PATH}/{os.path.splitext(filename)[0]}.ass", "w", encoding="utf8") as fp:
            fp.write(content)
        print(f"{filename} has been successfully converted to {os.path.splitext(filename)[0]}.ass")
    except Exception as e:
        print(f"{filename} convert failed. Info: {e}")
        return


def extract_txt(filename: str):
    content = ""
    for dial in extract(filename):
        dial_event = AssEvents()
        dial_event.from_dialogue(dial)
        if dial_event.Name:
            content = content + "{:　<10}".format(dial_event.Name) + dial_event.Text + "\n"
        else:
            content = content + dial_event.Text + "\n"
    try:
        with open(f"{ASS_PATH}/{os.path.splitext(filename)[0]}.txt", "w", encoding="utf8") as fp:
            fp.write(content)
        print(f"Successfully export txt form {filename}")
    except Exception as e:
        print(f"Filed to export txt form {filename}. Info: {e}")
        return


if __name__ == "__main__":
    for filepath, dirnames, filenames in os.walk(TXT_PATH):
        for filename in filenames:
            # if "dear" in filename or "unit" in filename:
            #     generate_txt(filename)
            if filename.endswith(".txt"):
                generate_ass(filename)
