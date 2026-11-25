import re
from collections import Counter

PAD, UNK = "<pad>", "<unk>"


def tokenize(text: str):
    text = text.lower().replace("’", "'").replace("‘", "'")
    return re.findall(r"[a-z]+(?:'[a-z]+)*", text)


class Vocab:
    def __init__(self, words):
        self.itos = [PAD, UNK] + list(words)
        self.stoi = {w: i for i, w in enumerate(self.itos)}

    @classmethod
    def build(cls, texts, max_size=2000):
        counter = Counter()
        for t in texts:
            counter.update(tokenize(t))
        words = [w for w, _ in counter.most_common(max_size)]
        return cls(words)

    def encode(self, tokens):
        return [self.stoi.get(t, self.stoi[UNK]) for t in tokens]

    def __len__(self):
        return len(self.itos)