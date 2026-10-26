"""Central configuration. Values here MUST match the training script (train_xception.py)."""
from pathlib import Path

# ---- Branding ---------------------------------------------------------------
APP_NAME = "FaceCheck - AI Face Detector"
SUBTITLE = "Deep Learning-Based Detection of AI-Generated Faces"
PROJECT_CREDIT = "Final Year Project, Fahim, UiTM"  # <-- EDIT ME

# ---- Paths ------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = ROOT / "models"

# ---- Model (copied from the training script) -------------------------------
TIMM_MODEL_NAME = "legacy_xception"   # TIMM_MODEL_NAME in training
IMG_SIZE = 299                        # IMG_SIZE in training
NORM_MEAN = 0.5                       # NORM_MEAN = [0.5, 0.5, 0.5]
NORM_STD = 0.5                        # NORM_STD  = [0.5, 0.5, 0.5]
NUM_CLASSES = 2                       # head = Dropout(0.5) + Linear(2048, 2)
DROPOUT = 0.5

# Bilateral filter used in training (FILTER_METHOD = "bilateral")
BILATERAL = dict(d=9, sigmaColor=75, sigmaSpace=75)

# ImageFolder sorts class folders alphabetically: fake -> 0, real -> 1.
# (Changeable at runtime in the app's settings panel.)
DEFAULT_CLASS_NAMES = ("fake", "real")
DISPLAY_NAMES = {"fake": "AI-Generated", "real": "Real"}

# ---- Upload validation -------------------------------------------------------
ALLOWED_EXTENSIONS = ("jpg", "jpeg", "png")
ALLOWED_FORMATS = ("JPEG", "PNG")
MAX_FILE_MB = 10
MIN_SIDE_PX = 64
MAX_PIXELS = 50_000_000

# ---- Face check --------------------------------------------------------------
MIN_FACE_PX = 48              # smallest face width accepted (original pixels)
CROP_IF_FACE_FRACTION = 0.45  # auto-crop only if face width < 45% of the short side
CROP_MARGIN = 0.45            # context kept around the face box when cropping

# ---- Result display ----------------------------------------------------------
LOW_CONFIDENCE = 0.70
