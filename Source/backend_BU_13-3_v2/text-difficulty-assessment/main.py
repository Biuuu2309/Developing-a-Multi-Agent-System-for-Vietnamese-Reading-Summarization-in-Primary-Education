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

    def __init__(self, vncorenlp_model_path=None):

        # Get vncorenlp path from config if not provided
        if vncorenlp_model_path is None:
            vncorenlp_model_path = config.get("preprocessing", {}).get("vncorenlp_model_path")

        # preprocessing
        self.cleaner = TextCleaner()
        self.splitter = SentenceSplitter(vncorenlp_model_path)
        self.tokenizer = Tokenizer(vncorenlp_model_path)
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
        """
        Preprocess text: clean, split sentences, tokenize, and segment.
        Note: For counting (sentence/word count), we use vncorenlp directly on original text
        to match notebook behavior. This preprocessing is for feature extraction.
        """
        # Clean text for processing
        cleaned_text = self.cleaner.clean(text)

        sentences = self.splitter.split(cleaned_text)

        tokens = self.tokenizer.tokenize_sentences(sentences)

        segmented = self.segmenter.segment_sentences(tokens)

        return segmented
    
    def count_sentences_words(self, text):
        """
        Count sentences and words using vncorenlp directly on original text (like notebook).
        This ensures consistent counting with the notebook approach.
        Notebook uses: sentences = annotator.tokenize(text), then counts len(sentences) and sum(len(sent))
        """
        # Use vncorenlp directly on original text (no cleaning) - like notebook
        vncorenlp = self.splitter.vncorenlp or self.tokenizer.vncorenlp
        
        if vncorenlp:
            try:
                # Tokenize directly like notebook: annotator.tokenize(text)
                sentences = vncorenlp.tokenize(text)
                
                if sentences and isinstance(sentences, list):
                    sentence_count = len(sentences)
                    # Count words: sum(len(sent) for sent in sentences)
                    word_count = sum(len(sent) for sent in sentences if isinstance(sent, list))
                    return sentence_count, word_count
            except Exception as e:
                pass
        
        # Fallback: use cleaned text (but this won't match notebook exactly)
        cleaned_text = self.cleaner.clean(text)
        sentences = self.splitter.split(cleaned_text)
        tokens = self.tokenizer.tokenize_sentences(sentences)
        
        sentence_count = len(sentences)
        word_count = sum(len(tokens_list) for tokens_list in tokens)
        
        return sentence_count, word_count

    def extract_features(self, sentences):

        features = {}

        features.update(self.lex.extract(sentences))
        features.update(self.syn.extract(sentences))
        features.update(self.read.extract(sentences))

        return features

    def predict(self, text):

        sentences = self.preprocess(text)

        features = self.extract_features(sentences)
        
        # Override sentence/word counts with vncorenlp direct counting (like notebook)
        sentence_count, word_count = self.count_sentences_words(text)
        features["num_sentences"] = sentence_count
        features["total_words"] = word_count
        
        # Recalculate dependent features
        if word_count > 0:
            features["words_per_sentence"] = word_count / sentence_count if sentence_count > 0 else 0
            features["avg_sentence_length"] = word_count / sentence_count if sentence_count > 0 else 0

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
    print("KET QUA DANH GIA")
    print("="*60)
    print(f"\nDo kho du doan: {difficulty_label}")
    print("\n" + "-"*60)
    print(explanation)
    print("="*60 + "\n")


def run_evaluation(dataset_path):

    evaluator = Evaluator()

    evaluator.evaluate(dataset_path)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="He thong danh gia do kho doc hieu van ban tieng Viet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Vi du su dung:

1. Nhap van ban truc tiep:
   python main.py --text "Chu voi con song trong rung xanh."

2. Doc tu file text:
   python main.py --file input.txt

3. Che do tuong tac (nhap tu ban phim):
   python main.py --interactive

4. Danh gia dataset:
   python main.py --evaluate data/processed/DATA.xlsx
        """
    )

    parser.add_argument(
        "--text",
        type=str,
        help="Van ban can danh gia (nhap truc tiep)"
    )

    parser.add_argument(
        "--file",
        type=str,
        help="Duong dan den file text chua van ban can danh gia"
    )

    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Che do tuong tac - nhap van ban tu ban phim"
    )

    parser.add_argument(
        "--evaluate",
        type=str,
        help="Duong dan den file Excel de danh gia dataset"
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