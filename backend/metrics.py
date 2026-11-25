import math
from collections import Counter

import torch
import torch.nn.functional as F

from vocab import tokenize

SEQ_LEN = 4


def make_samples(texts, vocab, seq_len=SEQ_LEN):
    xs, ys = [], []
    for t in texts:
        ids = vocab.encode(tokenize(t))
        for i in range(1, len(ids)):
            ctx = ids[max(0, i - seq_len):i]
            ctx = [0] * (seq_len - len(ctx)) + ctx
            xs.append(ctx)
            ys.append(ids[i])
    return torch.tensor(xs), torch.tensor(ys)


@torch.no_grad()
def evaluate(model, vocab, texts, batch_size=1024):
    x, y = make_samples(texts, vocab)
    total = len(y)
    keep = y != vocab.stoi["<unk>"]
    x, y = x[keep], y[keep]
    n = len(y)

    model.eval()
    top1 = top3 = top5 = 0
    nll = 0.0
    for i in range(0, n, batch_size):
        xb, yb = x[i:i + batch_size], y[i:i + batch_size]
        logits = model(xb)
        logits[:, 0] = float("-inf")  # <pad>
        logits[:, 1] = float("-inf")  # <unk>
        nll += F.cross_entropy(logits, yb, reduction="sum").item()
        hit = logits.topk(5, dim=1).indices == yb.unsqueeze(1)
        top1 += hit[:, :1].any(1).sum().item()
        top3 += hit[:, :3].any(1).sum().item()
        top5 += hit.any(1).sum().item()

    return {
        "samples": n,
        "oov_excluded": total - n,
        "top1": round(top1 / n, 4),
        "top3": round(top3 / n, 4),
        "top5": round(top5 / n, 4),
        "perplexity": round(math.exp(nll / n), 1),
    }


def frequency_baseline(vocab, train_texts, val_texts):
    counts = Counter()
    for t in train_texts:
        counts.update(i for i in vocab.encode(tokenize(t)) if i > 1)
    top = [w for w, _ in counts.most_common(3)]
    _, y = make_samples(val_texts, vocab)
    y = y[y != vocab.stoi["<unk>"]].tolist()
    return {
        "top1": round(sum(t == top[0] for t in y) / len(y), 4),
        "top3": round(sum(t in top for t in y) / len(y), 4),
        "words": [vocab.itos[i] for i in top],
    }