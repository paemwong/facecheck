"""FaceCheck - AI Face Detector (single-page Streamlit app)."""
from __future__ import annotations

import hashlib
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

from utils import config as cfg
from utils.face_detection import best_face, crop_to_face, detect_faces, should_crop
from utils.model_loader import ModelLoadError, count_params, load_model, predict_probs
from utils.preprocessing import ImageValidationError, load_and_validate, preprocess_to_array
from utils.styles import CSS

st.set_page_config(page_title=cfg.APP_NAME, page_icon="🛡️", layout="wide",
                   initial_sidebar_state="collapsed")

TMP_DIR = Path(tempfile.gettempdir()) / "facecheck_models"
SRC_BUNDLED, SRC_UPLOAD, SRC_URL = "Bundled model (models folder)", "Upload a .pth file", "Download from URL"


# --------------------------------------------------------------------------- state
def init_state():
    for key, default in (("uploader_key", 0), ("result", None), ("url_model", None)):
        st.session_state.setdefault(key, default)


# --------------------------------------------------------------------------- cached work
@st.cache_data(show_spinner=False, max_entries=8)
def inspect_image(data: bytes, name: str):
    """Validate the upload and run face detection once per file."""
    try:
        img = load_and_validate(data, name)
    except ImageValidationError as exc:
        return None, [], str(exc)
    return img, detect_faces(img), None


@st.cache_resource(show_spinner=False, max_entries=1)
def cached_model(path: str, mtime: float, size: int):
    return load_model(path)


# --------------------------------------------------------------------------- model source
def download_model(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Please enter a direct https:// link to the .pth file.")
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    target = TMP_DIR / f"url_{hashlib.sha256(url.encode()).hexdigest()[:16]}.pth"
    req = urllib.request.Request(url.strip(), headers={"User-Agent": "FaceCheck/1.0"})
    limit = 300 * 1024 * 1024
    written = 0
    with urllib.request.urlopen(req, timeout=60) as resp, open(target, "wb") as out:
        while chunk := resp.read(1 << 20):
            written += len(chunk)
            if written > limit:
                raise ValueError("The file is larger than 300 MB.")
            out.write(chunk)
    return str(target)


def model_and_settings():
    """Settings panel. Returns (model, model_label, class_names, require_face, auto_crop)."""
    ss = st.session_state
    bundled = sorted([*cfg.MODELS_DIR.glob("*.pth"), *cfg.MODELS_DIR.glob("*.pt")])
    path, label, model, error = None, None, None, None

    with st.expander("Model and detection settings", expanded=not bundled):
        source = st.radio("Model source", [SRC_BUNDLED, SRC_UPLOAD, SRC_URL], horizontal=True,
                          index=0 if bundled else 1)

        if source == SRC_BUNDLED:
            if bundled:
                path = st.selectbox("Model file", bundled, format_func=lambda p: p.name)
                label = path.name
            else:
                st.info("No .pth file found in the models folder. Add one there, or switch to "
                        "'Upload a .pth file'.")
        elif source == SRC_UPLOAD:
            up = st.file_uploader("Upload your trained Xception .pth (state_dict)", type=["pth", "pt"],
                                  key="model_uploader")
            if up is not None:
                data = up.getvalue()
                TMP_DIR.mkdir(parents=True, exist_ok=True)
                path = TMP_DIR / f"up_{hashlib.sha256(data).hexdigest()[:16]}.pth"
                if not path.exists():
                    path.write_bytes(data)
                label = up.name
        else:
            url = st.text_input("Direct link to a .pth file",
                                placeholder="https://huggingface.co/<user>/<repo>/resolve/main/model.pth")
            if st.button("Download model"):
                try:
                    with st.spinner("Downloading model..."):
                        ss.url_model = download_model(url)
                except Exception as exc:
                    st.error(f"Download failed: {exc}")
            if ss.url_model and Path(ss.url_model).exists():
                path, label = Path(ss.url_model), "Downloaded model"

        if path is not None:
            try:
                stat = Path(path).stat()
                with st.spinner("Loading model..."):
                    model = cached_model(str(path), stat.st_mtime, stat.st_size)
                st.success(f"Model ready: {label} ({count_params(model) / 1e6:.1f}M parameters, "
                           f"{cfg.TIMM_MODEL_NAME}, {cfg.IMG_SIZE}x{cfg.IMG_SIZE} input)")
            except ModelLoadError as exc:
                error = str(exc)
                st.error(error)

        st.markdown("**Detection options**")
        order = st.radio(
            "Class indices used during training",
            ["fake = 0, real = 1 (default: folders sorted alphabetically)", "real = 0, fake = 1"],
            help="Check the 'Class to index' line printed by your training script. "
                 "Wrong order will flip every prediction.")
        class_names = ("fake", "real") if order.startswith("fake") else ("real", "fake")
        require_face = st.checkbox("Require a detectable face (recommended)", value=True)
        auto_crop = st.checkbox("Crop to the face when it is small in the photo", value=True,
                                help="The training images are close-up faces, so this keeps wide "
                                     "photos closer to what the model was trained on.")
    return model, label, class_names, require_face, auto_crop


# --------------------------------------------------------------------------- UI blocks
def hero():
    st.markdown(f"""
    <div class="hero">
      <h1>FaceCheck - AI Face Detector</h1>
      <div class="subtitle">{cfg.SUBTITLE}</div>
      <p class="desc">FaceCheck uses a deep learning model (Xception convolutional neural network) to
      classify a facial image as a real photograph or an AI-generated face. Upload a photo, and the
      model estimates how likely it is to be authentic.</p>
      <a class="cta" href="#analyze">Start image analysis</a>
      <div class="disclaimer"><b>Disclaimer:</b> Predictions are model estimates and are not definitive
      proof that an image is authentic or AI-generated. Do not use results as the sole basis for
      important decisions.</div>
    </div>
    <div class="steps">
      <div class="step"><b><i>1</i>Upload</b><span>Drop a JPG, JPEG or PNG image containing a face.</span></div>
      <div class="step"><b><i>2</i>Check</b><span>The app validates the file and looks for a usable face.</span></div>
      <div class="step"><b><i>3</i>Analyze</b><span>The model returns a prediction with a confidence score.</span></div>
    </div>
    """, unsafe_allow_html=True)


def bar(name: str, p: float, css: str) -> str:
    return (f'<div class="bar-row"><div class="bar-head"><span>{name}</span><span>{p:.1%}</span></div>'
            f'<div class="bar"><div class="{css}" style="width:{p * 100:.1f}%"></div></div></div>')


def render_result(res: dict, class_names, model_label: str):
    probs = res["probs"]
    by_name = {class_names[i]: probs[i] for i in range(2)}
    pred = max(by_name, key=by_name.get)
    conf = by_name[pred]
    is_fake = pred == "fake"
    low = conf < cfg.LOW_CONFIDENCE
    note = ('<div class="note">Low confidence: the model is unsure about this image. '
            'Treat this result with extra caution.</div>') if low else ""
    cropped = "Face region analysed (auto-cropped)" if res["cropped"] else "Whole image analysed"
    st.markdown(f"""
    <div class="result {'fake' if is_fake else 'real'}">
      <div class="label">Prediction</div>
      <div class="verdict">{cfg.DISPLAY_NAMES[pred]}</div>
      <div class="conf">{conf:.1%} confidence</div>
      {bar(cfg.DISPLAY_NAMES['real'], by_name['real'], 'g')}
      {bar(cfg.DISPLAY_NAMES['fake'], by_name['fake'], 'r')}
      {note}
      <div class="meta">{cropped}<br>Model: {model_label}<br>Inference time: {res['seconds']:.2f} s</div>
    </div>""", unsafe_allow_html=True)
    st.caption("This is a model estimate, not proof of authenticity.")


# --------------------------------------------------------------------------- main
def main():
    init_state()
    ss = st.session_state
    st.markdown(CSS, unsafe_allow_html=True)
    hero()

    st.markdown('<div id="analyze"></div><div class="section-title">Analyze an image</div>'
                '<div class="section-sub">Upload a face image, then press Analyze Image.</div>',
                unsafe_allow_html=True)
    model, model_label, class_names, require_face, auto_crop = model_and_settings()

    left, right = st.columns(2, gap="large")
    img, face, file_id, clicked, ready = None, None, None, False, False

    with left:
        st.markdown('<div class="panel-title">Upload</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader("Drag and drop a JPG, JPEG or PNG image", type=list(cfg.ALLOWED_EXTENSIONS),
                                    key=f"uploader_{ss.uploader_key}", label_visibility="collapsed")
        if uploaded is not None:
            data = uploaded.getvalue()
            file_id = hashlib.md5(data).hexdigest()
            img, faces, err = inspect_image(data, uploaded.name)
            if err:
                st.error(err)
                img = None
            else:
                st.image(img, caption=f"{uploaded.name} ({img.width}x{img.height}px)")
                face = best_face(faces)
                if face:
                    extra = f" ({len(faces)} faces found, largest used)" if len(faces) > 1 else ""
                    st.markdown(f'<span class="pill ok">Face detected{extra}</span>', unsafe_allow_html=True)
                elif require_face:
                    st.error("No usable face detected. Upload a clear, front-facing photo where the "
                             "face is well lit and not covered, or turn off the face requirement in "
                             "the settings above.")
                else:
                    st.markdown('<span class="pill warn">No face detected. Results may be unreliable.</span>',
                                unsafe_allow_html=True)

        ready = img is not None and model is not None and (face is not None or not require_face)
        c1, c2 = st.columns([2, 1])
        clicked = c1.button("Analyze Image", type="primary", disabled=not ready)
        if c2.button("Remove image", disabled=uploaded is None):
            ss.uploader_key += 1
            ss.result = None
            st.rerun()
        if img is not None and model is None:
            st.caption("Load a model in the settings above to enable analysis.")

    with right:
        st.markdown('<div class="panel-title">Result</div>', unsafe_allow_html=True)
        if clicked and ready:
            try:
                with st.spinner("Analyzing image with the deep learning model..."):
                    start = time.perf_counter()
                    region, cropped = img, False
                    if auto_crop and face and should_crop(img, face):
                        region, cropped = crop_to_face(img, face), True
                    probs = predict_probs(model, preprocess_to_array(region))
                    ss.result = dict(file_id=file_id, probs=probs, cropped=cropped,
                                     seconds=time.perf_counter() - start)
            except Exception as exc:
                ss.result = None
                st.error(f"Analysis failed: {exc}")

        res = ss.result
        if res and img is not None and res["file_id"] == file_id:
            render_result(res, class_names, model_label or "model")
        else:
            st.markdown('<div class="placeholder">Your prediction will appear here.<br>'
                        'Upload an image and press <b>Analyze Image</b>.</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="footer">{cfg.APP_NAME}<br>{cfg.PROJECT_CREDIT}<br>'
                'Predictions are model estimates and not definitive proof of authenticity.</div>',
                unsafe_allow_html=True)


main()
