import torch
import torch.nn as nn


class NextWordModel(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 64, hidden_dim: int = 128):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.gru = nn.GRU(embed_dim, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        # x: (batch, seq_len) of word ids
        emb = self.embed(x)
        out, _ = self.gru(emb)
        return self.fc(out[:, -1, :])  # logits for the next word