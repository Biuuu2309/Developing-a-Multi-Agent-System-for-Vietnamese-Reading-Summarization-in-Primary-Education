# src/preprocessing/sentence_splitter.py

import re


class SentenceSplitter:

    def __init__(self):
        pass

    def split(self, text: str):
        """
        Split text into sentences based on punctuation.
        """
        sentences = re.split(r"[.!?]+", text)

        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]

        return sentences


if __name__ == "__main__":

    splitter = SentenceSplitter()

    text = "Chú voi con sống trong rừng. Chú rất hiền! Chú thích chơi."

    sentences = splitter.split(text)

    for s in sentences:
        print(s)
