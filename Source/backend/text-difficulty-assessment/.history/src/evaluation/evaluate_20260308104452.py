# src/evaluation/evaluate.py

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report

from preprocessing.text_cleaner import TextCleaner
from preprocessing.sentence_splitter import SentenceSplitter
from preprocessing.tokenizer import Tokenizer
from preprocessing.vietnamese_word_segmenter import VietnameseWordSegmenter

from feature_extraction.lexical_features import LexicalFeatures
from feature_extraction.syntactic_features import SyntacticFeatures
from feature_extraction.readability_features import ReadabilityFeatures

from inference_engine.rule_engine import RuleEngine
from utils.helpers import load_excel_dataset

class Evaluator:

    def __init__(self):

        self.cleaner = TextCleaner()
        self.splitter = SentenceSplitter()
        self.tokenizer = Tokenizer()
        self.segmenter = VietnameseWordSegmenter()

        self.lex = LexicalFeatures()
        self.syn = SyntacticFeatures()
        self.read = ReadabilityFeatures()

        self.engine = RuleEngine()

    def process_text(self, text):

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

    def evaluate(self, excel_path):

        df = load_excel_dataset(excel_path)

        y_true = []
        y_pred = []

        for _, row in df.iterrows():

            text = row["content"]
            true_grade = row["grade"]

            sentences = self.process_text(text)

            features = self.extract_features(sentences)

            pred_grade, _ = self.engine.infer(features)

            if pred_grade is None:
                continue

            y_true.append(true_grade)
            y_pred.append(pred_grade)

        print("Accuracy:", accuracy_score(y_true, y_pred))
        print()
        print(classification_report(y_true, y_pred))