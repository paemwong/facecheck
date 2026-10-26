"""Lightweight face detection using OpenCV Haar cascades (no extra downloads)."""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from . import config as cfg

Box = Tuple[int, int, int, int]  # x, y, w, h
_MAX_DETECT_SIDE = 800


@lru_cache(maxsize=1)
def _cascades():
    base = cv2.data.haarcascades
    names = ("haarcascade_frontalface_alt2.xml", "haarcascade_frontalface_default.xml")
    found = [cv2.CascadeClassifier(base + n) for n in names]
    found = [c for c in found if not c.empty()]
    if not found:
        raise RuntimeError("OpenCV face cascades could not be loaded.")
    return found


def _run(gray: np.ndarray) -> List[Box]:
    min_size = max(24, int(0.06 * min(gray.shape)))
    for cascade in _cascades():
        faces = cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(min_size, min_size)
        )
        if len(faces):
            return [tuple(int(v) for v in f) for f in faces]
    return []


def detect_faces(img: Image.Image) -> List[Box]:
    """Return face boxes in original-image pixels, largest first."""
    gray = np.array(img.convert("L"))
    h, w = gray.shape
    scale = min(1.0, _MAX_DETECT_SIDE / max(h, w))
    if scale < 1.0:
        gray = cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    gray = cv2.equalizeHist(gray)

    boxes = _run(gray)
    if not boxes:
        # Tightly framed portraits (like the training data) can defeat Haar cascades,
        # so retry with a border of extra context around the image.
        pad = int(0.4 * max(gray.shape))
        padded = cv2.copyMakeBorder(gray, pad, pad, pad, pad, cv2.BORDER_REPLICATE)
        boxes = [(x - pad, y - pad, bw, bh) for (x, y, bw, bh) in _run(padded)]

    out = []
    for x, y, bw, bh in boxes:
        x, y = max(0, x), max(0, y)
        out.append((int(x / scale), int(y / scale), int(bw / scale), int(bh / scale)))
    out.sort(key=lambda b: b[2] * b[3], reverse=True)
    return out


def best_face(faces: List[Box]) -> Optional[Box]:
    """Largest face, if it is big enough to be usable."""
    if faces and faces[0][2] >= cfg.MIN_FACE_PX:
        return faces[0]
    return None


def should_crop(img: Image.Image, face: Box) -> bool:
    """Crop only when the face is small in the frame (training images are face-filling)."""
    return face[2] / min(img.size) < cfg.CROP_IF_FACE_FRACTION


def crop_to_face(img: Image.Image, face: Box) -> Image.Image:
    """Square crop around the face with some context, kept inside the image."""
    x, y, w, h = face
    cx, cy = x + w / 2, y + h / 2
    side = min(max(w, h) * (1 + 2 * cfg.CROP_MARGIN), img.width, img.height)
    left = min(max(cx - side / 2, 0), img.width - side)
    top = min(max(cy - side / 2, 0), img.height - side)
    return img.crop((int(left), int(top), int(left + side), int(top + side)))
