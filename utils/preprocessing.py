"""Upload validation and the inference preprocessing pipeline.

The pipeline mirrors `eval_transform` from the training script exactly:

    PIL RGB image
      -> Resize((299, 299))                       (plain resize, bilinear, no crop)
      -> cv2.bilateralFilter(d=9, 75, 75)         (applied to the RGB array)
      -> ToTensor()                               (uint8 0-255 -> float 0-1, HWC -> CHW)
      -> Normalize(mean=0.5, std=0.5)             (range becomes -1 to 1)

This module is torch-free on purpose (returns a NumPy array) so it is easy to test.
"""
from __future__ import annotations

import io
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

from . import config as cfg

Image.MAX_IMAGE_PIXELS = cfg.MAX_PIXELS  # guard against decompression bombs


class ImageValidationError(Exception):
    """Raised with a user-friendly message when an upload cannot be used."""


def load_and_validate(data: bytes, filename: str) -> Image.Image:
    """Validate the raw upload and return an RGB PIL image."""
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext not in cfg.ALLOWED_EXTENSIONS:
        raise ImageValidationError(
            f"Unsupported file type '.{ext}'. Please upload a JPG, JPEG or PNG image."
        )
    if len(data) == 0:
        raise ImageValidationError("The file is empty.")
    if len(data) > cfg.MAX_FILE_MB * 1024 * 1024:
        raise ImageValidationError(
            f"The file is larger than {cfg.MAX_FILE_MB} MB. Please upload a smaller image."
        )

    try:
        with Image.open(io.BytesIO(data)) as probe:
            fmt = probe.format
            probe.verify()  # detects truncated / corrupt files
    except Exception:
        raise ImageValidationError(
            "This file could not be read as an image. It may be corrupted or not a real image."
        )

    if fmt not in cfg.ALLOWED_FORMATS:
        raise ImageValidationError(
            f"The file content is {fmt or 'unknown'}, not JPEG or PNG. "
            "Renaming a file does not convert it; please export it as JPG or PNG."
        )

    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        img = ImageOps.exif_transpose(img)  # fix phone-camera rotation
        img = img.convert("RGB")
    except Exception:
        raise ImageValidationError("The image could not be decoded. Please try another file.")

    if min(img.size) < cfg.MIN_SIDE_PX:
        raise ImageValidationError(
            f"The image is too small ({img.width}x{img.height}px). "
            f"Both sides must be at least {cfg.MIN_SIDE_PX}px."
        )
    return img


def preprocess_to_array(img: Image.Image) -> np.ndarray:
    """RGB PIL image -> float32 array of shape (1, 3, 299, 299), values in [-1, 1]."""
    img = img.convert("RGB")
    # torchvision.transforms.Resize on a PIL image == PIL bilinear resize
    img = img.resize((cfg.IMG_SIZE, cfg.IMG_SIZE), Image.Resampling.BILINEAR)

    arr = np.array(img)  # uint8, HWC, RGB (same as training's np.array(PIL image))
    arr = cv2.bilateralFilter(arr, **cfg.BILATERAL)

    arr = arr.astype(np.float32) / 255.0            # ToTensor scaling
    arr = (arr - cfg.NORM_MEAN) / cfg.NORM_STD      # Normalize(0.5, 0.5)
    arr = np.transpose(arr, (2, 0, 1))              # HWC -> CHW (channels-first)
    return np.ascontiguousarray(arr[None, ...])     # add batch dimension
