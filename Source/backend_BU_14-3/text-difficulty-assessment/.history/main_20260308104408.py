# main.py

from preprocessing.text_cleaner import TextCleaner
from preprocessing.sentence_splitter import SentenceSplitter
from preprocessing.tokenizer import Tokenizer
from preprocessing.vietnamese_word_segmenter import VietnameseWordSegmenter

from feature_extraction.lexical_features import LexicalFeatures
from feature_extraction.syntactic_features import SyntacticFeatures
from feature_extraction.readability_features import ReadabilityFeatures

from inference_engine.rule_engine import RuleEngine
from inference_engine.explanation import ExplanationGenerator
from knowledge_base.difficulty_levels import DifficultyLevels
from evaluation.evaluate import Evaluator

import argparse


class ReadingDifficultySystem:

    def __init__(self):

        # preprocessing
        self.cleaner = TextCleaner()
        self.splitter = SentenceSplitter()
        self.tokenizer = Tokenizer()
        self.segmenter = VietnameseWordSegmenter()

        # feature extraction
        self.lex = LexicalFeatures()
        self.syn = SyntacticFeatures()
        self.read = ReadabilityFeatures()

        # inference
        self.engine = RuleEngine()
        self.explainer = ExplanationGenerator()

    def preprocess(self, text):

        text = self.cleaner.clean(text)

        sentences = self.splitter.split(text)

        tokens = self.tokenizer.tokenize_sentences(sentences)

        segmented = self.segmenter.segment_sentences(tokens)

        return segmented

    def extract_features(self, sentences):

        features = {}

        features.update(self.lex.extract(sentences))
        features.update(self.syn.extract(sentences))
        features.update(self.read.extract(sentences))

        return features

    def predict(self, text):

        sentences = self.preprocess(text)

        features = self.extract_features(sentences)

        difficulty, matched_rules = self.engine.infer(features)

        difficulty_label = DifficultyLevels.get_label(difficulty)

        explanation = self.explainer.generate(
            difficulty_label,
            features,
            matched_rules
        )

        return difficulty_label, explanation


def run_prediction(text):

    system = ReadingDifficultySystem()

    difficulty, explanation = system.predict(text)

    print("\n===== RESULT =====\n")
    print(explanation)


def run_evaluation(dataset_path):

    evaluator = Evaluator()

    evaluator.evaluate(dataset_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--text",
        type=str,
        help="Input text to evaluate difficulty"
    )

    parser.add_argument(
        "--evaluate",
        type=str,
        help="Path to dataset Excel for evaluation"
    )

    args = parser.parse_args()

    if args.text:

        run_prediction(args.text)

    elif args.evaluate:

        run_evaluation(args.evaluate)

    else:

        print("Usage:")
        print("Predict difficulty:")
        print('python main.py --text "Chú voi con sống trong rừng xanh."')
        print()
        print("Evaluate dataset:")
        print("python main.py --evaluate data/processed/reading_dataset.xlsx")