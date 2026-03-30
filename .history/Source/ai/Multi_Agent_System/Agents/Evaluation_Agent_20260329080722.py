from bert_score import score as bertscore_fn
from underthesea import word_tokenize
import torch
import re
from pathlib import Path

# ---------------------------
# Tiền xử lý tiếng Việt
# ---------------------------
def preprocess_vi(text):
    text = text.strip()
    text = text.replace("\n", " ")
    tokens = word_tokenize(text, format="text")
    return tokens


# ---------------------------
# Tính BERTScore (so khớp tóm tắt với văn bản gốc — không cần gold summary)
# ---------------------------
def compute_bertscore(candidate, reference):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    P, R, F1 = bertscore_fn(
        [candidate],
        [reference],
        lang="vi",
        model_type=None,
        device=device
    )

    return {
        "bertscore_precision": P.item(),
        "bertscore_recall": R.item(),
        "bertscore_f1": F1.item()
    }


# ---------------------------
# Hàm tổng hợp (ứng dụng ngoài, không dùng ROUGE)
# ---------------------------
def evaluate_summary(candidate, reference):
    candidate_proc = preprocess_vi(candidate)
    reference_proc = preprocess_vi(reference)

    candidate_text = " ".join(candidate_proc)
    reference_text = " ".join(reference_proc)

    results = {}
    results.update(compute_bertscore(candidate_text, reference_text))
    return results

class EvaluationAgent:
    _vocab_cache: dict[int, set[str]] = {}

    def _default_vocab_dir(self) -> Path:
        this_file = Path(__file__).resolve()
        for parent in this_file.parents:
            candidate = parent / "Source" / "datasets" / "grade_vocab"
            if candidate.exists():
                return candidate
        return this_file.parent / "grade_vocab"

    def _load_grade_vocab(self, grade: int) -> set[str]:
        grade = int(grade)
        if grade in self._vocab_cache:
            return self._vocab_cache[grade]

        vocab_dir = self._default_vocab_dir()
        vocab_path = vocab_dir / f"grade_{grade}.txt"

        if not vocab_path.exists():
            vocab: set[str] = set()
            self._vocab_cache[grade] = vocab
            return vocab

        with open(vocab_path, "r", encoding="utf-8") as f:
            vocab = {line.strip() for line in f if line.strip()}

        self._vocab_cache[grade] = vocab
        return vocab

    def grade_vocab_match_ratio(
        self,
        summary: str,
        grade_level: int,
        *,
        min_word_char_pattern: str = r"[0-9A-Za-zÀ-ỹ_]",
    ) -> dict:
        """
        ratio = matched_tokens / total_valid_tokens
        """
        if not isinstance(summary, str) or not summary.strip():
            return {
                "grade_level": grade_level,
                "vocab_match_ratio": 0.0,
                "matched_tokens": 0,
                "total_valid_tokens": 0,
            }

        vocab = self._load_grade_vocab(grade_level)
        tokens = preprocess_vi(summary)

        valid_tokens: list[str] = []
        for tok in tokens:
            tok_clean = tok.strip().lower()
            tok_clean = re.sub(
                r"^[^\wÀ-ỹ]+|[^\wÀ-ỹ]+$",
                "",
                tok_clean,
                flags=re.UNICODE,
            )
            if not tok_clean:
                continue
            if not re.search(min_word_char_pattern, tok_clean):
                continue
            valid_tokens.append(tok_clean)

        total = len(valid_tokens)
        if total == 0:
            return {
                "grade_level": grade_level,
                "vocab_match_ratio": 0.0,
                "matched_tokens": 0,
                "total_valid_tokens": 0,
            }

        matched = sum(1 for t in valid_tokens if t in vocab)
        ratio = matched / total

        return {
            "grade_level": grade_level,
            "vocab_match_ratio": ratio,
            "matched_tokens": matched,
            "total_valid_tokens": total,
        }

    def __init__(self):
        pass

    def evaluate(
        self,
        text: str,
        summary: str,
        metrics: list = None
    ) -> dict:

        if metrics is None:
            metrics = ["bertscore"]

        results = {}

        candidate_proc = preprocess_vi(summary)
        reference_proc = preprocess_vi(text)

        candidate_text = " ".join(candidate_proc)
        reference_text = " ".join(reference_proc)

        if "bertscore" in metrics:
            bert_results = compute_bertscore(
                candidate_text,
                reference_text
            )
            results.update(bert_results)

        results["comment"] = self._generate_comment(results)

        difficulty_features = self._compute_difficulty_features(text)
        results.update(difficulty_features)

        return results

    def _generate_comment(self, results: dict) -> str:
        bert_f1 = results.get("bertscore_f1")
        comments = []

        if bert_f1 is not None:
            if bert_f1 > 0.8:
                comments.append("Mức độ tương đồng ngữ nghĩa với văn bản gốc rất cao.")
            elif bert_f1 > 0.6:
                comments.append("Mức độ tương đồng ngữ nghĩa với văn bản gốc ở mức trung bình.")
            else:
                comments.append("Mức độ tương đồng ngữ nghĩa với văn bản gốc còn thấp.")

        return " ".join(comments) if comments else ""

    def _compute_difficulty_features(self, text: str) -> dict:
        if not isinstance(text, str):
            return {}

        raw = text.strip()
        if not raw:
            return {}

        sentence_splits = re.split(r"[.!?]+", raw)
        sentences = [s.strip() for s in sentence_splits if s.strip()]
        num_sentences = max(1, len(sentences))

        tokens = preprocess_vi(raw).split()
        total_words = len(tokens)
        unique_words = len(set(tokens)) if total_words > 0 else 0

        type_token_ratio = (unique_words / total_words) if total_words > 0 else 0.0

        sentence_lengths = []
        for sent in sentences:
            sent_tokens = preprocess_vi(sent).split()
            sentence_lengths.append(len(sent_tokens))

        if sentence_lengths:
            avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
            max_sentence_length = max(sentence_lengths)
            min_sentence_length = min(sentence_lengths)
            long_threshold = 15
            long_count = sum(1 for l in sentence_lengths if l >= long_threshold)
            long_sentence_ratio = long_count / len(sentence_lengths)
        else:
            avg_sentence_length = 0.0
            max_sentence_length = 0
            min_sentence_length = 0
            long_sentence_ratio = 0.0

        word_lengths = [len(w) for w in tokens] if tokens else []
        avg_word_length = (sum(word_lengths) / len(word_lengths)) if word_lengths else 0.0

        words_per_sentence = (total_words / num_sentences) if num_sentences > 0 else 0.0

        lexical_density = (unique_words / total_words) if total_words > 0 else 0.0

        rare_word_ratio = 0.0
        unknown_word_ratio = 0.0
        avg_word_grade = 0.0

        if words_per_sentence <= 10 and avg_word_length <= 4:
            difficulty_level = "Grade 1"
            matched_rules = "grade1_simple_text"
        elif words_per_sentence <= 15 and avg_word_length <= 5:
            difficulty_level = "Grade 2"
            matched_rules = "grade2_basic_text"
        elif words_per_sentence <= 20:
            difficulty_level = "Grade 3"
            matched_rules = "grade3_intermediate_text"
        elif words_per_sentence <= 25:
            difficulty_level = "Grade 4"
            matched_rules = "grade4_advanced_text"
        else:
            difficulty_level = "Grade 5"
            matched_rules = "grade5_complex_text"

        return {
            "difficulty_level": difficulty_level,
            "total_words": total_words,
            "unique_words": unique_words,
            "type_token_ratio": type_token_ratio,
            "rare_word_ratio": rare_word_ratio,
            "unknown_word_ratio": unknown_word_ratio,
            "avg_word_grade": avg_word_grade,
            "num_sentences": num_sentences,
            "avg_sentence_length": avg_sentence_length,
            "max_sentence_length": max_sentence_length,
            "min_sentence_length": min_sentence_length,
            "long_sentence_ratio": long_sentence_ratio,
            "avg_word_length": avg_word_length,
            "words_per_sentence": words_per_sentence,
            "lexical_density": lexical_density,
            "matched_rules": matched_rules,
        }
