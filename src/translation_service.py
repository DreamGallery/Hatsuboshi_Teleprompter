import re
import os
import time
from dotenv import load_dotenv
from typing import List, Dict, Optional, Tuple, Set
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


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
            f"将日文文本根据对应关系和备注翻译成中文\n"
            f"注意：不要翻译文本中的英文部分, 不要随意修改文本中的标点符号\n"
            f"重要：必须保留原文中的所有可见换行符\\n，不要丢弃或修改它们\n\n"
            f"日文文本如下：\n\n{text}"
        )

        return [
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，"
                "并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
                "你必须保留原文中的所有格式标记，特别是换行符\\n。",
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

        user_content = (
            f"根据以下术语表（可以为空）：\n{terms_str}\n\n"
            f"将多个日文文本翻译成中文。每个文本都有一个索引编号。\n"
            f"请以相同的格式返回翻译结果，确保保留索引编号，格式为：[索引编号] 翻译后的文本\n"
            f"注意：不要翻译文本中的英文部分, 不要随意修改文本中的标点符号\n"
            f"非常重要：必须翻译所有文本，并确保每个翻译结果都包含对应的索引编号\n"
            f"非常重要：必须保留原文中的所有可见换行符\\n，不要丢弃或修改它们\n\n"
            f"日文文本如下：\n\n{all_texts}"
        )

        return [
            {
                "role": "system",
                "content": "你是一个轻小说翻译模型，可以流畅通顺地以日本轻小说的风格将日文翻译成简体中文，"
                "并联系上下文正确使用人称代词，不擅自添加原文中没有的代词。"
                "你将收到多个标记了索引编号的文本，请翻译每一个并保持相同的索引编号格式。"
                "必须确保翻译所有文本，并在每个翻译前标明正确的索引编号。"
                "你必须保留原文中的所有格式标记，特别是换行符\\n。",
            },
            {"role": "user", "content": user_content},
        ]

    def _is_degenerate_translation(self, original: str, translation: str) -> bool:
        if len(translation) > len(original) * 2:
            words = translation.split()
            if len(words) >= 8:
                for i in range(len(words) - 3):
                    pattern = " ".join(words[i:i+3])
                    count = translation.count(pattern)
                    if count >= 3:
                        print(f"Translation has degenerated: '{pattern}' appears {count} times, retrying...")
                        return True
                
                char_counts = {}
                for char in translation:
                    if char in char_counts:
                        char_counts[char] += 1
                    else:
                        char_counts[char] = 1
                
                most_common_char = max(char_counts.items(), key=lambda x: x[1])
                if most_common_char[1] > len(translation) * 0.3 and len(translation) > 20:
                    print(f"Translation has degenerated: '{most_common_char[0]}' appears too often ({most_common_char[1]} times), retrying...")
                    return True
        
        return False

    def _clean_translation(self, text: str) -> str:
        cleaned = text.replace("\n", "\\n")
        cleaned = cleaned.replace("...", "…")
        cleaned = cleaned.replace("―", "—")
        cleaned = cleaned.replace("《", "『")
        cleaned = cleaned.replace("》", "』")
        cleaned = cleaned.replace("<r=", "<r\\=")
        while True:
            cleaned_old = cleaned
            cleaned = re.sub(r'\\n\s*\\n', '\\n', cleaned)
            if len(cleaned) == len(cleaned_old):
                break
        cleaned = re.sub(r'\\n\s*$', '', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        return cleaned

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def translate(self, text: str, file_name: str) -> str:
        if not self.api_base or not self.api_key:
            raise ValueError(
                "OPENAI_API_BASE and OPENAI_API_KEY must be set in environment variables"
            )

        try:
            messages = self.create_messages(text)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1.3,
                top_p=0.95,
                max_tokens=4096,
            )

            translated_text = response.choices[0].message.content.strip()
            cleaned_translation = self._clean_translation(translated_text)
            
            if self._is_degenerate_translation(text, cleaned_translation):
                messages = self.create_messages(text)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=1,
                    top_p=0.95,
                    max_tokens=4096,
                )
                translated_text = response.choices[0].message.content.strip()
                cleaned_translation = self._clean_translation(translated_text)
            
            return cleaned_translation

        except Exception as e:
            raise Exception(f"File: {file_name}. Translation API request failed: {str(e)}")

    @retry(
        stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def batch_translate(
        self, texts: List[Tuple[str, int]], file_name: str, chunk_size: int = 20
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
            retry_chunk = False

            try:
                messages = self.create_batch_messages(chunk)

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=1.3,
                    top_p=0.95,
                    max_tokens=8192,
                )

                response_text = response.choices[0].message.content.strip()
                translated_indices = self._parse_batch_response(
                    response_text, result_map, orig_text_map
                )
                missed_indices = chunk_indices - translated_indices
                
                has_quality_issues = False
                for idx in translated_indices:
                    if idx in orig_text_map and idx in result_map:
                        if self._is_degenerate_translation(orig_text_map[idx], result_map[idx]):
                            has_quality_issues = True
                            break

                if len(missed_indices) > len(chunk_indices) / 4 or has_quality_issues:
                    print(f"File: {file_name}. Missing a lot of indices or detected quality issues, retrying the whole chunk...")
                    retry_chunk = True
                    for idx in translated_indices:
                        if idx in result_map:
                            del result_map[idx]
                    messages = self.create_batch_messages(chunk)
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=1,
                        top_p=0.95,
                        max_tokens=8192,
                    )
                    response_text = response.choices[0].message.content.strip()
                    translated_indices = self._parse_batch_response(
                        response_text, result_map, orig_text_map
                    )
                    missed_indices = chunk_indices - translated_indices
                
                if missed_indices and not retry_chunk:
                    print(
                        f"File: {file_name}. Missing translations for {len(missed_indices)} texts, retrying individually..."
                    )
                    self._retry_missed_translations(
                        missed_indices, orig_text_map, result_map, file_name
                    )

            except Exception as e:
                print(f"File: {file_name}. Batch translation error: {str(e)}")
                missed_indices = chunk_indices
                self._retry_missed_translations(
                    missed_indices, orig_text_map, result_map, file_name
                )

        final_missed = all_indices - set(result_map.keys())
        if final_missed:
            print(
                f"Final check ({file_name}): still missing translations for {len(final_missed)} texts, retrying..."
            )
            self._retry_missed_translations(final_missed, orig_text_map, result_map, file_name)

        for idx in all_indices:
            if idx not in result_map:
                print(
                    f"Warning ({file_name}): Failed to translate text with index {idx} after all retries"
                )
                result_map[idx] = ""

        return result_map

    def _parse_batch_response(
        self, response_text: str, result_map: Dict[int, str], orig_text_map: Dict[int, str]
    ) -> Set[int]:
        translated_indices = set()
        lines = response_text.split("\n")
        
        processed_lines = []
        index_pattern = re.compile(r'\s*\[\s*(\d+)\s*\]')
        
        for line in lines:
            if not line.strip():
                continue
                
            all_matches = list(index_pattern.finditer(line))
            
            if len(all_matches) > 1:
                start_positions = [match.start() for match in all_matches]
                start_positions.append(len(line))
                
                for i in range(len(all_matches)):
                    start = start_positions[i]
                    end = start_positions[i+1]
                    processed_lines.append(line[start:end])
            else:
                processed_lines.append(line)
        
        index_pattern = re.compile(r'^\s*\[\s*(\d+)\s*\](.*)$')
        current_idx = None
        current_text = ""
        
        for line in processed_lines:
            match = index_pattern.match(line)
            if match:
                if current_idx is not None and current_idx in orig_text_map:
                    result_map[current_idx] = self._clean_translation(current_text)
                    translated_indices.add(current_idx)
                
                try:
                    current_idx = int(match.group(1))
                    current_text = match.group(2).strip()
                except (ValueError, IndexError):
                    current_idx = None
                    current_text = ""
            elif current_idx is not None:
                if not current_text.endswith("\\n") and not line.strip().startswith("\\n"):
                    current_text += "\\n"
                current_text += line.strip()
        
        if current_idx is not None and current_idx in orig_text_map:
            result_map[current_idx] = self._clean_translation(current_text)
            translated_indices.add(current_idx)
            
        return translated_indices

    def _retry_missed_translations(
        self,
        missed_indices: Set[int],
        orig_text_map: Dict[int, str],
        result_map: Dict[int, str],
        file_name: str,
        max_retries: int = 2,
    ) -> None:
        for idx in missed_indices:
            retry_count = 0
            while retry_count < max_retries and idx not in result_map:
                try:
                    translation = self.translate(orig_text_map[idx], file_name)
                    cleaned_translation = self._clean_translation(translation)
                    result_map[idx] = cleaned_translation
                    print(f"File: {file_name}. Successfully translated index {idx} on retry")
                except Exception as e:
                    print(f"File: {file_name}. Retry failed for index {idx}: {str(e)}")
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
