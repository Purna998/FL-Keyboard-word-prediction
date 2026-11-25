import io
import json
import random
import threading
import time
from pathlib import Path

import requests
import torch
import torch.nn as nn

from metrics import evaluate
from model import NextWordModel


def train_on(model, x, y, epochs=1, lr=0.005, batch_size=64):
    """Plain minibatch training. Used by the baseline and by every client node."""
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()
    model.train()
    avg = 0.0
    for _ in range(epochs):
        perm = torch.randperm(len(x))
        total = 0.0
        for i in range(0, len(x), batch_size):
            idx = perm[i:i + batch_size]
            opt.zero_grad()
            loss = loss_fn(model(x[idx]), y[idx])
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            total += loss.item() * len(idx)
        avg = total / len(x)
    return avg


def fedavg(updates):
    """updates: list of (state_dict, num_samples). Weighted average of weights."""
    total = sum(n for _, n in updates)
    return {k: sum(sd[k] * (n / total) for sd, n in updates) for k in updates[0][0]}


class RemoteClient:
    """Server-side stub for a phone running in its own process.
    The server only ever sees weights and a sample count, never text."""

    def __init__(self, url):
        self.url = url.rstrip("/")
        info = requests.get(f"{self.url}/info", timeout=2).json()
        self.cid = info["cid"]
        self.n = info["n"]

    def train(self, global_state, vocab_size, epochs, lr):
        buf = io.BytesIO()
        torch.save(global_state, buf)
        r = requests.post(
            f"{self.url}/train",
            params={"epochs": epochs, "lr": lr},
            data=buf.getvalue(),
            timeout=600,
        )
        r.raise_for_status()
        out = torch.load(io.BytesIO(r.content), weights_only=True)
        return out["weights"], out["n"], out["loss"]

    def personalize(self, global_state, epochs, lr):
        buf = io.BytesIO()
        torch.save(global_state, buf)
        r = requests.post(
            f"{self.url}/personalize",
            params={"epochs": epochs, "lr": lr},
            data=buf.getvalue(),
            timeout=600,
        )
        r.raise_for_status()
        return r.json()

class FLServer:
    def __init__(self, model, vocab, clients, val_lines, weights_path, history_path):
        self.model = model
        self.vocab = vocab
        self.clients = clients
        self.val_lines = val_lines
        self.weights_path = Path(weights_path)
        self.history_path = Path(history_path)
        self.lock = threading.Lock()
        self.running = False
        self.error = None
        self.history = []
        if self.weights_path.exists():
            self.model.load_state_dict(torch.load(self.weights_path))
        if self.history_path.exists():
            self.history = json.loads(self.history_path.read_text())

    @property
    def round(self):
        return self.history[-1]["round"] if self.history else 0

    def _evaluate(self):
        with self.lock:
            return evaluate(self.model, self.vocab, self.val_lines)

    def _save(self):
        torch.save(self.model.state_dict(), self.weights_path)
        self.history_path.write_text(json.dumps(self.history))

    def run_round(self, clients_per_round, local_epochs, lr):
        t0 = time.time()
        chosen = random.sample(self.clients, min(clients_per_round, len(self.clients)))
        global_state = {k: v.detach().clone() for k, v in self.model.state_dict().items()}

        updates, losses, used = [], [], []
        for c in chosen:
            try:
                weights, n, loss = c.train(global_state, len(self.vocab), local_epochs, lr)
            except Exception as e:  # a phone went offline: skip it, like a real dropout
                print(f"client {c.cid} failed: {e!r}")
                continue
            updates.append((weights, n))
            losses.append(loss)
            used.append(c.cid)
        if not updates:
            raise RuntimeError("no clients responded")

        new_state = fedavg(updates)
        with self.lock:
            self.model.load_state_dict(new_state)

        m = self._evaluate()
        entry = {
            "round": self.round + 1,
            "clients": used,
            "avg_loss": round(sum(losses) / len(losses), 3),
            "top1": m["top1"], "top3": m["top3"], "top5": m["top5"],
            "perplexity": m["perplexity"],
            "seconds": round(time.time() - t0, 1),
        }
        self.history.append(entry)
        self._save()
        return entry

    def run(self, rounds, clients_per_round, local_epochs, lr):
        self.error = None
        try:
            if not self.history:  # record the untrained starting point as round 0
                m = self._evaluate()
                self.history.append({
                    "round": 0, "clients": [], "avg_loss": None,
                    "top1": m["top1"], "top3": m["top3"], "top5": m["top5"],
                    "perplexity": m["perplexity"], "seconds": 0,
                })
            for _ in range(rounds):
                self.run_round(clients_per_round, local_epochs, lr)
        except Exception as e:
            self.error = repr(e)
        finally:
            self.running = False

    def start(self, **cfg):
        if self.running:
            return False
        self.running = True
        threading.Thread(target=self.run, kwargs=cfg, daemon=True).start()
        return True

    def reset(self):
        with self.lock:
            self.model.load_state_dict(NextWordModel(len(self.vocab)).state_dict())
        self.history = []
        self.weights_path.unlink(missing_ok=True)
        self.history_path.unlink(missing_ok=True)