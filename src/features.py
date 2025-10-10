#!/usr/bin/env python3
"""
Feature extraction for cleaned audio.

Computes per-file features:
- MFCC (n_mfcc=40): mean and std for each coefficient (80 dims)
- Delta MFCC (order-1): mean and std (80 dims)
- Chroma STFT mean (12 dims)
- Spectral centroid mean (1 dim)
- Zero crossing rate mean (1 dim)
- RMS energy mean (1 dim)

Optionally computes log-mel spectrogram arrays for deep learning and saves them.

Outputs:
- data/features.csv (rows with filepath, label and per-file features)
- data/features.npy (X features array)
- Optionally: data/melspec.npy (N,H,W) and data/melspec_files.txt

Sample usage:
  python src/features.py --input data/clean --csv data/features.csv --npy data/features.npy --melspec data/melspec.npy

Programmatic usage:
  from src.features import extract_features
  feats, label = extract_features('data/clean/Actor_01/xxx.wav')
"""

import argparse
import csv
import os
from typing import Dict, Tuple, Optional, List

import numpy as np

try:
    import librosa
except Exception as e:
    librosa = None


SR = 22050
N_MFCC = 40
N_MELS = 64
HOP_LENGTH = 512
N_FFT = 2048


EMOTIONS = {
    "neutral", "calm", "happy", "sad", "angry", "fearful", "disgust", "surprised"
}

# RAVDESS filename code to emotion mapping (3rd token in name)
RAVDESS_EMOTION_MAP = {
    "01": "neutral",
    "02": "calm",
    "03": "happy",
    "04": "sad",
    "05": "angry",
    "06": "fearful",
    "07": "disgust",
    "08": "surprised",
}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def infer_label_from_path(path: str) -> Optional[str]:
    # Expect label in parent directories or filenames if organized; fallback None
    # For this project we don't strictly require label here; downstream can join from metadata if needed
    # Try to find one of known emotions in the path string
    low = path.replace("\\", "/").lower()
    for e in EMOTIONS:
        if f"/{e}/" in low or low.endswith(f"/{e}.wav") or f"_{e}.wav" in low:
            return e
    # Try RAVDESS pattern: name like 03-01-05-01-02-01-12.wav where 3rd token is emotion code
    base = os.path.basename(path)
    parts = base.split("-")
    if len(parts) >= 3:
        em_code = parts[2]
        if em_code in RAVDESS_EMOTION_MAP:
            return RAVDESS_EMOTION_MAP[em_code]
    return None


def extract_features(file_path: str, sr: int = SR) -> Tuple[np.ndarray, Optional[str]]:
    """
    Extracts features from a single audio file and returns (feature_vector, label).
    """
    if librosa is None:
        raise RuntimeError("librosa is required. Please install dependencies.")
    y, _ = librosa.load(file_path, sr=sr, mono=True)
    # Defensive: ensure finite
    if not np.any(np.isfinite(y)):
        y = np.zeros(sr, dtype=np.float32)

    # MFCCs
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=N_MFCC, n_fft=N_FFT, hop_length=HOP_LENGTH)
    mfcc_delta = librosa.feature.delta(mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    mfcc_std = np.std(mfcc, axis=1)
    d_mfcc_mean = np.mean(mfcc_delta, axis=1)
    d_mfcc_std = np.std(mfcc_delta, axis=1)

    # Chroma
    stft = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP_LENGTH))
    chroma = librosa.feature.chroma_stft(S=stft, sr=sr)
    chroma_mean = np.mean(chroma, axis=1)

    # Spectral centroid
    spec_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spec_centroid_mean = float(np.mean(spec_centroid))

    # Zero crossing rate
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    zcr_mean = float(np.mean(zcr))

    # RMS energy
    rms = librosa.feature.rms(y=y)[0]
    rms_mean = float(np.mean(rms))

    # Concatenate features
    feat_vec = np.concatenate([
        mfcc_mean, mfcc_std,
        d_mfcc_mean, d_mfcc_std,
        chroma_mean,
        np.array([spec_centroid_mean, zcr_mean, rms_mean], dtype=np.float32)
    ]).astype(np.float32)

    label = infer_label_from_path(file_path)
    return feat_vec, label


def compute_melspec(file_path: str, sr: int = SR, n_mels: int = N_MELS) -> np.ndarray:
    y, _ = librosa.load(file_path, sr=sr, mono=True)
    S = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=N_FFT, hop_length=HOP_LENGTH, n_mels=n_mels, power=2.0)
    S_db = librosa.power_to_db(S, ref=np.max).astype(np.float32)
    return S_db


def list_audio_files(root: str) -> List[str]:
    exts = {".wav", ".flac", ".mp3", ".m4a"}
    files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                files.append(os.path.join(dirpath, fn))
    return files


def main():
    ap = argparse.ArgumentParser(description="Extract features from cleaned audio")
    ap.add_argument("--input", type=str, default="data/clean", help="Input folder with cleaned wavs")
    ap.add_argument("--csv", type=str, default="data/features.csv", help="Output CSV for features + labels")
    ap.add_argument("--npy", type=str, default="data/features.npy", help="Output Numpy .npy for features array")
    ap.add_argument("--melspec", type=str, default=None, help="Optional: path to save mel-spectrogram array .npy")
    ap.add_argument("--metadata", type=str, default=None, help="Optional: CSV with filepath->label mapping to override inference")
    args = ap.parse_args()

    if librosa is None:
        raise RuntimeError("librosa is required. Please install dependencies.")

    files = list_audio_files(args.input)
    if not files:
        print(f"[warn] No audio found under {args.input}")
        return

    ensure_dir(os.path.dirname(args.csv) or ".")
    ensure_dir(os.path.dirname(args.npy) or ".")
    if args.melspec:
        ensure_dir(os.path.dirname(args.melspec) or ".")

    # Optional external metadata mapping of absolute/normalized filepath -> label
    meta_map: Dict[str, str] = {}
    if args.metadata and os.path.isfile(args.metadata):
        try:
            import pandas as pd
            mdf = pd.read_csv(args.metadata)
            # Try common column names
            file_col = "filepath" if "filepath" in mdf.columns else ("file" if "file" in mdf.columns else None)
            label_col = "emotion_label" if "emotion_label" in mdf.columns else ("label" if "label" in mdf.columns else None)
            if file_col and label_col:
                for _, row in mdf.iterrows():
                    p = os.path.normcase(os.path.normpath(str(row[file_col])))
                    meta_map[p] = str(row[label_col])
        except Exception as e:
            print(f"[warn] Failed to load metadata mapping: {e}")

    X: List[np.ndarray] = []
    Y: List[Optional[str]] = []
    melspecs: List[np.ndarray] = []

    with open(args.csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        # header: filepath, label, feat_0..feat_N-1
        header_written = False

        for i, fp in enumerate(files):
            try:
                feats, label = extract_features(fp)
            except Exception as e:
                print(f"[error] {fp}: {e}")
                continue

            # Override label from metadata if provided
            if args.metadata:
                key = os.path.normcase(os.path.normpath(fp))
                label = meta_map.get(key, label)

            X.append(feats)
            Y.append(label)

            if not header_written:
                header = ["filepath", "label"] + [f"f{i}" for i in range(len(feats))]
                w.writerow(header)
                header_written = True

            row = [fp, label if label is not None else ""] + feats.astype(float).tolist()
            w.writerow(row)

            if args.melspec is not None:
                try:
                    S_db = compute_melspec(fp)
                    melspecs.append(S_db)
                except Exception as e:
                    print(f"[warn] melspec failed for {fp}: {e}")

            if (i + 1) % 100 == 0:
                print(f"Processed {i + 1} / {len(files)} files")

    X_array = np.stack(X, axis=0).astype(np.float32)
    np.save(args.npy, X_array)
    print(f"Saved features to {args.npy} shape={X_array.shape}")
    print(f"Saved CSV to {args.csv} rows={len(X)}")

    if args.melspec is not None and melspecs:
        # Pad to same time length (right-pad with min value) for stacking
        max_T = max(m.shape[1] for m in melspecs)
        padded = []
        for m in melspecs:
            if m.shape[1] < max_T:
                pad = np.full((m.shape[0], max_T - m.shape[1]), np.min(m), dtype=m.dtype)
                m = np.concatenate([m, pad], axis=1)
            padded.append(m)
        M_array = np.stack(padded, axis=0)
        np.save(args.melspec, M_array)
        print(f"Saved mel-spectrograms to {args.melspec} shape={M_array.shape}")


if __name__ == "__main__":
    main()


