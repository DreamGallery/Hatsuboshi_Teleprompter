import os
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple, Set
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
import time


load_dotenv()


class TranslationService:
    def __init__(self):
        self.api_base = os.getenv("OPENAI_API_BASE")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "deepseek-chat")

        self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)

        self.translation_terms: List[Dict[str, str]] = []

    def filter_terms_for_text(self, text: str) -> List[Dict[str, str]]:
        filtered_terms = []

        for term in self.translation_terms:
            if not term.get("enable", True):
                continue

            if term.get("always_include", False):
                filtered_terms.append(
                    {
                        "src": term["src"],
                        "dst": term["dst"],
                        "info": term.get("info", ""),
                    }
                )
            elif term.get("src", "") in text:
                filtered_terms.append(
                    {
                        "src": term["src"],
                        "dst": term["dst"],
                        "info": term.get("info", ""),
                    }
                )

        return filtered_terms

    def format_terms(self, terms: List[Dict[str, str]]) -> str:
        terms_list = []
        for term in terms:
            src = term["src"]
            dst = term["dst"]
            info = term.get("info")
            if info:
                single = f"{src}->{dst} #{info}"
            else:
                single = f"{src}->{dst}"
            terms_list.append(single)
        return "\n".join(terms_list)

    def create_messages(self, text: str) -> List[Dict[str, str]]:
        relevant_terms = self.filter_terms_for_text(text)
        terms_str = self.format_terms(relevant_terms)

        user_content = (
            f"根据以下术语表（可以为空）：\n{terms_str}\n\n"
            f"将下面的日文文本根据对应关系和备注翻译成中文：{text}\n"
        )

        return [
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，"
                "并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。",
            },
            {"role": "user", "content": user_content},
        ]

    def create_batch_messages(
        self, texts: List[Tuple[str, int]]
    ) -> List[Dict[str, str]]:

        formatted_texts = []
        for text, index in texts:
            formatted_texts.append(f"[{index}] {text}")
        all_texts = "\n\n".join(formatted_texts)
        relevant_terms = self.filter_terms_for_text(all_texts)
        terms_str = self.format_terms(relevant_terms)
        print(terms_str)

        user_content = (
            f"根据以下术语表（可以为空）：\n{terms_str}\n\n"
            f"请将下面的多个日文文本翻译成中文。每个文本都有一个索引编号。\n"
            f"请以相同的格式返回翻译结果，确保保留索引编号，格式为：[索引编号] 翻译后的文本\n"
            f"非常重要：必须翻译所有文本，并确保每个翻译结果都包含对应的索引编号\n\n"
            f"{all_texts}"
        )

        return [
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，"
                "并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
                "你将收到多个标记了索引编号的文本，请翻译每一个并保持相同的索引编号格式。"
                "必须确保翻译所有文本，并在每个翻译前标明正确的索引编号。",
            },
            {"role": "user", "content": user_content},
        ]

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def translate(self, text: str) -> str:
        if not self.api_base or not self.api_key:
            raise ValueError(
                "OPENAI_API_BASE and OPENAI_API_KEY must be set in environment variables"
            )

        try:
            messages = self.create_messages(text)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                top_p=0.95,
                max_tokens=4096,
            )

            translated_text = response.choices[0].message.content.strip()
            return translated_text

        except Exception as e:
            raise Exception(f"Translation API request failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def batch_translate(
        self, texts: List[Tuple[str, int]], chunk_size: int = 20
    ) -> Dict[int, str]:
        if not self.api_base or not self.api_key:
            raise ValueError(
                "OPENAI_API_BASE and OPENAI_API_KEY must be set in environment variables"
            )

        result_map = {}
        orig_text_map = {idx: text for text, idx in texts}
        all_indices = set([idx for _, idx in texts])

        for i in range(0, len(texts), chunk_size):
            chunk = texts[i : i + chunk_size]
            chunk_indices = set([idx for _, idx in chunk])

            try:
                messages = self.create_batch_messages(chunk)

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    top_p=0.95,
                    max_tokens=4096,
                )

                response_text = response.choices[0].message.content.strip()
                translated_indices = self._parse_batch_response(
                    response_text, result_map
                )
                missed_indices = chunk_indices - translated_indices

                if missed_indices:
                    print(
                        f"Missing translations for {len(missed_indices)} texts, retrying individually..."
                    )
                    self._retry_missed_translations(
                        missed_indices, orig_text_map, result_map
                    )

            except Exception as e:
                print(f"Batch translation error: {str(e)}")
                missed_indices = chunk_indices
                self._retry_missed_translations(
                    missed_indices, orig_text_map, result_map
                )

        final_missed = all_indices - set(result_map.keys())
        if final_missed:
            print(
                f"Final check: still missing translations for {len(final_missed)} texts, retrying..."
            )
            self._retry_missed_translations(final_missed, orig_text_map, result_map)

        for idx in all_indices:
            if idx not in result_map:
                print(
                    f"Warning: Failed to translate text with index {idx} after all retries"
                )
                result_map[idx] = ""

        return result_map

    def _parse_batch_response(
        self, response_text: str, result_map: Dict[int, str]
    ) -> Set[int]:
        translated_indices = set()
        current_lines = response_text.split("\n")

        for line in current_lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("[") and "]" in line:
                try:
                    idx_end = line.find("]")
                    idx_str = line[1:idx_end].strip()
                    idx = int(idx_str)
                    translation = line[idx_end + 1 :].strip()
                    result_map[idx] = translation
                    translated_indices.add(idx)
                except (ValueError, IndexError):
                    continue

        return translated_indices

    def _retry_missed_translations(
        self,
        missed_indices: Set[int],
        orig_text_map: Dict[int, str],
        result_map: Dict[int, str],
        max_retries: int = 2,
    ) -> None:
        for idx in missed_indices:
            retry_count = 0
            while retry_count < max_retries and idx not in result_map:
                try:
                    print(f"Retrying translation for index {idx}...")
                    trans = self.translate(orig_text_map[idx])
                    result_map[idx] = trans
                    print(f"Successfully translated index {idx} on retry")
                except Exception as e:
                    print(f"Retry failed for index {idx}: {str(e)}")
                    time.sleep(1)

                retry_count += 1

    def add_translation_term(
        self, src: str, dst: str, info: Optional[str] = None
    ) -> None:
        term = {
            "src": src,
            "dst": dst,
            "info": info if info else "",
            "enable": True,
            "always_include": False,
        }
        self.all_terms.append(term)
