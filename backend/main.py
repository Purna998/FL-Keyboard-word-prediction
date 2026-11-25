import json
import os
from pathlib import Path

import torch
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fl import FLServer, RemoteClient
from metrics import SEQ_LEN, evaluate
from model import NextWordModel
from vocab import Vocab, tokenize

torch.manual_seed(0)

ROOT = Path(__file__).parent.parent
ART = ROOT / "artifacts"
N_CLIENTS = int(os.environ.get("N_CLIENTS", 12))
BASE_PORT = 9001

for f in ("vocab.json", "baseline.pt", "reference.json"):
    if not (ART / f).exists():
        raise SystemExit(f"artifacts/{f} missing. Run: python make_baseline.py")

# The server holds: a vocab file, two models, and a validation set used only for testing.
# It never opens any client's text.
val_lines = [l.strip() for l in (ROOT / "data" / "val.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
vocab = Vocab(json.loads((ART / "vocab.json").read_text(encoding="utf-8")))
reference = json.loads((ART / "reference.json").read_text(encoding="utf-8"))

baseline = NextWordModel(len(vocab))
baseline.load_state_dict(torch.load(ART / "baseline.pt"))
baseline.eval()

fed = FLServer(
    model=NextWordModel(len(vocab)),
    vocab=vocab,
    clients=[],
    val_lines=val_lines,
    weights_path=ART / "federated.pt",
    history_path=ART / "fl_history.json",
)


def discover():
    """Find the client processes that are currently running."""
    found = []
    for i in range(N_CLIENTS):
        try:
            found.append(RemoteClient(f"http://127.0.0.1:{BASE_PORT + i}"))
        except Exception:
            pass
    fed.clients = found
    return found


print("clients found:", [(c.cid, c.n) for c in discover()])

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
    return [vocab.itos[i] for i in torch.topk(logits, k).indices.tolist()]


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
    return {"ok": True, "vocab_size": len(vocab), "fl_round": fed.round,
            "clients_online": len(fed.clients)}


@app.get("/evaluate")
def evaluate_endpoint():
    return {
        "baseline": evaluate(baseline, vocab, val_lines),
        "federated": fed._evaluate(),
        "fl_round": fed.round,
        "frequency_baseline": reference,
    }


@app.get("/fl/clients")
def fl_clients():
    return [{"cid": c.cid, "samples": c.n, "url": c.url} for c in discover()]

@app.post("/fl/personalize/{cid}")
def fl_personalize(cid: str, epochs: int = 8, lr: float = 0.003):
    c = next((c for c in discover() if c.cid == cid), None)
    if c is None:
        raise HTTPException(404, f"client {cid} is not online")
    with fed.lock:
        state = {k: v.detach().clone() for k, v in fed.model.state_dict().items()}
    return c.personalize(state, epochs, lr)  # the server only hands out the global model


class FLConfig(BaseModel):
    rounds: int = 20
    clients_per_round: int = 6
    local_epochs: int = 2
    lr: float = 0.005


@app.post("/fl/start")
def fl_start(cfg: FLConfig):
    if not discover():
        return {"started": False, "message": "no client processes found, run .\\run_clients.ps1"}
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

