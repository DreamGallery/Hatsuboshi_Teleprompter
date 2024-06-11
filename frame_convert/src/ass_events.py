from src.adv_text import *
from src.time_format import *


class AssEvents(object):
    def __init__(
        self,
        Layer: int = 0,
        Start: str = "",
        End: str = "",
        Duration: float = 0,
        Style: str = "",
        Name: str = "",
        MarginL: int = 0,
        MarginR: int = 0,
        MarginV: int = 0,
        Effect: str = "",
        Text: str = "",
    ):
        self.Layer = Layer
        self.Start = Start
        self.End = End
        self.Duration = Duration
        self.Style = Style
        self.Name = Name
        self.MarginL = MarginL
        self.MarginR = MarginR
        self.MarginV = MarginV
        self.Effect = Effect
        self.Text = Text

    def from_dialogue(self, adv_line: str) -> None:
        self.Start = format_time(get_clip(adv_line).get("_startTime"))
        self.Duration = get_clip(adv_line).get("_duration")
        self.End = end_time(get_clip(adv_line).get("_startTime"), self.Duration)
        self.Style = "Hatsuboshi COMMU"
        self.Name = get_name(adv_line)
        self.Text = get_text(adv_line)

    def echo_dialogue(self) -> str:
        dialogue = "Dialogue: %d,%s,%s,%s,%s,%d,%d,%d,%s,%s" % (
            self.Layer,
            self.Start,
            self.End,
            self.Style,
            self.Name,
            self.MarginL,
            self.MarginR,
            self.MarginV,
            self.Effect,
            "",
        )
        return dialogue

    def echo_comment(self) -> str:
        comment = "Comment: %d,%s,%s,%s,%s,%d,%d,%d,%s,%s" % (
            self.Layer,
            self.Start,
            self.End,
            self.Style,
            self.Name,
            self.MarginL,
            self.MarginR,
            self.MarginV,
            self.Effect,
            self.Text,
        )
        return comment

    @classmethod
    def echo_format(cls) -> str:
        format = "Format:"
        for attribute in cls.__init__.__code__.co_varnames[1:]:
            if attribute == "Duration":
                continue
            format = format + f"\u0020{attribute},"
        format = format[:-1]
        return format
