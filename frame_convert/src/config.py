import os
import json
import configparser


_BASE_PATH = os.path.abspath(os.path.dirname(__file__) + os.path.sep + "..")
config = configparser.ConfigParser()
config.read(os.path.join(_BASE_PATH, "config.ini"), encoding="utf-8")


# [Info]
player = config.get("Info", "player")
adv_file = config.get("Info", "adv_file")
video = config.get("Info", "video")

# [File Path]
TXT_PATH = config.get("File Path", "TXT_PATH")
ASS_PATH = config.get("File Path", "ASS_PATH")
VIDEO_PATH = config.get("File Path", "VIDEO_PATH")
FONT_PATH = config.get("File Path", "FONT_PATH")

# [Font Config]
font_size = config.getint("Font Config", "font_size")
stroke_width = config.getint("Font Config", "stroke_width")
kerning = config.getint("Font Config", "kerning")

# [ASS Style]
style_1 = json.loads(config.get("ASS Style", "style_1"))

# [Match Arg]
threshold = config.getfloat("Match Arg", "threshold")
half_split_length = config.getint("Match Arg", "half_split_length")
