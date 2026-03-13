# src/knowledge_base/vocabulary_knowledge.py

from pathlib import Path


class VocabularyKnowledge:

    def __init__(self, vocab_folder="data/vocabulary"):
        self.vocab_by_grade = {}
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

        for grade in sorted(self.vocab_by_grade.keys()):
            if word in self.vocab_by_grade[grade]:
                return grade

        return None

    def text_vocabulary_grade(self, words):
        """
        Estimate difficulty level of vocabulary in a text
        """

        grades = []

        for w in words:

            g = self.word_grade(w)

            if g is not None:
                grades.append(g)

        if not grades:
            return None

        return sum(grades) / len(grades)
