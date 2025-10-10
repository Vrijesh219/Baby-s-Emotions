#!/usr/bin/env python3
"""
Inference utilities for emotion recognition.

Provides predict_from_file(model_path, audio_path) that auto-detects model type:
- .joblib: scikit-learn baseline using tabular features (same as features.py)
- .h5 or SavedModel directory: Keras deep model expecting mel-spectrogram (H,W,1)

Examples:
  # Baseline (RandomForest)
  python src/infer.py --model models/baseline_rf.joblib --file path/to.wav --type baseline

  # Deep (Keras CNN on mel-spectrogram)
  python src/infer.py --model models/emotion_cnn.h5 --file path/to.wav --type deep

Optional exports (Keras):
  # SavedModel
  python src/infer.py --export_saved_model models/emotion_cnn_saved

  # TFLite (float32)
  python src/infer.py --export_tflite models/emotion_cnn.tflite --model models/emotion_cnn.h5
"""

import argparse
import os
import json
from typing import Tuple

import numpy as np

try:
    import joblib
except Exception:
    joblib = None

try:
    import tensorflow as tf
    from tensorflow import keras
except Exception:
    tf = None
    keras = None

try:
    import librosa
except Exception:
    librosa = None


SR = 22050
N_MELS = 64
HOP_LENGTH = 512
N_FFT = 2048


def ensure_deps():
    if librosa is None:
        raise RuntimeError("librosa is required. Install dependencies.")


def compute_tabular_features(audio_path: str) -> np.ndarray:
    """Replicates extract_features logic for a single file for baseline model."""
    import librosa
    y, _ = librosa.load(audio_path, sr=SR, mono=True)
    if not np.any(np.isfinite(y)):
        y = np.zeros(SR, dtype=np.float32)
    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=40, n_fft=N_FFT, hop_length=HOP_LENGTH)
    d = librosa.feature.delta(mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    d_mean = np.mean(d, axis=1)
    d_std = np.std(d, axis=1)
    stft = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH))
    chroma_mean = np.mean(librosa.feature.chroma_stft(S=stft, sr=SR), axis=1)
    spec_centroid_mean = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=SR)[0]))
    zcr_mean = float(np.mean(librosa.feature.zero_crossing_rate(y)[0]))
    rms_mean = float(np.mean(librosa.feature.rms(y=y)[0]))
    feat = np.concatenate([
        mfcc_mean, mfcc_std, d_mean, d_std, chroma_mean,
        np.array([spec_centroid_mean, zcr_mean, rms_mean], dtype=np.float32)
    ]).astype(np.float32)
    return feat[np.newaxis, :]


def compute_melspec_tensor(audio_path: str) -> np.ndarray:
    y, _ = librosa.load(audio_path, sr=SR, mono=True)
    S = librosa.feature.melspectrogram(y=y, sr=SR, n_fft=N_FFT, hop_length=HOP_LENGTH, n_mels=N_MELS, power=2.0)
    S_db = librosa.power_to_db(S, ref=np.max).astype(np.float32)
    # Add channel dim -> (1, H, W, 1)
    return S_db[np.newaxis, ..., np.newaxis]


def predict_from_file(model_path: str, audio_path: str) -> Tuple[str, float]:
    """Returns (predicted_label, confidence). Auto-detects baseline vs deep by extension."""
    ensure_deps()
    ext = os.path.splitext(model_path)[1].lower()

    if ext == ".joblib":
        if joblib is None:
            raise RuntimeError("joblib not available to load scikit-learn model")
        model = joblib.load(model_path)
        x = compute_tabular_features(audio_path)
        proba = None
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(x)[0]
            pred_idx = int(np.argmax(proba))
            pred = model.classes_[pred_idx]
            conf = float(np.max(proba))
        else:
            pred = model.predict(x)[0]
            conf = 1.0
        return str(pred), conf

    # Keras model (.h5 or SavedModel dir)
    if keras is None:
        raise RuntimeError("TensorFlow/Keras not available")
    model = keras.models.load_model(model_path)
    x = compute_melspec_tensor(audio_path)
    probs = model.predict(x, verbose=0)[0]
    idx = int(np.argmax(probs))
    conf = float(probs[idx])
    # Try to get class names if present in model
    if hasattr(model, "classes_"):
        label = model.classes_[idx]
    else:
        label = str(idx)
    return label, conf


def export_saved_model(model_path: str, out_dir: str):
    if keras is None:
        raise RuntimeError("TensorFlow/Keras not available")
    model = keras.models.load_model(model_path)
    keras.models.save_model(model, out_dir, save_format="tf")
    print(f"SavedModel exported to {out_dir}")


def export_tflite(model_path: str, out_file: str):
    if tf is None:
        raise RuntimeError("TensorFlow not available")
    model = keras.models.load_model(model_path)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    tflite_model = converter.convert()
    with open(out_file, "wb") as f:
        f.write(tflite_model)
    print(f"TFLite model written to {out_file}")


def main():
    ap = argparse.ArgumentParser(description="Run inference for a single audio file")
    ap.add_argument("--model", type=str, required=False, help="Path to .joblib or .h5 model")
    ap.add_argument("--file", type=str, required=False, help="Path to audio file")
    ap.add_argument("--type", type=str, choices=["baseline", "deep"], default=None, help="Hint of model type")
    ap.add_argument("--export_saved_model", type=str, default=None, help="Export Keras model to SavedModel dir")
    ap.add_argument("--export_tflite", type=str, default=None, help="Export Keras model to TFLite file path")
    args = ap.parse_args()

    if args.export_saved_model and args.model:
        export_saved_model(args.model, args.export_saved_model)
        return
    if args.export_tflite and args.model:
        export_tflite(args.model, args.export_tflite)
        return

    if not args.model or not args.file:
        print("Provide --model and --file for prediction, or use export options.")
        return

    label, conf = predict_from_file(args.model, args.file)
    result = {"file": args.file, "predicted": label, "confidence": round(conf, 4)}
    print(json.dumps(result))


if __name__ == "__main__":
    main()


