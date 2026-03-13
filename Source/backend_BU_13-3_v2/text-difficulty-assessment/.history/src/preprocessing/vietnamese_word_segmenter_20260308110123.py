# src/preprocessing/vietnamese_word_segmenter.py

from pathlib import Path


class VietnameseWordSegmenter:

    def __init__(self, vocab_folder="data/vocabulary"):
        """
        Load vocabulary from grade dictionaries
        """
        self.vocab = set()
        self.max_word_length = 1
        self.load_vocab(vocab_folder)

    def load_vocab(self, vocab_folder):
        """
        Load all vocabulary files and merge them.
        Files are loaded in order from grade 1 (lowest) to grade 5 (highest).
        """
        vocab_path = Path(vocab_folder)

        # Load files in order from grade 1 to grade 5
        files = sorted(vocab_path.glob("grade_*.txt"), key=lambda f: int(f.stem.split("_")[1]))

        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    word = line.strip()

                    if word:
                        self.vocab.add(word)

                        length = len(word.split("_"))
                        if length > self.max_word_length:
                            self.max_word_length = length

    def segment(self, tokens):
        """
        Apply longest matching algorithm
        tokens: list of tokens from tokenizer
        """
        i = 0
        result = []

        while i < len(tokens):

            matched = None

            for size in range(self.max_word_length, 0, -1):

                if i + size > len(tokens):
                    continue

                candidate = "_".join(tokens[i:i + size])

                if candidate in self.vocab:
                    matched = candidate
                    result.append(candidate)
                    i += size
                    break

            if matched is None:
                result.append(tokens[i])
                i += 1

        return result

    def segment_sentences(self, tokenized_sentences):
        """
        Apply segmentation to list of tokenized sentences
        """
        return [self.segment(sentence) for sentence in tokenized_sentences]


if __name__ == "__main__":

    segmenter = VietnameseWordSegmenter()

    tokens = ["ban", "đêm", "chú", "voi", "con", "đi", "dạo"]

    segmented = segmenter.segment(tokens)

    print(segmented)