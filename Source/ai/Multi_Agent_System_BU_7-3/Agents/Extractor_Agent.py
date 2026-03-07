# Extractor_Agent.py

import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from nltk.tokenize import sent_tokenize
from typing import Optional


# ==========================================
# MODEL DEFINITION
# ==========================================

class PhoBERTSUM(nn.Module):
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        self.classifier = nn.Linear(
            encoder.config.hidden_size, 1
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        sent_emb = outputs.last_hidden_state.mean(dim=1)
        return self.classifier(sent_emb)


# ==========================================
# EXTRACTOR AGENT
# ==========================================

class ExtractorAgent:
    """
    Extractive summarization agent
    Model: PhoBERTSUM (sentence scoring model)
    """

    def __init__(
        self,
        model_path: str,
        encoder_name: str = "vinai/phobert-base",
        max_len: int = 128
    ):

        self.model_path = model_path
        self.encoder_name = encoder_name
        self.max_len = max_len

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self._load_model()

    # ======================================
    # LOAD MODEL
    # ======================================

    def _load_model(self):

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.encoder_name,
            use_fast=False
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        encoder = AutoModel.from_pretrained(
            self.encoder_name
        ).to(self.device)

        self.model = PhoBERTSUM(encoder).to(self.device)

        checkpoint = torch.load(
            self.model_path,
            map_location=self.device
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model.eval()

    # ======================================
    # UTILITIES
    # ======================================

    def _split_sentences(self, text: str):

        if not isinstance(text, str):
            return []

        sentences = sent_tokenize(text)

        return [
            s.strip()
            for s in sentences
            if len(s.strip()) > 10
        ]

    def _get_top_k(self, num_sentences: int, ratio: float):

        return max(1, int(num_sentences * ratio))

    # ======================================
    # CORE EXTRACTIVE LOGIC
    # ======================================

    @torch.no_grad()
    def extract(
        self,
        text: str,
        ratio: float = 0.5
    ) -> str:

        sentences = self._split_sentences(text)
        n = len(sentences)

        if n == 0:
            return ""

        if n == 1:
            return sentences[0]

        top_k = self._get_top_k(n, ratio)

        encoded = self.tokenizer(
            sentences,
            padding=True,
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )

        input_ids = encoded["input_ids"].to(self.device)
        attention_mask = encoded["attention_mask"].to(self.device)

        scores = self.model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        scores = scores.squeeze().cpu()

        top_idx = torch.topk(
            scores,
            min(top_k, n)
        ).indices.tolist()

        if not isinstance(top_idx, list):
            top_idx = [top_idx]

        top_idx.sort()

        summary = " ".join(
            sentences[i] for i in top_idx
        )

        return summary.strip()

    # ======================================
    # UNIFIED INTERFACE FOR COORDINATOR
    # ======================================

    def run(
        self,
        text: str,
        ratio: float = 0.5
    ) -> str:

        try:
            return self.extract(text, ratio=ratio)

        except Exception as e:
            return f"[Extractor Error] {str(e)}"