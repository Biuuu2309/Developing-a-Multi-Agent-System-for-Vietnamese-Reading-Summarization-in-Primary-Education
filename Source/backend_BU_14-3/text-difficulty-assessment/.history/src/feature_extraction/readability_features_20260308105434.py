# src/feature_extraction/readability_features.py


class ReadabilityFeatures:

    def __init__(self):
        pass

    def extract(self, tokenized_sentences):

        words = [w for s in tokenized_sentences for w in s]

        total_words = len(words)
        total_sentences = len(tokenized_sentences)

        if total_words == 0:
            return {}

        total_chars = sum(len(w.replace("_", "")) for w in words)

        avg_word_length = total_chars / total_words
        words_per_sentence = total_words / total_sentences if total_sentences else 0

        unique_words = len(set(words))

        lexical_density = unique_words / total_words

        return {
            "avg_word_length": avg_word_length,
            "words_per_sentence": words_per_sentence,
            "lexical_density": lexical_density
        }
