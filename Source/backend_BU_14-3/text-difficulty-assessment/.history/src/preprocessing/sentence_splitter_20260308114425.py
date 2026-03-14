# src/preprocessing/sentence_splitter.py

import re
try:
    from py_vncorenlp import VnCoreNLP
    VNCORENLP_AVAILABLE = True
except ImportError:
    try:
        from vncorenlp import VnCoreNLP
        VNCORENLP_AVAILABLE = True
    except ImportError:
        VNCORENLP_AVAILABLE = False


class SentenceSplitter:

    def __init__(self, vncorenlp_model_path=None):
        """
        Initialize sentence splitter with vncorenlp if available
        """
        self.vncorenlp = None
        
        if VNCORENLP_AVAILABLE and vncorenlp_model_path:
            try:
                self.vncorenlp = VnCoreNLP(vncorenlp_model_path, annotators="wseg", max_heap_size='-Xmx500m')
            except Exception as e:
                self.vncorenlp = None

    def split(self, text: str):
        """
        Split text into sentences using vncorenlp if available, otherwise use regex.
        """
        if self.vncorenlp:
            try:
                # VnCoreNLP tokenize returns list of sentences, each sentence is a list of words
                tokenized = self.vncorenlp.tokenize(text)
                
                if tokenized and isinstance(tokenized, list):
                    # Reconstruct sentences from tokenized output
                    sentences = []
                    for sent_tokens in tokenized:
                        if sent_tokens:
                            # Join tokens back to form sentence
                            sentence = " ".join(sent_tokens)
                            sentences.append(sentence)
                    
                    if sentences:
                        return sentences
            except Exception as e:
                pass
        
        # Fallback method using regex
        sentences = re.split(r"[.!?]+", text)
        sentences = [
            sentence.strip()
            for sentence in sentences
            if sentence.strip()
        ]
        return sentences if sentences else [text.strip()]


if __name__ == "__main__":

    splitter = SentenceSplitter()

    text = "Chú voi con sống trong rừng. Chú rất hiền! Chú thích chơi."

    sentences = splitter.split(text)

    for s in sentences:
        print(s)
