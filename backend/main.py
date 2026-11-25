import json
import threading  # noqa: F401
from pathlib import Path

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fl import Client, FLServer, train_on
from metrics import SEQ_LEN, evaluate, frequency_baseline, make_samples
from model import NextWordModel
from vocab import Vocab, tokenize

torch.manual_seed(0)

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
ART = ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def read_lines(path):
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


train_lines = read_lines(DATA / "clean_corpus.txt")
val_lines = read_lines(DATA / "val.txt")

# ---------- vocab (saved, so it never changes between restarts) ----------
VOCAB_PATH = ART / "vocab.json"
if VOCAB_PATH.exists():
    vocab = Vocab(json.loads(VOCAB_PATH.read_text(encoding="utf-8")))
else:
    vocab = Vocab.build(train_lines, max_size=5000)
    VOCAB_PATH.write_text(json.dumps(vocab.itos[2:]), encoding="utf-8")
print("vocab size:", len(vocab))

# ---------- centralized baseline (trained once, then loaded) ----------
baseline = NextWordModel(len(vocab))
BASE_PATH = ART / "baseline.pt"
if BASE_PATH.exists():
    baseline.load_state_dict(torch.load(BASE_PATH))
    print("loaded baseline from disk")
else:
    x, y = make_samples(train_lines, vocab)
    loss = train_on(baseline, x, y, epochs=3, lr=0.005, batch_size=512)
    torch.save(baseline.state_dict(), BASE_PATH)
    print(f"trained baseline, final loss={loss:.3f}")
baseline.eval()

# ---------- federated setup: one client per story ----------
clients = [
    Client(f.stem, read_lines(f), vocab)
    for f in sorted((DATA / "clients").glob("holmes_*.txt"))
]
print("clients:", [(c.cid, c.n) for c in clients])

fed = FLServer(
    model=NextWordModel(len(vocab)),
    vocab=vocab,
    clients=clients,
    val_lines=val_lines,
    weights_path=ART / "federated.pt",
    history_path=ART / "fl_history.json",
)

# ---------- API ----------
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def top_k(model, text, k):
    ids = vocab.encode(tokenize(text))[-SEQ_LEN:]
    ids = [0] * (SEQ_LEN - len(ids)) + ids
    model.eval()
    with torch.no_grad():
        logits = model(torch.tensor([ids]))[0]
    logits[0] = float("-inf")  # <pad>
    logits[1] = float("-inf")  # <unk>
    top = torch.topk(logits, k).indices.tolist()
    return [vocab.itos[i] for i in top]


class PredictIn(BaseModel):
    text: str
    k: int = 3
    which: str = "baseline"  # "baseline" or "federated"


@app.post("/predict")
def predict(body: PredictIn):
    if body.which == "federated":
        with fed.lock:
            words = top_k(fed.model, body.text, body.k)
    else:
        words = top_k(baseline, body.text, body.k)
    return {"suggestions": words, "model": body.which}


@app.get("/health")
def health():
    return {"ok": True, "vocab_size": len(vocab), "fl_round": fed.round}


@app.get("/evaluate")
def evaluate_endpoint():
    return {
        "baseline": evaluate(baseline, vocab, val_lines),
        "federated": fed._evaluate(),
        "fl_round": fed.round,
        "frequency_baseline": frequency_baseline(vocab, train_lines, val_lines),
    }


class FLConfig(BaseModel):
    rounds: int = 20
    clients_per_round: int = 6
    local_epochs: int = 2
    lr: float = 0.005


@app.post("/fl/start")
def fl_start(cfg: FLConfig):
    ok = fed.start(rounds=cfg.rounds, clients_per_round=cfg.clients_per_round,
                   local_epochs=cfg.local_epochs, lr=cfg.lr)
    return {"started": ok, "message": "started" if ok else "already running"}


@app.get("/fl/status")
def fl_status():
    return {"running": fed.running, "round": fed.round, "error": fed.error,
            "history": fed.history}


@app.post("/fl/reset")
def fl_reset():
    if fed.running:
        return {"reset": False, "message": "training is running"}
    fed.reset()
    return {"reset": True}