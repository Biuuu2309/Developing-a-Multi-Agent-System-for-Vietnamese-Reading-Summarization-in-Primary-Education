# src/feature_extraction/lexical_features.py

from pathlib import Path
from knowledge_base.vocabulary_knowledge import VocabularyKnowledge

class LexicalFeatures:

    def __init__(self, vocab_folder="data/vocabulary"):
        self.vocab_knowledge = VocabularyKnowledge()
        self.load_vocab(vocab_folder)

    def load_vocab(self, vocab_folder):

        vocab_path = Path(vocab_folder)

        for file in vocab_path.glob("grade_*.txt"):

            grade = int(file.stem.split("_")[1])
            words = set()

            with open(file, "r", encoding="utf-8") as f:
                for line in f:
                    w = line.strip()
                    if w:
                        words.add(w)

            self.vocab_by_grade[grade] = words

    def word_grade(self, word):
        """
        Determine which grade the word belongs to
        """
        for grade in sorted(self.vocab_by_grade.keys()):
            if word in self.vocab_by_grade[grade]:
                return grade
        return None

    def extract(self, tokenized_sentences):

        words = [w for s in tokenized_sentences for w in s]

        total_words = len(words)
        unique_words = len(set(words))

        rare_words = 0
        unknown_words = 0

        word_grades = []

        for w in words:

            g = self.vocab_knowledge.word_grade(w)

            if g is None:
                unknown_words += 1
            else:
                word_grades.append(g)
                if g >= 4:
                    rare_words += 1

        avg_word_grade = sum(word_grades)/len(word_grades) if word_grades else 0

        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "type_token_ratio": unique_words / total_words if total_words else 0,
            "rare_word_ratio": rare_words / total_words if total_words else 0,
            "unknown_word_ratio": unknown_words / total_words if total_words else 0,
            "avg_word_grade": avg_word_grade
        }