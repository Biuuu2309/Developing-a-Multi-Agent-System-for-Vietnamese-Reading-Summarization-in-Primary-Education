# src/knowledge_base/vocabulary_knowledge.py

from pathlib import Path


class VocabularyKnowledge:

    def __init__(self, vocab_folder="data/vocabulary"):
        self.vocab_by_grade = {}
        self.load_vocab(vocab_folder)

    def load_vocab(self, vocab_folder):
        """
        Load vocabulary files from grade 1 to grade 5.
        Files are loaded in order from grade 1 (lowest) to grade 5 (highest).
        """
        vocab_path = Path(vocab_folder)

        # Load files in order from grade 1 to grade 5
        files = sorted(vocab_path.glob("grade_*.txt"), key=lambda f: int(f.stem.split("_")[1]))

        for file in files:
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
        Determine the grade level of a word.
        Returns the LOWEST grade where the word appears.
        Checks from grade 1 (lowest) to grade 5 (highest).
        This ensures that if a word appears in multiple grade files,
        we return the earliest/appropriate grade level.
        """
        # Check from grade 1 (lowest) to grade 5 (highest)
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
