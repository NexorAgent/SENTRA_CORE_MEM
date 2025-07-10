'''
cmpz_dict_builder.py

Module for building a dynamic compression dictionary for the CMPZ pipeline.
'''  
import re
import json
from collections import Counter

class CMPZDictBuilder:
    def __init__(self, memory_blocks, stopwords=None):
        """
        :param memory_blocks: Iterable of text blocks to analyze
        :param stopwords:    Iterable of tokens to exclude from dictionary
        """
        self.memory_blocks = memory_blocks
        self.stopwords = set(stopwords) if stopwords else set()
        self.dictionary = {}

    def preprocess(self, text):
        """
        Lowercase, remove punctuation, tokenize, filter stopwords
        """
        text = text.lower()
        # strip punctuation
        text = re.sub(r"[^\w\s]", "", text)
        tokens = text.split()
        tokens = [t for t in tokens if t and t not in self.stopwords]
        return tokens

    def build_frequency(self):
        """
        Count token frequencies across all memory blocks
        :return: Counter of token frequencies
        """
        counter = Counter()
        for block in self.memory_blocks:
            tokens = self.preprocess(block)
            counter.update(tokens)
        return counter

    def build_dict(self, top_n=1000):
        """
        Build dictionary mapping top-N tokens to glyph symbols
        :param top_n: Number of most frequent tokens to include
        :return: Mapping token -> symbol
        """
        freq = self.build_frequency()
        most_common = freq.most_common(top_n)
        # assign hex-based glyph codes: §00, §01, …
        self.dictionary = {token: f"§{i:02X}" for i, (token, _) in enumerate(most_common)}
        return self.dictionary

    def load_dict(self, path):
        """
        Load existing dictionary from JSON file
        """
        with open(path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
        return self.dictionary

    def save_dict(self, path):
        """
        Persist dictionary to JSON file
        """
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.dictionary, f, ensure_ascii=False, indent=2)

# Example usage
if __name__ == '__main__':
    # Load memory blocks
    with open('resume_translated.txt', 'r', encoding='utf-8') as f:
        blocks = f.read().split('---')  # adjust delimiter as needed

    # Optionally load stopwords
    stopwords = set()
    try:
        with open('cmpz_stopwords.txt', 'r', encoding='utf-8') as sf:
            stopwords = set(sf.read().split())
    except FileNotFoundError:
        pass

    builder = CMPZDictBuilder(blocks, stopwords)
    glyph_dict = builder.build_dict(top_n=500)
    builder.save_dict('cmpz_dict.json')
    print(f"Generated {len(glyph_dict)} glyph entries.")
