from rouge_score import rouge_scorer
from bert_score import score as bertscore
from underthesea import word_tokenize
import torch
import re

# ---------------------------
# Tiền xử lý tiếng Việt
# ---------------------------
def preprocess_vi(text):
    text = text.strip()
    text = text.replace("\n", " ")
    tokens = word_tokenize(text, format="text")
    return tokens


# ---------------------------
# Tính ROUGE
# ---------------------------
def compute_rouge(candidate, reference):
    scorer = rouge_scorer.RougeScorer(
        ['rouge1', 'rougeL'],
        use_stemmer=False
    )

    scores = scorer.score(reference, candidate)

    rouge_results = {
        "rouge1_precision": scores['rouge1'].precision,
        "rouge1_recall": scores['rouge1'].recall,
        "rouge1_f1": scores['rouge1'].fmeasure,
        "rougeL_precision": scores['rougeL'].precision,
        "rougeL_recall": scores['rougeL'].recall,
        "rougeL_f1": scores['rougeL'].fmeasure,
    }

    return rouge_results


# ---------------------------
# Tính BERTScore (PhoBERT)
# ---------------------------
from bert_score import score
import torch

def compute_bertscore(candidate, reference):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    P, R, F1 = score(
        [candidate],
        [reference],
        lang="vi",          # QUAN TRỌNG
        model_type=None,    # KHÔNG ghi vinai/phobert-base
        device=device
    )

    return {
        "bertscore_precision": P.item(),
        "bertscore_recall": R.item(),
        "bertscore_f1": F1.item()
    }



# ---------------------------
# Hàm tổng hợp
# ---------------------------
def evaluate_summary(candidate, reference):
    candidate_proc = preprocess_vi(candidate)
    reference_proc = preprocess_vi(reference)

    candidate_text = " ".join(candidate_proc)
    reference_text = " ".join(reference_proc)

    results = {}
    results.update(compute_rouge(candidate_text, reference_text))
    results.update(compute_bertscore(candidate_text, reference_text))

    return results

class EvaluationAgent:
    
    def __init__(self):
        pass

    def evaluate(
        self,
        text: str,
        summary: str,
        metrics: list = None
    ) -> dict:

        if metrics is None:
            metrics = ["rouge", "bertscore"]

        results = {}

        # Tiền xử lý
        candidate_proc = preprocess_vi(summary)
        reference_proc = preprocess_vi(text)

        candidate_text = " ".join(candidate_proc)
        reference_text = " ".join(reference_proc)

        # ROUGE
        if "rouge" in metrics:
            rouge_results = compute_rouge(
                candidate_text,
                reference_text
            )
            results.update(rouge_results)

        # BERTScore
        if "bertscore" in metrics:
            bert_results = compute_bertscore(
                candidate_text,
                reference_text
            )
            results.update(bert_results)

        # Tạo nhận xét
        results["comment"] = self._generate_comment(results)

        # Tính thêm các feature về độ khó văn bản (text difficulty)
        difficulty_features = self._compute_difficulty_features(text)
        results.update(difficulty_features)

        return results

    def _generate_comment(self, results: dict) -> str:
        """
        Sinh nhận xét đơn giản dựa trên F1
        """

        rouge_f1 = results.get("rougeL_f1")
        bert_f1 = results.get("bertscore_f1")

        comments = []

        if rouge_f1 is not None:
            if rouge_f1 > 0.5:
                comments.append("Tóm tắt có mức độ bao phủ nội dung khá tốt.")
            else:
                comments.append("Tóm tắt còn thiếu nhiều thông tin quan trọng.")

        if bert_f1 is not None:
            if bert_f1 > 0.8:
                comments.append("Mức độ tương đồng ngữ nghĩa rất cao.")
            elif bert_f1 > 0.6:
                comments.append("Mức độ tương đồng ngữ nghĩa ở mức trung bình.")
            else:
                comments.append("Mức độ tương đồng ngữ nghĩa còn thấp.")

        return " ".join(comments)

    # -----------------------------------------------------
    # Text difficulty features (đơn giản, tương tự hệ thống đánh giá độ khó)
    # -----------------------------------------------------
    def _compute_difficulty_features(self, text: str) -> dict:
        """
        Tính các feature cơ bản:
        - total_words, unique_words, type_token_ratio
        - num_sentences, avg_sentence_length, max_sentence_length, min_sentence_length
        - long_sentence_ratio
        - avg_word_length, words_per_sentence, lexical_density
        Đồng thời ước lượng mức độ khó (difficulty_level) và matched_rules đơn giản.
        """
        if not isinstance(text, str):
            return {}

        raw = text.strip()
        if not raw:
            return {}

        # Câu: tách theo . ! ? (rất đơn giản)
        sentence_splits = re.split(r"[.!?]+", raw)
        sentences = [s.strip() for s in sentence_splits if s.strip()]
        num_sentences = max(1, len(sentences))

        # Từ: dùng underthesea để word tokenize
        tokens = preprocess_vi(raw).split()
        total_words = len(tokens)
        unique_words = len(set(tokens)) if total_words > 0 else 0

        type_token_ratio = (unique_words / total_words) if total_words > 0 else 0.0

        # Độ dài câu
        sentence_lengths = []
        for sent in sentences:
            sent_tokens = preprocess_vi(sent).split()
            sentence_lengths.append(len(sent_tokens))

        if sentence_lengths:
            avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths)
            max_sentence_length = max(sentence_lengths)
            min_sentence_length = min(sentence_lengths)
            long_threshold = 15  # ngưỡng câu dài
            long_count = sum(1 for l in sentence_lengths if l >= long_threshold)
            long_sentence_ratio = long_count / len(sentence_lengths)
        else:
            avg_sentence_length = 0.0
            max_sentence_length = 0
            min_sentence_length = 0
            long_sentence_ratio = 0.0

        # Độ dài từ trung bình
        word_lengths = [len(w) for w in tokens] if tokens else []
        avg_word_length = (sum(word_lengths) / len(word_lengths)) if word_lengths else 0.0

        words_per_sentence = (total_words / num_sentences) if num_sentences > 0 else 0.0

        # Lexical density ~ tỉ lệ từ khác nhau
        lexical_density = (unique_words / total_words) if total_words > 0 else 0.0

        # Các feature khó định nghĩa (rare / unknown / avg_word_grade) để 0 mặc định
        rare_word_ratio = 0.0
        unknown_word_ratio = 0.0
        avg_word_grade = 0.0

        # Heuristic đơn giản ước lượng độ khó (Grade 1-5)
        # Dựa trên độ dài câu và độ dài từ
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