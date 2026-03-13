# src/preprocessing/text_cleaner.py

import re

class TextCleaner:
    
    def __init__(self):
        pass

    def remove_special_characters(self, text: str) -> str:
        """
        Remove special characters except Vietnamese letters and punctuation.
        """
        text = re.sub(r"[^a-zA-ZÀ-ỹ0-9\s.,!?;:]", " ", text)
        return text

    def normalize_whitespace(self, text: str) -> str:
        """
        Normalize multiple spaces to single space
        """
        return re.sub(r"\s+", " ", text).strip()

    def lowercase(self, text: str) -> str:
        """
        Convert text to lowercase
        """
        return text.lower()

    def clean(self, text: str) -> str:
        """
        Full cleaning pipeline
        """
        text = self.lowercase(text)
        text = self.remove_special_characters(text)
        text = self.normalize_whitespace(text)
        return text


if __name__ == "__main__":
    cleaner = TextCleaner()

    sample = "Ban đêm, chú voi con đi dạo!!!"
    cleaned = cleaner.clean(sample)

    print(cleaned)
