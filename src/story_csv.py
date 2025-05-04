import io, csv
from typing import Union, TypedDict, List


class DialogueLine(TypedDict):
    id: str
    name: str
    text: str
    trans: str


class StoryCsv:
    def __init__(self, csv_text: Union[str, List[str]]):
        if isinstance(csv_text, str):
            csv_text.replace("\r\n", "\n")
            csv_text = csv_text.strip().split("\n")

        reader = csv.DictReader(csv_text)
        if reader.fieldnames != ["id", "name", "text", "trans"]:
            raise ValueError(f"First line of csv should be 'id,name,text,trans'")

        self.data: List[DialogueLine] = []
        for line in reader:
            self.append_line(
                {
                    "id": line["id"],
                    "name": line["name"],
                    "text": line["text"],
                    "trans": line["trans"],
                }
            )

        translator_line = self.data.pop(-1)
        if translator_line["id"] != "译者":
            raise ValueError(
                f"Last line of csv should be translator and start with '译者'"
            )
        self.translator = translator_line["name"]

        info_line = self.data.pop(-1)
        if info_line["id"] != "info":
            raise ValueError(
                f"Last but 2 line of csv should be original file info and start with 'info'"
            )
        self.origin = info_line["name"]

    @classmethod
    def new_empty_csv(cls, full_origin: str) -> "StoryCsv":
        return cls(f"id,name,text,trans\ninfo,{full_origin},,\n译者,,,")

    def append_line(self, line: DialogueLine):
        self.data.append(line)

    def __str__(self):
        with io.StringIO() as output:

            writer = csv.DictWriter(output, fieldnames=["id", "name", "text", "trans"])

            writer.writerow(
                {"id": "id", "name": "name", "text": "text", "trans": "trans"}
            )

            for row in self.data:
                writer.writerow(row)
            writer.writerow(
                {"id": "info", "name": self.origin, "text": "", "trans": ""}
            )
            writer.writerow(
                {"id": "译者", "name": self.translator, "text": "", "trans": ""}
            )

            csv_string = output.getvalue()
            return csv_string.replace("\r\n", "\n")
