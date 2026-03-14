# main.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from preprocessing.text_cleaner import TextCleaner
from preprocessing.sentence_splitter import SentenceSplitter
from preprocessing.tokenizer import Tokenizer
from preprocessing.vietnamese_word_segmenter import VietnameseWordSegmenter

from feature_extraction.lexical_features import LexicalFeatures
from feature_extraction.syntactic_features import SyntacticFeatures
from feature_extraction.readability_features import ReadabilityFeatures
from models.ml_model import MLModel
from inference_engine.rule_engine import RuleEngine
from inference_engine.explanation import ExplanationGenerator
from knowledge_base.difficulty_levels import DifficultyLevels
from evaluation.evaluate import Evaluator
from utils.helpers import load_yaml_config
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


def load_text_from_file(file_path):
    """
    Load text from a file
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def read_text_interactive():
    """
    Read text interactively from user input
    """
    print("\n" + "="*60)
    print("Nhap van ban de danh gia do kho (Nhan Enter 2 lan de ket thuc):")
    print("="*60)
    
    lines = []
    empty_count = 0
    
    while True:
        try:
            line = input()
            if line.strip() == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
        except KeyboardInterrupt:
            print("\n\nDa huy.")
            sys.exit(0)
    
    text = "\n".join(lines).strip()
    
    if not text:
        print("Khong co van ban nao duoc nhap.")
        sys.exit(1)
    
    return text


def run_prediction(text):

    if not text or not text.strip():
        print("Error: Text is empty.")
        return

    system = ReadingDifficultySystem()

    difficulty_label, explanation = system.predict(text)

    print("\n" + "="*60)
    print("KẾT QUẢ ĐÁNH GIÁ")
    print("="*60)
    print(f"\nĐộ khó dự đoán: {difficulty_label}")
    print("\n" + "-"*60)
    print(explanation)
    print("="*60 + "\n")


def run_evaluation(dataset_path):

    evaluator = Evaluator()

    evaluator.evaluate(dataset_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Hệ thống đánh giá độ khó đọc hiểu văn bản tiếng Việt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ví dụ sử dụng:

1. Nhập văn bản trực tiếp:
   python main.py --text "Chú voi con sống trong rừng xanh."

2. Đọc từ file text:
   python main.py --file input.txt

3. Chế độ tương tác (nhập từ bàn phím):
   python main.py --interactive

4. Đánh giá dataset:
   python main.py --evaluate data/processed/DATA.xlsx
        """
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Văn bản cần đánh giá (nhập trực tiếp)"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Đường dẫn đến file text chứa văn bản cần đánh giá"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Chế độ tương tác - nhập văn bản từ bàn phím"
    )

    parser.add_argument(
        "--evaluate",
        type=str,
        help="Đường dẫn đến file Excel để đánh giá dataset"
    )

    args = parser.parse_args()

    if args.evaluate:
        run_evaluation(args.evaluate)
    
    elif args.file:
        text = load_text_from_file(args.file)
        run_prediction(text)
    
    elif args.text:
        run_prediction(args.text)
    
    elif args.interactive:
        text = read_text_interactive()
        run_prediction(text)
    
    else:
        parser.print_help()