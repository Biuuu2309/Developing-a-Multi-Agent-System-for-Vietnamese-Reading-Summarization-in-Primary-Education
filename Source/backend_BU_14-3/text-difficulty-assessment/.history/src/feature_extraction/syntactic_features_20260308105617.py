# src/feature_extraction/syntactic_features.py


class SyntacticFeatures:

    def __init__(self):
        pass

    def extract(self, tokenized_sentences):

        sentence_lengths = [len(s) for s in tokenized_sentences]

        num_sentences = len(sentence_lengths)

        avg_sentence_length = sum(sentence_lengths)/num_sentences if num_sentences else 0

        max_sentence_length = max(sentence_lengths) if sentence_lengths else 0
        min_sentence_length = min(sentence_lengths) if sentence_lengths else 0

        long_sentences = sum(1 for l in sentence_lengths if l >= 15)

        return {
            "num_sentences": num_sentences,
            "avg_sentence_length": avg_sentence_length,
            "max_sentence_length": max_sentence_length,
            "min_sentence_length": min_sentence_length,
            "long_sentence_ratio": long_sentences/num_sentences if num_sentences else 0
        }
