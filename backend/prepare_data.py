import re
from pathlib import Path

RAW = Path(__file__).parent.parent / "data" / "corpus.txt"
OUT = Path(__file__).parent.parent / "data"
(OUT / "clients").mkdir(exist_ok=True)

text = RAW.read_text(encoding="utf-8")

# 1) split off your hand-written chat lines (everything before the book)
book_start = text.find("Project Gutenberg's The Adventures")
chat_part = text[:book_start]

# 2) strip Gutenberg header/footer
START = "*** START OF THIS PROJECT GUTENBERG EBOOK"
END = "*** END OF THIS PROJECT GUTENBERG EBOOK"
book = text[text.find(START):text.find(END)]
book = book.split("\n", 1)[1]

# 3) split into the 12 stories by their ALL-CAPS headings (contents list is mixed case, so it's skipped)
heading = re.compile(
    r"^\s*(?:XII|XI|X|IX|VIII|VII|VI|V|IV|III|II|I)\.\s+[A-Z][A-Z’' ,\-]+$", re.M
)
parts = heading.split(book)[1:]  # drop front matter
print("stories found:", len(parts))  # should be 12


def clean_sentences(raw: str):
    raw = (raw.replace("’", "'").replace("‘", "'")
              .replace("“", '"').replace("”", '"')
              .replace("—", " ").replace("_", ""))
    sents = []
    for para in re.split(r"\n\s*\n", raw):
        para = " ".join(para.split())
        for s in re.split(r"(?<=[.!?])\s+", para):
            words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)*", s)
            if 3 <= len(words) <= 30:
                sents.append(" ".join(words).lower())
    return sents


val = []
for i, body in enumerate(parts, 1):
    sents = clean_sentences(body)
    # hold out every 10th sentence for validation
    val += sents[9::10]
    train = [s for j, s in enumerate(sents) if j % 10 != 9]
    (OUT / "clients" / f"holmes_{i:02d}.txt").write_text("\n".join(train), encoding="utf-8")
    print(f"client {i:02d}: {len(train)} sentences")

chat = [l.strip().lower() for l in chat_part.splitlines() if l.strip()]
(OUT / "chat.txt").write_text("\n".join(chat), encoding="utf-8")
(OUT / "val.txt").write_text("\n".join(val), encoding="utf-8")

# one combined file for the centralized baseline
all_train = []
for f in sorted((OUT / "clients").glob("*.txt")):
    all_train += f.read_text(encoding="utf-8").splitlines()
(OUT / "clean_corpus.txt").write_text("\n".join(all_train + chat), encoding="utf-8")
print("total train sentences:", len(all_train) + len(chat), "| val:", len(val))