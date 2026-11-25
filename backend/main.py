from pathlib import Path

import torch
import torch.nn as nn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from model import NextWordModel
from vocab import Vocab, tokenize

SEQ_LEN = 4
DATA = Path(__file__).parent.parent / "data" / "clean_corpus.txt"

lines = [l.strip() for l in DATA.read_text(encoding="utf-8").splitlines() if l.strip()]
vocab = Vocab.build(lines, max_size=5000)
model = NextWordModel(len(vocab))


def make_samples(texts, seq_len=SEQ_LEN):
    xs, ys = [], []
    for t in texts:
        ids = vocab.encode(tokenize(t))
        for i in range(1, len(ids)):
            ctx = ids[max(0, i - seq_len):i]
            ctx = [0] * (seq_len - len(ctx)) + ctx  # left-pad with <pad>
            xs.append(ctx)
            ys.append(ids[i])
    return torch.tensor(xs), torch.tensor(ys)


def train_baseline(epochs=3, batch_size=512):
    x, y = make_samples(lines)
    opt = torch.optim.Adam(model.parameters(), lr=0.005)
    loss_fn = nn.CrossEntropyLoss()
    model.train()
    for ep in range(epochs):
        perm = torch.randperm(len(x))
        total = 0.0
        for i in range(0, len(x), batch_size):
            idx = perm[i:i + batch_size]
            opt.zero_grad()
            loss = loss_fn(model(x[idx]), y[idx])
            loss.backward()
            opt.step()
            total += loss.item() * len(idx)
        print(f"epoch {ep+1}: loss={total/len(x):.3f}")


train_baseline()

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class PredictIn(BaseModel):
    text: str
    k: int = 3


@app.post("/predict")
def predict(body: PredictIn):
    tokens = tokenize(body.text)
    ids = vocab.encode(tokens)[-SEQ_LEN:]
    ids = [0] * (SEQ_LEN - len(ids)) + ids
    model.eval()
    with torch.no_grad():
        logits = model(torch.tensor([ids]))[0]
        logits[0] = float("-inf")  # never suggest <pad>
        logits[1] = float("-inf")  # never suggest <unk>
        top = torch.topk(logits, body.k).indices.tolist()
    return {"suggestions": [vocab.itos[i] for i in top]}


@app.get("/health")
def health():
    return {"ok": True, "vocab_size": len(vocab)}