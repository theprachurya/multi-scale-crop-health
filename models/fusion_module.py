import torch
import torch.nn as nn

class ConcatFusion(nn.Module):
    """Concatenates feature vectors from all active branches."""
    def __init__(self, input_dims: list):
        super().__init__()
        self.output_dim = sum(input_dims)
        self.last_weights = None

    def forward(self, features: list):
        # features is a list of tensors from active modalities
        if len(features) == 0:
            raise ValueError("No features provided to ConcatFusion.")

        # Uniform placeholder weights are exposed for API consistency.
        num_modalities = len(features)
        batch_size = features[0].shape[0]
        self.last_weights = torch.full(
            (batch_size, num_modalities),
            1.0 / num_modalities,
            device=features[0].device,
            dtype=features[0].dtype,
        )
        return torch.cat(features, dim=1)

    def get_last_weights(self):
        return self.last_weights

class AttentionFusion(nn.Module):
    """Cross-modal self-attention in a shared embedding space."""
    def __init__(self, input_dims: list, embed_dim: int = 512, num_heads: int = 4, dropout: float = 0.1):
        super().__init__()
        self.projections = nn.ModuleList([nn.Linear(in_dim, embed_dim) for in_dim in input_dims])
        self.self_attn = nn.MultiheadAttention(
            embed_dim=embed_dim,
            num_heads=num_heads,
            dropout=dropout,
            batch_first=True,
        )
        self.norm = nn.LayerNorm(embed_dim)
        self.output_dim = embed_dim
        self.last_weights = None
        
    def forward(self, features: list):
        if len(features) == 0:
            raise ValueError("No features provided to AttentionFusion.")

        tokens = [proj(feat) for proj, feat in zip(self.projections, features)]
        x = torch.stack(tokens, dim=1)  # [B, M, D]

        attn_out, attn_scores = self.self_attn(x, x, x, need_weights=True, average_attn_weights=False)
        x = self.norm(x + attn_out)

        # Approximate per-modality importance by averaging query/key attention.
        # attn_scores shape: [B, heads, M, M]
        self.last_weights = attn_scores.mean(dim=(1, 2)).detach()

        return x.mean(dim=1)

    def get_last_weights(self):
        return self.last_weights


class LearnedGatingFusion(nn.Module):
    """Projects each modality then learns sample-wise softmax gates."""

    def __init__(self, input_dims: list, output_dim: int = 512, gate_hidden_dim: int = 256):
        super().__init__()
        self.projections = nn.ModuleList([nn.Linear(in_dim, output_dim) for in_dim in input_dims])
        self.gates = nn.ModuleList([
            nn.Sequential(
                nn.Linear(output_dim, gate_hidden_dim),
                nn.ReLU(inplace=True),
                nn.Linear(gate_hidden_dim, 1),
            )
            for _ in input_dims
        ])
        self.output_dim = output_dim
        self.last_weights = None

    def forward(self, features: list):
        if len(features) == 0:
            raise ValueError("No features provided to LearnedGatingFusion.")

        projected = [proj(feat) for proj, feat in zip(self.projections, features)]
        gate_logits = torch.cat([gate(feat) for gate, feat in zip(self.gates, projected)], dim=1)
        weights = torch.softmax(gate_logits, dim=1)  # [B, M]

        fused = 0
        for i, feat in enumerate(projected):
            fused = fused + weights[:, i:i+1] * feat

        self.last_weights = weights.detach()
        return fused

    def get_last_weights(self):
        return self.last_weights


class ScalarWeightedFusion(nn.Module):
    """Learnable global scalar weights with projection to a shared space."""

    def __init__(self, input_dims: list, output_dim: int = 512):
        super().__init__()
        if len(input_dims) == 0:
            raise ValueError("input_dims must not be empty.")
        self.projections = nn.ModuleList([nn.Linear(in_dim, output_dim) for in_dim in input_dims])
        self.weight_logits = nn.Parameter(torch.zeros(len(input_dims), dtype=torch.float32))
        self.output_dim = output_dim
        self.last_weights = None

    def forward(self, features: list):
        if len(features) == 0:
            raise ValueError("No features provided to ScalarWeightedFusion.")

        projected = [proj(feat) for proj, feat in zip(self.projections, features)]
        weights = torch.softmax(self.weight_logits, dim=0)  # [M]

        fused = 0
        for i, feat in enumerate(projected):
            fused = fused + weights[i] * feat

        # Repeat per batch to keep API consistent with other fusion modules.
        batch_size = projected[0].shape[0]
        self.last_weights = weights.unsqueeze(0).repeat(batch_size, 1).detach()
        return fused

    def get_last_weights(self):
        return self.last_weights
