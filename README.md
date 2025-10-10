# Speech Emotion Recognition (SER)

A complete pipeline for Speech Emotion Recognition with two complementary approaches:
- Baseline: Tabular features (MFCC, delta, chroma, spectral) + scikit-learn RandomForest
- Deep: Keras CNN trained on log-mel spectrograms (or MFCC tensors)

Includes preprocessing, feature extraction, training, single-file inference, a Flask API, a small web client for recording and uploading audio, evaluation scripts, tests, and Docker packaging.

## Architecture (high-level)
```
Raw audio  ->  Preprocess (trim/pad/augment)  ->  data/clean
                                        \
                                         +-> Feature extraction -> data/features.csv, data/features.npy
                                         +-> (optional) Mel-spectrograms/MFCC tensors -> data/melspec.npy

Baseline path:
  data/features.csv -> train_baseline.py -> models/baseline_rf.joblib
                                                 \
                                                  -> evaluate.py -> reports/*

Deep path:
  data/melspec.npy + labels -> train_deep.py -> models/emotion_cnn.h5
                                                    \
                                                     -> evaluate.py -> reports/*

Serving:
  infer.py (CLI) | Flask app.py (REST) | web/ (record + upload)
```

## Datasets
- RAVDESS: `https://zenodo.org/record/1188976`
- TESS: `https://tspace.library.utoronto.ca/handle/1807/24487`
- SAVEE: `https://kahlan.eps.surrey.ac.uk/savee/`

Use `scripts/download_datasets.py` to index locally existing folders and generate a combined metadata CSV (no network download performed).

## Setup
```bash
# Python venv (Windows PowerShell shown; use your OS equivalent)
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Preprocess and Feature Extraction
```bash
# 1) Preprocess raw audio to fixed 3s clips (with optional augmentation)
python src/preprocess.py --input data/raw --output data/clean --metadata data/clean_metadata.csv --augment 2

# 2) Extract features and optional mel-spectrogram tensors
python src/features.py --input data/clean --csv data/features.csv --npy data/features.npy --melspec data/melspec.npy
```

## Training
- Baseline (RandomForest + GridSearchCV):
```bash
python src/train_baseline.py --csv data/features.csv --model models/baseline_rf.joblib
```
- Deep (Keras CNN on mel-spectrograms or MFCC arrays):
```bash
python src/train_deep.py --melspec data/melspec.npy --labels_csv data/features.csv --epochs 60
# or
python src/train_deep.py --mfcc data/mfcc.npy --labels_csv data/features.csv --epochs 60
```

## Inference (CLI)
```bash
# Baseline
python src/infer.py --model models/baseline_rf.joblib --file path/to.wav --type baseline

# Deep (Keras)
python src/infer.py --model models/emotion_cnn.h5 --file path/to.wav --type deep

# Optional exports
python src/infer.py --export_saved_model models/emotion_cnn_saved --model models/emotion_cnn.h5
python src/infer.py --export_tflite models/emotion_cnn.tflite --model models/emotion_cnn.h5
```

## REST API (Flask)
```bash
$env:MODEL_PATH="F:\\...\\models\\emotion_cnn.h5"  # set your path
$env:PORT="8080"
python app.py
```
- POST `/predict` accepts `multipart/form-data` with `file`, or JSON with `audio_b64`.
- Response: `{ "emotion": "happy", "confidence": 0.89 }`

## Web Client
- Serve static site from project root:
```bash
python -m http.server 8000
```
- Open http://localhost:8000/web/
- Click "Start Recording", then "Upload & Predict".

## Evaluation
```bash
python src/evaluate.py --csv data/features.csv --model models/baseline_rf.joblib --split_col split --split_value test
```
Outputs to `reports/`: confusion matrix (normalized), ROC curves (if available), per-class F1 bar chart, metrics JSON.

## Docker
```bash
docker build -t emotion-api .
docker run --rm -p 8080:8080 -e MODEL_PATH=/app/models/emotion_cnn.h5 -v "%cd%/models:/app/models:ro" emotion-api
```

## Tests & CI
```bash
pip install pytest scipy
pytest -q
```
GitHub Actions workflow: `.github/workflows/ci.yml` runs tests on push/PR.

## Notes
- Ensure TensorFlow CPU is available for deep inference (`tensorflow-cpu==2.15.0`).
- For environments without TensorFlow, consider TFLite or ONNX runtime paths (can be added on request).
