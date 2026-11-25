import argparse
import io
import json
import random
from pathlib import Path

import torch
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fl import train_on
from metrics import SEQ_LEN, make_samples
from model import NextWordModel
from vocab import Vocab, tokenize

ROOT = Path(__file__).parent.parent
DEVICE_DIR = ROOT / "artifacts" / "devices"  # this phone's own storage


class PredictIn(BaseModel):
    text: str
    k: int = 3
    which: str = "personal"  # "personal" or "global"


def create_app(cid: str, data_path: Path) -> FastAPI:
    DEVICE_DIR.mkdir(parents=True, exist_ok=True)
    vocab = Vocab(json.loads((ROOT / "artifacts" / "vocab.json").read_text(encoding="utf-8")))
    lines = [l.strip() for l in data_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    x, y = make_samples(lines, vocab)  # private data, in memory only
    print(f"[{cid}] loaded {len(y)} private training samples")

    paths = {"global": DEVICE_DIR / f"{cid}_global.pt", "personal": DEVICE_DIR / f"{cid}_personal.pt"}
    models = {"global": None, "personal": None}

    def load(state):
        m = NextWordModel(len(vocab))
        m.load_state_dict(state)
        m.eval()
        return m

    for name, p in paths.items():  # restore what this phone stored last time
        if p.exists():
            models[name] = load(torch.load(p))
            print(f"[{cid}] restored {name} model from device storage")

    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

    @app.get("/info")
    def info():
        return {"cid": cid, "n": len(y)}

    @app.get("/status")
    def status():
        return {"cid": cid, "has_global": models["global"] is not None,
                "has_personal": models["personal"] is not None}

    @app.get("/sample")
    def sample(n: int = 5):
        # the phone showing its OWN data to its own screen
        return {"lines": random.sample(lines, min(n, len(lines)))}

    @app.post("/train")  # one federated round: train locally, return weights only
    async def train(request: Request, epochs: int = 1, lr: float = 0.005):
        state = torch.load(io.BytesIO(await request.body()), weights_only=True)
        model = NextWordModel(len(vocab))
        model.load_state_dict(state)
        loss = train_on(model, x, y, epochs=epochs, lr=lr, batch_size=64)
        out = io.BytesIO()
        torch.save({
            "weights": {k: v.detach().clone() for k, v in model.state_dict().items()},
            "n": len(y),
            "loss": loss,
        }, out)
        print(f"[{cid}] federated round: trained {epochs} epoch(s), loss={loss:.3f}")
        return Response(out.getvalue(), media_type="application/octet-stream")

    @app.post("/personalize")  # download global model, then adapt it on-device
    async def personalize(request: Request, epochs: int = 8, lr: float = 0.003):
        state = torch.load(io.BytesIO(await request.body()), weights_only=True)
        models["global"] = load(state)
        torch.save(state, paths["global"])
        personal = load(state)
        loss = train_on(personal, x, y, epochs=epochs, lr=lr, batch_size=32)
        personal.eval()
        models["personal"] = personal
        torch.save(personal.state_dict(), paths["personal"])
        print(f"[{cid}] personalized on-device, loss={loss:.3f}")
        return {"cid": cid, "loss": round(loss, 3), "epochs": epochs}

    @app.post("/predict")
    def predict(body: PredictIn):
        model = models["personal"] if body.which == "personal" else models["global"]
        if model is None:
            raise HTTPException(409, "this phone has no model yet")
        ids = vocab.encode(tokenize(body.text))[-SEQ_LEN:]
        ids = [0] * (SEQ_LEN - len(ids)) + ids
        with torch.no_grad():
            logits = model(torch.tensor([ids]))[0]
        logits[0] = float("-inf")  # <pad>
        logits[1] = float("-inf")  # <unk>
        return {"suggestions": [vocab.itos[i] for i in torch.topk(logits, body.k).indices.tolist()]}

    return app


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--cid", required=True)
    p.add_argument("--data", required=True, help="this client's private text file")
    p.add_argument("--port", type=int, required=True)
    a = p.parse_args()
    uvicorn.run(create_app(a.cid, Path(a.data)), host="127.0.0.1", port=a.port, log_level="warning")