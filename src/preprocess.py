#!/usr/bin/env python3
"""
Preprocess audio files:
- Reads from data/raw/
- Resamples to 22050 Hz
- Trims leading/trailing silence
- Pads or truncates to exactly 3.0 seconds
- Normalizes amplitude
- Optional augmentations: Gaussian noise, time-stretch (0.9–1.1), pitch shift (±2 semitones)
- Saves cleaned audio to data/clean/ and writes data/clean_metadata.csv

Usage examples:
  python src/preprocess.py
  python src/preprocess.py --sr 22050 --duration 3.0
  python src/preprocess.py --augment 3
  python src/preprocess.py --input data/raw --output data/clean --metadata data/clean_metadata.csv --augment 2
"""

import argparse
import csv
import os
import sys
import math
import random
from typing import List, Tuple

import numpy as np

try:
    import soundfile as sf
except Exception as e:
    sf = None

try:
    import librosa
    import librosa.effects
except Exception as e:
    librosa = None


RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def list_audio_files(root: str) -> List[str]:
    exts = {".wav", ".flac", ".mp3", ".m4a"}
    files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                files.append(os.path.join(dirpath, fn))
    return files


def load_audio_mono(path: str, target_sr: int) -> Tuple[np.ndarray, int]:
    if librosa is None:
        raise RuntimeError("librosa is required for preprocessing. Please install dependencies.")
    y, sr = librosa.load(path, sr=target_sr, mono=True)
    if not np.any(np.isfinite(y)):
        y = np.zeros(int(target_sr * 0.1), dtype=np.float32)
    return y.astype(np.float32), target_sr


def trim_silence(y: np.ndarray, top_db: float = 20.0) -> np.ndarray:
    # Use librosa.effects.trim to remove leading/trailing silence
    yt, _ = librosa.effects.trim(y, top_db=top_db)
    return yt


def pad_or_truncate(y: np.ndarray, target_len: int) -> np.ndarray:
    if len(y) > target_len:
        return y[:target_len]
    if len(y) < target_len:
        pad_len = target_len - len(y)
        return np.pad(y, (0, pad_len), mode="constant")
    return y


def normalize_audio(y: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    peak = np.max(np.abs(y)) if y.size > 0 else 0.0
    if peak < eps:
        return y
    return y / peak


def add_gaussian_noise(y: np.ndarray, snr_db: float = 20.0) -> np.ndarray:
    # Compute noise power for desired SNR
    sig_power = np.mean(y ** 2) + 1e-9
    snr = 10 ** (snr_db / 10.0)
    noise_power = sig_power / snr
    noise = np.random.normal(0.0, np.sqrt(noise_power), size=y.shape).astype(np.float32)
    return (y + noise).astype(np.float32)


def time_stretch(y: np.ndarray, rate: float) -> np.ndarray:
    return librosa.effects.time_stretch(y, rate=rate).astype(np.float32)


def pitch_shift(y: np.ndarray, sr: int, n_steps: float) -> np.ndarray:
    return librosa.effects.pitch_shift(y, sr=sr, n_steps=n_steps).astype(np.float32)


def save_wav(path: str, y: np.ndarray, sr: int) -> None:
    if sf is None:
        raise RuntimeError("soundfile is required to write wav files. Please install dependencies.")
    ensure_dir(os.path.dirname(path))
    sf.write(path, y, sr)


def process_file(
    in_path: str,
    out_dir: str,
    sr: int,
    duration_s: float,
    augment_count: int,
) -> List[Tuple[str, str]]:
    """Return list of (output_file, source_file) including augmented variants."""
    rel = os.path.relpath(in_path)
    stem = os.path.splitext(os.path.basename(in_path))[0]
    base_out = os.path.join(out_dir, stem + ".wav")

    try:
        y, _ = load_audio_mono(in_path, sr)
        y = trim_silence(y, top_db=20.0)
        target_len = int(sr * duration_s)
        y = pad_or_truncate(y, target_len)
        y = normalize_audio(y)
        save_wav(base_out, y, sr)
    except Exception as e:
        print(f"[error] Failed {in_path}: {e}")
        return []

    outputs = [(base_out, in_path)]

    # Augmentations
    for i in range(augment_count):
        y_aug = y.copy()
        # Randomly choose a subset of augmentations
        # 1) Gaussian noise with random SNR in [15, 30] dB
        if random.random() < 0.7:
            snr_db = random.uniform(15.0, 30.0)
            y_aug = add_gaussian_noise(y_aug, snr_db=snr_db)
        # 2) Time-stretch in [0.9, 1.1]
        if random.random() < 0.7:
            rate = random.uniform(0.9, 1.1)
            try:
                y_aug = time_stretch(y_aug, rate)
            except Exception:
                pass
        # 3) Pitch shift ±2 semitones
        if random.random() < 0.7:
            steps = random.uniform(-2.0, 2.0)
            try:
                y_aug = pitch_shift(y_aug, sr, steps)
            except Exception:
                pass
        # Enforce exact duration and normalization after augment
        y_aug = pad_or_truncate(y_aug, target_len)
        y_aug = normalize_audio(y_aug)

        out_path = os.path.join(out_dir, f"{stem}_aug{i+1}.wav")
        save_wav(out_path, y_aug, sr)
        outputs.append((out_path, in_path))

    return outputs


def main():
    parser = argparse.ArgumentParser(description="Preprocess audio dataset to fixed length normalized wavs")
    parser.add_argument("--input", type=str, default="data/raw", help="Input root folder containing raw audio")
    parser.add_argument("--output", type=str, default="data/clean", help="Output folder for cleaned audio")
    parser.add_argument("--metadata", type=str, default="data/clean_metadata.csv", help="Output CSV for metadata")
    parser.add_argument("--sr", type=int, default=22050, help="Target sample rate")
    parser.add_argument("--duration", type=float, default=3.0, help="Target duration in seconds")
    parser.add_argument("--augment", type=int, default=0, help="Number of augmented variants to generate per file")
    args = parser.parse_args()

    if librosa is None or sf is None:
        print("[error] Missing dependencies. Install with: pip install -r requirements.txt")
        sys.exit(1)

    in_root = args.input
    out_root = args.output
    meta_csv = args.metadata
    sr = args.sr
    duration_s = args.duration
    augment_count = max(0, int(args.augment))

    if not os.path.isdir(in_root):
        print(f"[error] Input folder not found: {in_root}")
        sys.exit(1)

    ensure_dir(out_root)
    ensure_dir(os.path.dirname(meta_csv) or ".")

    files = list_audio_files(in_root)
    if not files:
        print(f"[warn] No audio files found under {in_root}")
        sys.exit(0)

    rows: List[Tuple[str, str, str]] = []  # (output_path, source_path, split)
    for idx, fp in enumerate(files):
        outs = process_file(fp, out_root, sr, duration_s, augment_count)
        for out_fp, src_fp in outs:
            rows.append((os.path.normpath(out_fp), os.path.normpath(src_fp), "train"))
        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1} / {len(files)} files...")

    # Write metadata CSV: filepath,source_path,split
    with open(meta_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["filepath", "source_path", "split"])
        for out_fp, src_fp, split in rows:
            w.writerow([out_fp, src_fp, split])

    print(f"Done. Cleaned audio saved to: {out_root}")
    print(f"Metadata written to: {meta_csv}")


if __name__ == "__main__":
    main()


