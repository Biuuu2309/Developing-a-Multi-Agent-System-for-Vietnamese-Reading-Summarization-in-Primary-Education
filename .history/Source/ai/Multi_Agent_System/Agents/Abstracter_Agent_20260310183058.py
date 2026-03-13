# Abstracter_Agent.py
import re
import unicodedata
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional, Literal


class AbstracterAgent:
    """
    Abstractive summarization agent
    Model: Fine-tuned ViT5 grade-based summarizer
    """

    def __init__(
        self,
        model_path: str = "E:\Project_NguyenMinhVu_2211110063\Source\ai\Model Train\Model_DG\vit5_grade_summary",
        max_input_len: int = 512,
        max_target_len: int = 256,
        num_beams: int = 4,
        no_repeat_ngram_size: int = 3
    ):

        self.model_path = model_path
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len
        self.num_beams = num_beams
        self.no_repeat_ngram_size = no_repeat_ngram_size

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self._load_model()

    # =====================================
    # MODEL LOADING
    # =====================================

    def _load_model(self):

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_path,
            use_fast=False
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_path
        )

        self.model.to(self.device)
        self.model.eval()

    # =====================================
    # LENGTH CONTROL UTILITIES
    # =====================================

    def _count_words(self, text: str) -> int:
        """
        Đếm số từ đơn giản (split theo whitespace).
        Đủ tốt để ước lượng độ dài summary, không phụ thuộc VnCoreNLP.
        """
        if not isinstance(text, str):
            return 0
        return len(text.split())

    def _word_to_token_estimate(self, word_count: int) -> int:
        """
        Ước lượng số token từ số từ.
        Dựa trên thực nghiệm với T5: 1 word ≈ 1.3 token.
        """
        if word_count <= 0:
            return 0
        return int(word_count * 1.3)

    def _clean_summary(self, summary: str) -> str:
        """
        Cắt summary ở dấu chấm cuối để tránh dở câu.
        """
        if not isinstance(summary, str):
            return ""
        last_period = summary.rfind(".")
        if last_period != -1:
            summary = summary[: last_period + 1]
        return summary.strip()
    
    def vietnamese_text_normalization(self, text, vncore=None):
        """
        Vietnamese Text Normalization Layer
        Works for ANY Vietnamese text
        """

        # ====================================
        # 1. Unicode normalization
        # ====================================
        text = unicodedata.normalize("NFC", text)

        # ====================================
        # 2. Remove duplicated spaces
        # ====================================
        text = re.sub(r"\s+", " ", text)

        # ====================================
        # 3. Fix spacing around punctuation
        # ====================================
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)
        text = re.sub(r"([,.!?;:])([^\s])", r"\1 \2", text)

        # ====================================
        # 4. Fix glued words
        # Example: Đĩnhchi -> Đĩnh Chi
        # ====================================
        text = re.sub(
            r"([a-zàáạảãăắằẳẵặâấầẩẫậđèéẹẻẽêếềểễệìíịỉĩòóọỏõôốồổỗộơớờởỡợùúụủũưứừửữựỳýỵỷỹ])([A-ZÀÁẠẢÃĂẮẰẲẴẶÂẤẦẨẪẬĐ])",
            r"\1 \2",
            text
        )

        # ====================================
        # 5. Fix ALL CAPS words
        # ====================================
        words = text.split()

        fixed_words = []
        for w in words:
            if w.isupper() and len(w) > 2:
                fixed_words.append(w.capitalize())
            else:
                fixed_words.append(w)

        text = " ".join(fixed_words)

        # ====================================
        # 6. Capitalize sentences
        # ====================================
        sentences = re.split(r'(?<=[.!?]) +', text)

        def capitalize_first_letter(sentence):
            if not sentence:
                return sentence
            return sentence[0].upper() + sentence[1:]

        sentences = [capitalize_first_letter(s) for s in sentences]

        text = " ".join(sentences)

        # ====================================
        # 7. Use NER to fix proper names
        # ====================================
        if vncore is not None:

            annotated = vncore.annotate(text)

            entities = set()

            for sent in annotated['sentences']:
                for token in sent:
                    if token['nerLabel'] != 'O':
                        entities.add(token['form'])

            for ent in entities:
                pattern = re.compile(ent, re.IGNORECASE)
                text = pattern.sub(ent, text)

        return text.strip()

    # =====================================
    # CORE SUMMARIZATION
    # =====================================
    
    def extract_entities(text):
    
        ner = annotator.annotate(text)

        entities = set()

        for sent in ner['sentences']:

            current_entity = []
            current_label = None

            for token in sent:

                label = token.get("nerLabel", "O")

                if label.startswith("B-"):

                    if current_entity:
                        entities.add(" ".join(current_entity))

                    current_entity = [token["form"]]
                    current_label = label[2:]

                elif label.startswith("I-") and current_entity:

                    current_entity.append(token["form"])

                else:

                    if current_entity:
                        entities.add(" ".join(current_entity))

                    current_entity = []

            if current_entity:
                entities.add(" ".join(current_entity))

        return list(entities)
    
    def correct_entities(summary, entities):
    
        words = summary.split()
    
        for entity in entities:
        
            match, score, _ = process.extractOne(
                entity,
                words,
                scorer=fuzz.partial_ratio
            )
    
            if score > 70:
                summary = summary.replace(match, entity)
    
        return summary

    def summarize(
        self,
        content: str,
        grade: int,
        max_input_len: Optional[int] = None,
        max_target_len: Optional[int] = None,
        mode: str = "sample",
        length_option: Literal["short", "medium", "long"] = "medium",
    ) -> str:

        if not content or len(content.strip()) == 0:
            return "Nội dung trống."

        max_input_len = max_input_len or self.max_input_len
        # max_target_len là upper bound cứng để tránh quá dài
        max_target_len = max_target_len or self.max_target_len

        # -------------------------------
        # 1. Đếm số từ văn bản gốc
        # -------------------------------
        total_words = self._count_words(content)

        # -------------------------------
        # 2. Tính số từ mong muốn cho summary
        # -------------------------------
        if length_option == "short":
            summary_words = int(total_words * 0.35)
        elif length_option == "long":
            summary_words = int(total_words * 0.75)
        else:
            # medium hoặc bất kỳ giá trị lạ nào → medium
            summary_words = int(total_words * 0.50)

        # -------------------------------
        # 3. WORD → TOKEN
        # -------------------------------
        target_max_len = self._word_to_token_estimate(summary_words)
        target_min_len = int(target_max_len * 0.6) if target_max_len > 0 else 0

        # Giới hạn bởi max_target_len cấu hình của agent
        target_max_len = min(target_max_len, max_target_len)
        if target_min_len >= target_max_len:
            target_min_len = int(target_max_len * 0.6)

        # Đảm bảo không quá ngắn
        if target_max_len < 32:
            target_max_len = min(max_target_len, 32)
            target_min_len = int(target_max_len * 0.6)

        # -------------------------------
        # 4. TOKENIZE INPUT
        # -------------------------------
        prompt = f"Tóm tắt văn bản cho học sinh lớp {grade}: {content}"

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_input_len
        ).to(self.device)

        # -------------------------------
        # 5. GENERATE
        # -------------------------------
        with torch.no_grad():
            if mode == "beam":
                output_ids = self.model.generate(
                    **inputs,
                    min_length=target_min_len,
                    max_length=target_max_len,
                    num_beams=self.num_beams,
                    length_penalty=1.2,
                    no_repeat_ngram_size=self.no_repeat_ngram_size,
                    early_stopping=True,
                )
            else:
                # sample
                output_ids = self.model.generate(
                    **inputs,
                    min_length=target_min_len,
                    max_length=target_max_len,
                    do_sample=True,
                    top_k=50,
                    top_p=0.9,
                    temperature=0.8,
                    no_repeat_ngram_size=self.no_repeat_ngram_size,
                )

        summary = self.tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True
        )

        summary = self._clean_summary(summary)
        summary = self.vietnamese_text_normalization(summary)
        return summary.strip()

    # =====================================
    # UNIFIED INTERFACE FOR COORDINATOR
    # =====================================

    def run(
        self,
        content: str,
        grade: int = 5,
        mode: str = "sample",
        length_option: Literal["short", "medium", "long"] = "medium",
    ) -> str:
        """
        Unified interface used by Coordinator
        """

        try:
            summary = self.summarize(
                content,
                grade,
                mode=mode,
                length_option=length_option,
            )
            return summary

        except Exception as e:
            return f"[Abstracter Error] {str(e)}"