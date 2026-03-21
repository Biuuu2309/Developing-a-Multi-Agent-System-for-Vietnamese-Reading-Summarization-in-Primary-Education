# Abstracter_Agent.py
import re
import unicodedata
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional, Literal
from rapidfuzz import process, fuzz
from vncorenlp import VnCoreNLP
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from sentence_transformers import SentenceTransformer

WORD_LIMIT = 768
MAX_WORDS  = 768

class AbstracterAgent:
    """
    Abstractive summarization agent
    Model: Fine-tuned ViT5 grade-based summarizer
    """

    def __init__(
        self,
        model_path: str = "E:\Project_NguyenMinhVu_2211110063\Source\ai\Model Train\Model_DG_ver2\vit5_grade_summary",
        max_input_len: int = 768,
        max_target_len: int = 256,
        num_beams: int = 4,
        no_repeat_ngram_size: int = 3,
        annotator: VnCoreNLP = None,
        vncorenlp: VnCoreNLP = None,
        model_simcse = SentenceTransformer("VoVanPhuc/sup-SimCSE-VietNamese-phobert-base")
    ):

        self.model_path = model_path
        self.max_input_len = max_input_len
        self.max_target_len = max_target_len
        self.num_beams = num_beams
        self.no_repeat_ngram_size = no_repeat_ngram_size
        self.annotator = annotator
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.vncorenlp = vncorenlp
        self.model_simcse = model_simcse
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

    def normalize_text(self, text: str) -> str:
        text = text.replace("_", " ")
        text = re.sub(r'\s+([,\.!?;:\)\]])', r'\1', text)
        text = re.sub(r'([,\.!?;:])(?!\s)(?!\d)', r'\1 ', text)
        text = re.sub(r'([\(\[])\s+', r'\1', text)
        text = re.sub(r' +', ' ', text).strip()
        return text

    def sentence_split(self, text: str) -> list[str]:
        """
        Split text thành sentences sử dụng VnCoreNLP nếu có, 
        nếu không thì fallback về regex-based splitting.
        """
        if self.vncorenlp is None:
            # Fallback: split bằng regex khi không có VnCoreNLP
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            return [self.normalize_text(s.strip()) for s in sentences if s.strip()]
        
        sentences = []
        try:
            for sent in self.vncorenlp.annotate(text)["sentences"]:
                raw = " ".join([w["form"] for w in sent])
                sentences.append(self.normalize_text(raw))
        except Exception as e:
            # Fallback nếu VnCoreNLP lỗi
            import re
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
            sentences = [self.normalize_text(s.strip()) for s in sentences if s.strip()]
        
        return sentences
    
    
    
    def textrank(self, sentences):
        tfidf = TfidfVectorizer().fit_transform(sentences)
        sim   = cosine_similarity(tfidf)
        graph = nx.from_numpy_array(sim)
        scores = nx.pagerank(graph)
        return scores

    def lexrank(self, sentences):
        tfidf  = TfidfVectorizer().fit_transform(sentences)
        sim    = cosine_similarity(tfidf)
        scores = sim.sum(axis=1)
        return dict(enumerate(scores))

    def filter_by_ratio(self, sentences, ratio=0.7):
        tr = self.textrank(sentences)
        lr = self.lexrank(sentences)
        combined = {i: 0.5 * tr[i] + 0.5 * lr[i] for i in range(len(sentences))}
        k       = max(1, int(len(sentences) * ratio))
        top_ids = sorted(combined, key=combined.get, reverse=True)[:k]
        return [sentences[i] for i in sorted(top_ids)]

    def phobert_scoring(self, sentences, full_text):
        sent_emb = self.model_simcse.encode(sentences, normalize_embeddings=True)
        doc_emb  = self.model_simcse.encode([full_text], normalize_embeddings=True)[0]
        return sent_emb @ doc_emb

    def mmr(self, sentences, scores, lambda_=0.8, top_k=5):
        sent_emb   = self.model_simcse.encode(sentences, normalize_embeddings=True)
        selected   = []
        candidates = list(range(len(sentences)))

        for _ in range(top_k):
            mmr_scores = []
            for i in candidates:
                redundancy = max(
                    [sent_emb[i] @ sent_emb[j] for j in selected],
                    default=0
                )
                mmr_score = lambda_ * scores[i] - (1 - lambda_) * redundancy
                mmr_scores.append((i, mmr_score))

            best = max(mmr_scores, key=lambda x: x[1])[0]
            selected.append(best)
            candidates.remove(best)

        return [sentences[i] for i in sorted(selected)]

    def count_words(self, text: str) -> int:
        return len(text.split())

    def extract_summary(self,
        text: str,
        max_words: int,   # None = không giới hạn
        filter_ratio: float = 0.7,
        mmr_ratio: float = 0.5,
        lambda_: float = 0.8,
    ) -> str:
        sentences = self.sentence_split(text)

        if len(sentences) < 3:
            result = self.normalize_text(text)
            if max_words and self.count_words(result) > max_words:
                result = " ".join(result.split()[:max_words])
            return result

        filtered = self.filter_by_ratio(sentences, ratio=filter_ratio)
        scores   = self.phobert_scoring(filtered, text)

        # --- top_k ban đầu ---
        top_k = max(1, int(len(filtered) * mmr_ratio))

        # --- Vòng lặp giảm top_k cho đến khi đạt max_words ---
        if max_words:
            while top_k >= 1:
                summary_sents = self.mmr(filtered, scores, lambda_=lambda_, top_k=top_k)
                summary       = " ".join(summary_sents)
                if self.count_words(summary) <= max_words:
                    break
                top_k -= 1
            else:
                # Phòng trường hợp 1 câu vẫn vượt giới hạn
                summary = " ".join(summary.split()[:max_words])
        else:
            summary_sents = self.mmr(filtered, scores, lambda_=lambda_, top_k=top_k)
            summary       = " ".join(summary_sents)

        return summary

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
    
    def extract_entities(self, text):
        """
        Trích xuất thực thể bằng VnCoreNLP nếu có annotator.
        Nếu self.annotator == None thì trả về [] để tránh lỗi.
        """
        if self.annotator is None or not isinstance(text, str) or not text.strip():
            return []

        ner = self.annotator.annotate(text)

        entities = set()

        for sent in ner.get("sentences", []):

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
    
    def correct_entities(self, summary, entities, content):
        """
        Sử dụng danh sách thực thể để sửa lại tên riêng trong summary.
        - Ưu tiên thực thể dài (nhiều token) trước.
        - Chuẩn hóa tên theo đúng dạng xuất hiện trong content (hoa/thường, khoảng trắng).
        - Xử lý được trường hợp dính chữ hoặc có dấu gạch dưới.
        """
        if not isinstance(summary, str) or not summary.strip():
            return summary

        if not isinstance(content, str):
            content = ""

        # Sắp xếp: thực thể dài trước (để xử lý tên đầy đủ trước tên ngắn)
        entities_sorted = sorted(entities, key=len, reverse=True)

        clean_summary = summary

        for entity in entities_sorted:
            raw = entity.strip()
            if not raw:
                continue

            # Bỏ gạch dưới: "Mạc_Đĩnh_Chi" -> "Mạc Đĩnh Chi"
            entity_clean = raw.replace("_", " ").strip()
            if not entity_clean:
                continue

            # Tìm dạng chuẩn trong content (ưu tiên theo văn bản gốc)
            canonical = None
            if content:
                m = re.search(re.escape(entity_clean), content, flags=re.IGNORECASE)
                if m:
                    canonical = m.group(0)

            # Nếu không tìm được trong content, fallback: capitalize từng từ
            if canonical is None:
                canonical = " ".join(w.capitalize() for w in entity_clean.split())

            # Xây regex cho phép thiếu khoảng trắng / có dấu gạch dưới giữa các token
            tokens = re.split(r"\s+", entity_clean)
            if len(tokens) == 1:
                pattern = re.compile(re.escape(tokens[0]), flags=re.IGNORECASE)
            else:
                # Ví dụ: "Mạc Đĩnh Chi" -> r"Mạc[_ ]*Đĩnh[_ ]*Chi"
                pattern_str = r"[_ ]*".join(re.escape(t) for t in tokens)
                pattern = re.compile(pattern_str, flags=re.IGNORECASE)

            # Thay thế trong summary bằng dạng chuẩn
            clean_summary = pattern.sub(canonical, clean_summary)

        # Sau khi sửa theo entity, bỏ các gạch dưới còn sót lại (nếu có)
        clean_summary = clean_summary.replace("_", " ")
        clean_summary = re.sub(r"\s+", " ", clean_summary).strip()

        return clean_summary

    def smart_summary(self, text: str) -> str:
        if self.count_words(text) > WORD_LIMIT:
            return self.extract_summary(text, max_words=MAX_WORDS)
        return text

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
        # 3. WORD → TOKEN (khớp Train_Model_DG: max_new_tokens + min 30% max)
        # -------------------------------
        target_max_len = self._word_to_token_estimate(summary_words)
        target_max_len = min(target_max_len, max_target_len)
        target_max_len = max(target_max_len, 1)
        target_min_len = max(1, min(int(target_max_len * 0.5), target_max_len))

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
                    min_new_tokens=target_min_len,
                    max_new_tokens=target_max_len,
                    num_beams=self.num_beams,
                    length_penalty=1.2,
                    no_repeat_ngram_size=self.no_repeat_ngram_size,
                    early_stopping=True,
                )
            else:
                # sample
                output_ids = self.model.generate(
                    **inputs,
                    min_new_tokens=target_min_len,
                    max_new_tokens=target_max_len,
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

        # Chỉ cố gắng sửa thực thể nếu có annotator
        entities = self.extract_entities(content)
        if entities:
            summary = self.correct_entities(summary, entities, content)

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
            content_smart = self.smart_summary(content)
            summary = self.summarize(
                content_smart,
                grade,
                mode=mode,
                length_option=length_option,
            )
            return summary

        except Exception as e:
            return f"[Abstracter Error] {str(e)}"