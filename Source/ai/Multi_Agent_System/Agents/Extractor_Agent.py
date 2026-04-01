# Extractor_Agent.py

import inspect
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel
from nltk.tokenize import sent_tokenize
# ==========================================
# MODEL DEFINITION
# ==========================================
# Matches Train_Model_TX notebook architecture.


class PhoBERTSUM(nn.Module):
    def __init__(self, encoder):
        super().__init__()
        self.encoder = encoder
        hidden = encoder.config.hidden_size
        self.classifier = nn.Sequential(
            nn.Linear(hidden, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 1),
        )

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        cls_emb = outputs.last_hidden_state[:, 0, :]
        return self.classifier(cls_emb)


def _align_classifier_state_dict(state):
    """Map older classifier layouts to the current notebook layout."""
    if not isinstance(state, dict):
        return state
    out = dict(state)
    if "classifier.weight" in out and "classifier.3.weight" not in out:
        out["classifier.3.weight"] = out.pop("classifier.weight")
        out["classifier.3.bias"] = out.pop("classifier.bias")
    if "classifier.1.weight" in out and "classifier.3.weight" not in out:
        out["classifier.3.weight"] = out.pop("classifier.1.weight")
        out["classifier.3.bias"] = out.pop("classifier.1.bias")
    return out


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
        encoder_name: str = "vinai/phobert-large",
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

        load_kw = {"map_location": self.device}
        if "weights_only" in inspect.signature(torch.load).parameters:
            load_kw["weights_only"] = False
        checkpoint = torch.load(self.model_path, **load_kw)

        state = None
        if isinstance(checkpoint, dict):
            for key in ("model_state_dict", "model_state", "state_dict"):
                if key in checkpoint:
                    state = checkpoint[key]
                    break
            if state is None:
                # raw state dict (tensor keys only)
                if checkpoint and all(
                    isinstance(v, torch.Tensor) for v in checkpoint.values()
                ):
                    state = checkpoint
        else:
            state = checkpoint

        if state is None:
            raise KeyError(
                "Checkpoint must contain model_state_dict, model_state, "
                "state_dict, or be a raw state dict. "
                f"Got keys: {list(checkpoint.keys()) if isinstance(checkpoint, dict) else type(checkpoint)}"
            )

        self.model.load_state_dict(_align_classifier_state_dict(state))

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