import argparse
import io
import json
from pathlib import Path

import torch
import uvicorn
from fastapi import FastAPI, Request, Response

from fl import train_on
from metrics import make_samples
from model import NextWordModel
from vocab import Vocab

ROOT = Path(__file__).parent.parent


def create_app(cid: str, data_path: Path) -> FastAPI:
    # The vocab is a fixed list shipped to every device; no pooled text is needed.
    vocab = Vocab(json.loads((ROOT / "artifacts" / "vocab.json").read_text(encoding="utf-8")))
    lines = [l.strip() for l in data_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    x, y = make_samples(lines, vocab)  # this client's private data, in memory only
    print(f"[{cid}] loaded {len(y)} private training samples")

    app = FastAPI()

    @app.get("/info")
    def info():
        return {"cid": cid, "n": len(y)}  # a count, never the text

    @app.post("/train")
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
        print(f"[{cid}] trained {epochs} epoch(s), loss={loss:.3f}")
        return Response(out.getvalue(), media_type="application/octet-stream")

    return app


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--cid", required=True)
    p.add_argument("--data", required=True, help="this client's private text file")
    p.add_argument("--port", type=int, required=True)
    a = p.parse_args()
    uvicorn.run(create_app(a.cid, Path(a.data)), host="127.0.0.1", port=a.port, log_level="warning")