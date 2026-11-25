import json
from pathlib import Path

import torch

from fl import train_on
from metrics import frequency_baseline, make_samples
from model import NextWordModel
from vocab import Vocab

torch.manual_seed(0)
ROOT = Path(__file__).parent.parent
DATA, ART = ROOT / "data", ROOT / "artifacts"
ART.mkdir(exist_ok=True)


def read_lines(p):
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


train_lines = read_lines(DATA / "clean_corpus.txt")
val_lines = read_lines(DATA / "val.txt")

if (ART / "vocab.json").exists():
    vocab = Vocab(json.loads((ART / "vocab.json").read_text(encoding="utf-8")))
    print("vocab.json exists, keeping it")
else:
    vocab = Vocab.build(train_lines, max_size=5000)
    (ART / "vocab.json").write_text(json.dumps(vocab.itos[2:]), encoding="utf-8")
    print("created vocab.json")

if (ART / "baseline.pt").exists():
    print("baseline.pt exists, keeping it")
else:
    model = NextWordModel(len(vocab))
    x, y = make_samples(train_lines, vocab)
    loss = train_on(model, x, y, epochs=40, lr=0.005, batch_size=64)
    torch.save(model.state_dict(), ART / "baseline.pt")
    print(f"trained baseline, loss={loss:.3f}")

ref = frequency_baseline(vocab, train_lines, val_lines)
(ART / "reference.json").write_text(json.dumps(ref), encoding="utf-8")
print("reference.json:", ref)