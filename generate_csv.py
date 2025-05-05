import os
import time
import concurrent.futures
from src.read_ini import config
from src.story_csv import StoryCsv
from typing import List, Dict, Tuple
from src.gakuen_parser import parse_messages
from src.translation_service import TranslationService
from src.terms import terms

CSV_PATH = config.get("File Path", "CSV_PATH")
TXT_PATH = config.get("File Path", "TXT_PATH")
player_name = config.get("Info", "player_name")


def generate_csv(
    filename: str, chunk_size: int = 20, file_index: int = None, total_files: int = None
):
    with open(f"{TXT_PATH}/{filename}", "r", encoding="utf8") as f:
        gakuen_txt = f.read()
        parsed_lines = parse_messages(gakuen_txt)

        sc_csv = StoryCsv.new_empty_csv(filename)
        texts_to_translate: List[Tuple[str, int]] = []
        text_indices: Dict[int, Dict] = {}

        idx = 0
        for line in parsed_lines:
            if line["__tag__"] == "message" or line["__tag__"] == "narration":
                if line.get("text"):
                    texts_to_translate.append((line["text"], idx))
                    text_indices[idx] = {
                        "type": "narration",
                        "id": "0000000000000",
                        "name": line.get("name", "__narration__"),
                        "text": line["text"],
                    }
                    idx += 1

            elif line["__tag__"] == "choicegroup":
                if isinstance(line["choices"], list):
                    for choice in line["choices"]:
                        texts_to_translate.append((choice["text"], idx))
                        text_indices[idx] = {
                            "type": "choice",
                            "id": "select",
                            "name": "",
                            "text": choice["text"],
                        }
                        idx += 1
                elif isinstance(line["choices"], dict):
                    texts_to_translate.append((line["choices"]["text"], idx))
                    text_indices[idx] = {
                        "type": "choice",
                        "id": "select",
                        "name": "",
                        "text": line["choices"]["text"],
                    }
                    idx += 1
                else:
                    print(
                        f"Warning: Unknown choice type found in {filename}: {type(line['choices'])}, content: {line['choices']}"
                    )

        translations = {}
        has_translator = (
            os.getenv("OPENAI_API_BASE") is not None and os.getenv("OPENAI_API_KEY") is not None
        )
        if has_translator and texts_to_translate:
            translator = TranslationService()
            translator.translation_terms = terms
            progress_prefix = (
                f"[{file_index}/{total_files}] "
                if file_index is not None and total_files is not None
                else ""
            )
            print(
                f"{progress_prefix}Batch translating {filename} with {len(texts_to_translate)} texts..."
            )
            try:
                translations = translator.batch_translate(
                    texts_to_translate, filename, chunk_size
                )
                print(f"{progress_prefix}Translation of {filename} completed")
            except Exception as e:
                print(f"{progress_prefix}Batch translation of {filename} failed: {e}")
                translations = {idx: "" for idx, _ in texts_to_translate}

        for idx, meta in text_indices.items():
            trans_text = (
                translations.get(idx, "").replace('"', '') if has_translator else ""
            )
            sc_csv.append_line(
                {
                    "id": meta["id"],
                    "name": meta["name"],
                    "text": meta["text"],
                    "trans": trans_text,
                }
            )

        with open(
            f"{CSV_PATH}/{os.path.splitext(filename)[0]}.csv", "w", encoding="utf-8"
        ) as fp:
            try:
                fp.write(str(sc_csv))
                progress_prefix = (
                    f"[{file_index}/{total_files}] "
                    if file_index is not None and total_files is not None
                    else ""
                )
                print(
                    f"{progress_prefix}{filename} has been successfully converted to {os.path.splitext(filename)[0]}.csv"
                )
            except Exception as e:
                progress_prefix = (
                    f"[{file_index}/{total_files}] "
                    if file_index is not None and total_files is not None
                    else ""
                )
                print(f"{progress_prefix}{filename} convert failed. Info: {e}")

    return


def batch_generation(max_workers: int = 5, chunk_size: int = 20):
    files_to_process = []
    for filepath, dirnames, filenames in os.walk(TXT_PATH):
        for filename in filenames:
            if not filename.endswith(".txt") or not filename.startswith("adv_"):
                continue
            files_to_process.append(filename)

    total_files = len(files_to_process)
    print(f"Found {total_files} files to process")

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(
                generate_csv, filename, chunk_size, i + 1, total_files
            ): filename
            for i, filename in enumerate(files_to_process)
        }

        for future in concurrent.futures.as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                future.result()
            except Exception as exc:
                print(f"{filename} generated an exception: {exc}")

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"All {total_files} files processed in {processing_time:.2f} seconds")


if __name__ == "__main__":
    batch_generation(max_workers=5, chunk_size=20)
