# Abstracter_Agent.py

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional


class AbstracterAgent:
    """
    Abstractive summarization agent
    Model: Fine-tuned ViT5 grade-based summarizer
    """

    def __init__(
        self,
        model_path: str = "../../Model_DG/vit5_grade_summary",
        max_input_len: int = 512,
        max_target_len: int = 256,
        num_beams: int = 5,
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
    # CORE SUMMARIZATION
    # =====================================

    def summarize(
        self,
        content: str,
        grade: int,
        max_input_len: Optional[int] = None,
        max_target_len: Optional[int] = None,
        mode: str = "sample"
    ) -> str:

        if not content or len(content.strip()) == 0:
            return "Nội dung trống."

        max_input_len = max_input_len or self.max_input_len
        max_target_len = max_target_len or self.max_target_len

        prompt = f"Tóm tắt văn bản cho học sinh lớp {grade}: {content}"

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=max_input_len
        ).to(self.device)

        with torch.no_grad():
            if mode == "beam":
                output_ids = self.model.generate(
                    **inputs,
                    max_length=max_target_len,
                    num_beams=self.num_beams,
                    early_stopping=True,
                    no_repeat_ngram_size=self.no_repeat_ngram_size
                )
            elif mode == "sample":
                output_ids = self.model.generate(
                **inputs,
                max_length=max_target_len,
                do_sample=True,
                top_k=50,
                top_p=0.9,
                temperature=0.8,
                no_repeat_ngram_size=self.no_repeat_ngram_size
            )

        summary = self.tokenizer.decode(
            output_ids[0],
            skip_special_tokens=True
        )

        return summary.strip()

    # =====================================
    # UNIFIED INTERFACE FOR COORDINATOR
    # =====================================

    def run(self, content: str, grade: int = 5, mode: str = "sample") -> str:
        """
        Unified interface used by Coordinator
        """

        try:
            summary = self.summarize(content, grade, mode=mode)
            return summary

        except Exception as e:
            return f"[Abstracter Error] {str(e)}"