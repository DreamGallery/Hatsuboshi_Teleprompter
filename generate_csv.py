import os
from src.read_ini import config
from src.story_csv import StoryCsv
from src.gakuen_parser import parse_messages


CSV_PATH = config.get("File Path", "CSV_PATH")
TXT_PATH = config.get("File Path", "TXT_PATH")
player_name = config.get("Info", "player_name")


def generate_csv(filename: str):
    with open(f"{TXT_PATH}/{filename}", "r", encoding="utf8") as f:
        gakuen_txt = f.read()
        parsed_lines = parse_messages(gakuen_txt)
        sc_csv = StoryCsv.new_empty_csv(filename)
        for line in parsed_lines:
            if line["__tag__"] == "message" or line["__tag__"] == "narration":
                if line.get("text"):
                    sc_csv.append_line(
                        {
                            "id": "0000000000000",
                            "name": line.get("name", "__narration__"),
                            "text": line["text"],
                            "trans": "",
                        }
                    )
            if line["__tag__"] == "choicegroup":
                if isinstance(line["choices"], list):
                    for choice in line["choices"]:
                        sc_csv.append_line(
                            {
                                "id": "select",
                                "name": "",
                                "text": choice["text"],
                                "trans": "",
                            }
                        )
                elif isinstance(line["choices"], dict):
                    sc_csv.append_line(
                        {
                            "id": "select",
                            "name": "",
                            "text": line["choices"]["text"],
                            "trans": "",
                        }
                    )
                else:
                    raise ValueError(f"Unknown choice type: {line['choices']}")

        with open(
            f"{CSV_PATH}/{os.path.splitext(filename)[0]}.csv", "w", encoding="utf-8"
        ) as fp:
            try:
                fp.write(str(sc_csv))
                print(
                    f"{filename} has been successfully converted to {os.path.splitext(filename)[0]}.csv"
                )
            except Exception as e:
                print(f"{filename} convert failed. Info: {e}")

    return


if __name__ == "__main__":
    for filepath, dirnames, filenames in os.walk(TXT_PATH):
        for filename in filenames:
            if not filename.endswith(".txt") or not filename.startswith("adv_"):
                continue
            generate_csv(filename)
