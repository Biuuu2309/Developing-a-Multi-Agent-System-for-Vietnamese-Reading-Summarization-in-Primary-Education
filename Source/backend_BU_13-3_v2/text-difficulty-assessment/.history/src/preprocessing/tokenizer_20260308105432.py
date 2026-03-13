# src/preprocessing/tokenizer.py

class Tokenizer:

    def __init__(self):
        pass

    def tokenize(self, sentence: str):
        """
        Tokenize sentence by whitespace
        """
        tokens = sentence.split()
        return tokens

    def tokenize_sentences(self, sentences):
        """
        Tokenize a list of sentences
        """
        return [self.tokenize(sentence) for sentence in sentences]


if __name__ == "__main__":

    tokenizer = Tokenizer()

    sentence = "ban đêm chú voi con đi dạo"

    tokens = tokenizer.tokenize(sentence)

    print(tokens)
