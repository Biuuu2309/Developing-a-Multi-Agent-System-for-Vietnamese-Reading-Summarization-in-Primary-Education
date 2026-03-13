# main.py

from src.preprocessing.text_cleaner import TextCleaner
from src.preprocessing.sentence_splitter import SentenceSplitter
from src.preprocessing.tokenizer import Tokenizer
from src.preprocessing.vietnamese_word_segmenter import VietnameseWordSegmenter

from src.feature_extraction.lexical_features import LexicalFeatures
from src.feature_extraction.syntactic_features import SyntacticFeatures
from src.feature_extraction.readability_features import ReadabilityFeatures
from src.models.ml_model import MLModel
from src.inference_engine.rule_engine import RuleEngine
from src.inference_engine.explanation import ExplanationGenerator
from src.knowledge_base.difficulty_levels import DifficultyLevels
from src.evaluation.evaluate import Evaluator
from src.utils.helpers import load_yaml_config
import argparse

config = load_yaml_config("config/config.yaml")

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
        self.model = MLModel()

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
            difficulty,
            features,
            matched_rules
        )
        return difficulty_label, explanation


def run_prediction(text):

    system = ReadingDifficultySystem()

    difficulty_label, explanation = system.predict(text)

    print("\n===== RESULT =====\n")
    print(f"Predicted difficulty: {difficulty_label}")
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