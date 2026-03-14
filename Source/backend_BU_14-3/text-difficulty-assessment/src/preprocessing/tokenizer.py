# src/preprocessing/tokenizer.py

try:
    from py_vncorenlp import VnCoreNLP
    VNCORENLP_AVAILABLE = True
except ImportError:
    try:
        from vncorenlp import VnCoreNLP
        VNCORENLP_AVAILABLE = True
    except ImportError:
        VNCORENLP_AVAILABLE = False


class Tokenizer:

    def __init__(self, vncorenlp_model_path=None):
        """
        Initialize tokenizer with vncorenlp if available.
        If vncorenlp_model_path is None, py-vncorenlp will auto-download model.
        """
        self.vncorenlp = None
        
        if VNCORENLP_AVAILABLE:
            try:
                if vncorenlp_model_path:
                    self.vncorenlp = VnCoreNLP(vncorenlp_model_path, annotators="wseg", max_heap_size='-Xmx500m')
                else:
                    # py-vncorenlp will auto-download model if path is None
                    self.vncorenlp = VnCoreNLP(save_dir="./models", annotators="wseg")
            except Exception as e:
                self.vncorenlp = None

    def tokenize(self, sentence: str):
        """
        Tokenize sentence using vncorenlp word segmentation if available,
        otherwise use whitespace splitting.
        VnCoreNLP performs Vietnamese word segmentation (tách từ).
        """
        if self.vncorenlp:
            try:
                # VnCoreNLP tokenize returns list of sentences, each sentence is a list of words
                tokenized = self.vncorenlp.tokenize(sentence)
                
                if tokenized and isinstance(tokenized, list):
                    # If multiple sentences, take first one
                    if tokenized and isinstance(tokenized[0], list):
                        return tokenized[0]
                    elif tokenized:
                        return tokenized
            except Exception as e:
                pass
        
        # Fallback: tokenize by whitespace
        return sentence.split()

    def tokenize_sentences(self, sentences):
        """
        Tokenize a list of sentences using vncorenlp word segmentation
        """
        if self.vncorenlp:
            try:
                # Process all sentences at once for efficiency
                all_text = " ".join(sentences)
                tokenized = self.vncorenlp.tokenize(all_text)
                
                if tokenized and isinstance(tokenized, list):
                    return tokenized
            except Exception as e:
                pass
        
        # Fallback: tokenize each sentence separately
        return [self.tokenize(sentence) for sentence in sentences]


if __name__ == "__main__":

    tokenizer = Tokenizer()

    sentence = "ban đêm chú voi con đi dạo"

    tokens = tokenizer.tokenize(sentence)

    print(tokens)
