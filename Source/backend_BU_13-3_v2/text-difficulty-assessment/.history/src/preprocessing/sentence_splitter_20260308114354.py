# src/preprocessing/sentence_splitter.py

import re
try:
    from vncorenlp import VnCoreNLP
    VNCORENLP_AVAILABLE = True
except ImportError:
    VNCORENLP_AVAILABLE = False
    print("Warning: vncorenlp not available. Using fallback method.")


class SentenceSplitter:

    def __init__(self, vncorenlp_model_path=None):
        """
        Initialize sentence splitter with vncorenlp if available
        """
        self.vncorenlp = None
        
        if VNCORENLP_AVAILABLE and vncorenlp_model_path:
            try:
                self.vncorenlp = VnCoreNLP(vncorenlp_model_path, annotators="wseg,pos,ner,parse", max_heap_size='-Xmx500m')
            except Exception as e:
                print(f"Warning: Could not initialize VnCoreNLP: {e}. Using fallback method.")
                self.vncorenlp = None

    def split(self, text: str):
        """
        Split text into sentences using vncorenlp if available, otherwise use regex.
        """
        if self.vncorenlp:
            try:
                # VnCoreNLP returns annotated sentences
                annotated = self.vncorenlp.annotate(text)
                sentences = []
                
                # Extract sentences from annotated output
                if isinstance(annotated, dict) and 'sentences' in annotated:
                    for sent in annotated['sentences']:
                        if isinstance(sent, dict) and 'form' in sent:
                            sentences.append(sent['form'])
                        elif isinstance(sent, str):
                            sentences.append(sent)
                elif isinstance(annotated, list):
                    sentences = [str(s) for s in annotated if s]
                else:
                    # Fallback: split by punctuation
                    sentences = re.split(r"[.!?]+", text)
                
                sentences = [s.strip() for s in sentences if s.strip()]
                return sentences if sentences else [text.strip()]
            except Exception as e:
                print(f"Warning: VnCoreNLP sentence splitting failed: {e}. Using fallback.")
        
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
