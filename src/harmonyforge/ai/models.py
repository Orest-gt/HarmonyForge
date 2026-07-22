"""
Custom lightweight AI models for HarmonyForge.
"""

import torch
import torch.nn as nn
from typing import List


class LightweightStylePredictor(nn.Module):
    """
    A lightweight PyTorch neural network that maps a tokenized text prompt
    (e.g., "dark trap beat like metro boomin") to a StyleSignature tensor.
    """
    def __init__(self, vocab_size: int = 1000, embed_dim: int = 32, hidden_dim: int = 64, output_features: int = 8):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, embed_dim)
        self.fc1 = nn.Linear(embed_dim, hidden_dim)
        self.relu = nn.ReLU()
        # Outputs map to [harmonic_complexity, dissonance, modal_prob, syncopation, repetition, darkness, tension, rhythmic_density]
        self.fc2 = nn.Linear(hidden_dim, output_features)
        self.sigmoid = nn.Sigmoid()  # Scale outputs between 0.0 and 1.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x is [batch_size, sequence_length]
        embedded = self.embed(x)
        # Simple Bag of Words (average pooling)
        pooled = embedded.mean(dim=1)
        hidden = self.relu(self.fc1(pooled))
        out: torch.Tensor = self.sigmoid(self.fc2(hidden))
        return out


def mock_predict_style(prompt: str) -> List[float]:
    """
    Mock inference using the initialized lightweight model.
    In a full production environment, we would load pre-trained weights.
    """
    model = LightweightStylePredictor()
    model.eval()

    # Mock tokenization (hash words to vocab)
    tokens = [abs(hash(w)) % 1000 for w in prompt.lower().split()]
    if not tokens:
        tokens = [0]

    input_tensor = torch.tensor([tokens], dtype=torch.long)

    with torch.no_grad():
        output = model(input_tensor)

    result: List[float] = list(output[0].tolist())
    return result
