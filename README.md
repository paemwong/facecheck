# FaceCheck - AI Face Detector

Deep learning-based detection of AI-generated faces. Streamlit app, Xception (timm `legacy_xception`) classifier, built for Streamlit Community Cloud.

## Project structure

```
facecheck/
├── app.py                  # single-page UI
├── requirements.txt
├── .gitignore
├── .streamlit/config.toml  # navy theme + upload limit
├── models/                 # put your .pth here
└── utils/
    ├── config.py           # all settings that must match training (edit branding here)
    ├── preprocessing.py    # validation + the exact training eval pipeline
    ├── face_detection.py   # OpenCV Haar face check and crop
    ├── model_loader.py     # rebuilds Xception + loads state_dict
    └── styles.py           # CSS
```

## Preprocessing (matches your training script)

| Step | Value |
|---|---|
| Color | RGB (PIL) |
| Resize | plain resize to 299x299, bilinear, no crop |
| Filter | `cv2.bilateralFilter(d=9, sigmaColor=75, sigmaSpace=75)` after resize |
| Scale | 0-255 to 0-1, then `(x - 0.5) / 0.5` giving -1 to 1 |
| Layout | channels-first (1, 3, 299, 299) |
| Head | `Dropout(0.5)` + `Linear(2048, 2)`, softmax over 2 logits |
| Labels | `fake = 0`, `real = 1` (ImageFolder alphabetical order) |

If your class folders are not named `fake` and `real`, or your training log shows a different
`Class to index`, change it in the app's settings panel (or `DEFAULT_CLASS_NAMES` in `utils/config.py`).

## Run locally (Windows, VS Code)

1. Install Python 3.11 or 3.12 from python.org (tick "Add python.exe to PATH").
2. Open the `facecheck` folder in VS Code, then open a terminal (Ctrl + `).
3. Create and activate a virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, or use `.venv\Scripts\activate.bat` in Command Prompt.
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Copy your trained file (for example `xception_ai_face_detector_xception_with_aug.pth`) into `models/`.
6. Start the app:
   ```powershell
   streamlit run app.py
   ```
   It opens at http://localhost:8501.

In VS Code, press Ctrl+Shift+P, choose "Python: Select Interpreter" and pick `.venv` so imports resolve.

## Changing the model

Open "Model and detection settings" on the page. You can pick any `.pth` in `models/`, upload a different `.pth` directly in the browser, or paste a direct download link (for example a Hugging Face `resolve/main/...pth` URL). The new file must be a `state_dict` of the same architecture (`legacy_xception` with the Dropout/Linear(2) head). A different backbone needs changes in `utils/config.py` and `utils/model_loader.py`.

## Deploy to Streamlit Community Cloud

1. Create a GitHub account and a new **public** repository (free tier).
2. Push the project:
   ```powershell
   git init
   git add .
   git commit -m "FaceCheck FYP"
   git branch -M main
   git remote add origin https://github.com/<your-username>/facecheck.git
   git push -u origin main
   ```
   Your `.pth` is roughly 80-90 MB, below GitHub's 100 MB hard limit (GitHub warns above 50 MB). If yours is larger, either use Git LFS or host it on Hugging Face and use the "Download from URL" option.
3. Go to https://share.streamlit.io, sign in with GitHub, click **Create app**, and choose the repository, branch `main` and main file `app.py`.
4. Open **Advanced settings** and select Python 3.11 or 3.12, then click **Deploy**. The first build takes a few minutes while PyTorch installs.

Notes:
- `requirements.txt` uses the CPU-only PyTorch index to keep the install small. This is enough for single-image inference.
- Free apps sleep after inactivity; the first request after waking reloads the model (a few seconds).
- No `packages.txt` is needed because `opencv-python-headless` has no system dependencies.

## Troubleshooting

| Problem | Fix |
|---|---|
| `legacy_xception` not found | `pip install -U timm` (version 0.9.12 or newer) |
| "does not match the expected architecture" | The `.pth` was trained with a different backbone or head |
| Every prediction looks flipped | Change the class-index option in settings |
| No face detected on a valid photo | Use a front-facing, well-lit photo, or untick "Require a detectable face" |
| Build fails on Streamlit Cloud | Choose Python 3.11 in Advanced settings and reboot the app |
