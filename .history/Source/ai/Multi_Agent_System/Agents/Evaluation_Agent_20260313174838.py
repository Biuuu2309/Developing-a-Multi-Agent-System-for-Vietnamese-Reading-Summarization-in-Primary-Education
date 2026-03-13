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