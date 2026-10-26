"""Rebuilds the trained Xception model and loads a state_dict (.pth) into it.

Architecture (identical to training):
    timm.create_model("legacy_xception", pretrained=False)
    model.fc = nn.Sequential(nn.Dropout(0.5), nn.Linear(2048, 2))

The checkpoint is a plain state_dict saved with torch.save(model.state_dict(), path).
"""
from __future__ import annotations

from typing import List

import numpy as np
import timm
import torch
import torch.nn as nn

from . import config as cfg


class ModelLoadError(Exception):
    """Raised with a user-friendly message when a checkpoint cannot be used."""


def build_architecture() -> nn.Module:
    model = timm.create_model(cfg.TIMM_MODEL_NAME, pretrained=False)  # no download
    model.fc = nn.Sequential(
        nn.Dropout(cfg.DROPOUT), nn.Linear(model.fc.in_features, cfg.NUM_CLASSES)
    )
    return model


def _extract_state_dict(ckpt) -> dict:
    if isinstance(ckpt, nn.Module):
        raise ModelLoadError(
            "This file contains a whole pickled model. Please save with "
            "torch.save(model.state_dict(), 'model.pth') and upload that instead."
        )
    if isinstance(ckpt, dict):
        for key in ("state_dict", "model_state_dict", "model"):
            if isinstance(ckpt.get(key), dict):
                ckpt = ckpt[key]
                break
    if not isinstance(ckpt, dict) or not ckpt:
        raise ModelLoadError("The file does not contain a valid state_dict.")
    # Remove the 'module.' prefix added by DataParallel, if present
    return {k[7:] if k.startswith("module.") else k: v for k, v in ckpt.items()}


def load_model(path: str) -> nn.Module:
    try:
        # weights_only=True blocks arbitrary code execution from untrusted pickles
        ckpt = torch.load(path, map_location="cpu", weights_only=True)
    except Exception as exc:
        raise ModelLoadError(
            "The file could not be loaded as a PyTorch state_dict "
            f"(is it a valid .pth file?). Details: {str(exc)[:200]}"
        )

    state = _extract_state_dict(ckpt)
    model = build_architecture()
    try:
        model.load_state_dict(state, strict=True)
    except RuntimeError as exc:
        raise ModelLoadError(
            "The checkpoint does not match the expected architecture "
            "(legacy_xception + Dropout/Linear(2) head). It was probably trained with a "
            f"different backbone or head. Details: {str(exc)[:300]}"
        )
    model.eval()
    return model


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())


def predict_probs(model: nn.Module, batch: np.ndarray) -> List[float]:
    """Softmax probabilities indexed by class index (same as training)."""
    with torch.inference_mode():
        logits = model(torch.from_numpy(batch))
        return torch.softmax(logits, dim=1)[0].tolist()
