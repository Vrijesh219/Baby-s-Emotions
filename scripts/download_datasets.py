#!/usr/bin/env python3
"""
Index existing local datasets (no external downloads) and produce metadata.csv.

Assumes your datasets are already present under a root folder (e.g., 'dataset/').
It scans for RAVDESS, TESS, and SAVEE inside that folder, parses emotion labels
and speakers from filenames/paths, and writes a combined metadata CSV:

Columns: filepath,emotion_label,speaker,split(train/val/test)
Split is speaker-wise and deterministic.

Example:
  python scripts/download_datasets.py --datasets ravdess tess savee --out dataset --metadata data/metadata.csv
"""

import argparse
import csv
import os
import re
import sys
import random
import pathlib
from typing import Dict, List, Tuple, Optional

# Reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Emotion mappings
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

SAVEE_PREFIX_TO_EMOTION = {
    "a": "angry",
    "d": "disgust",
    "f": "fearful",
    "h": "happy",
    "n": "neutral",
    "sa": "sad",
    "su": "surprised",
}

TESS_CANONICAL = {
    "angry": "angry",
    "anger": "angry",
    "disgust": "disgust",
    "fear": "fearful",
    "fearful": "fearful",
    "happy": "happy",
    "neutral": "neutral",
    "sad": "sad",
    "surprise": "surprised",
    "surprised": "surprised",
    "pleasant_surprise": "surprised",
}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def locate_audio_files(root: str) -> List[str]:
    exts = {".wav", ".flac", ".mp3", ".m4a"}
    found = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in exts:
                found.append(os.path.join(dirpath, fn))
    return found


def infer_ravdess_label_and_speaker(path: str) -> Tuple[Optional[str], Optional[str]]:
    # Filename like: 03-01-05-01-02-01-12.wav (3rd token is emotion two-digit)
    fn = os.path.basename(path)
    parts = fn.split("-")
    emotion = None
    if len(parts) >= 3:
        em_code = parts[2]
        emotion = RAVDESS_EMOTION_MAP.get(em_code)
    # Speaker usually directory 'Actor_XX'
    m = re.search(r"Actor_\d+", path.replace("\\", "/"))
    speaker = m.group(0) if m else None
    return emotion, speaker


def infer_tess_label_and_speaker(path: str) -> Tuple[Optional[str], Optional[str]]:
    # Filenames like OAF_angry.wav or YAF_sad.wav; emotion token in name
    fn = os.path.basename(path)
    stem = os.path.splitext(fn)[0]
    tokens = re.split(r"[_\- ]+", stem.lower())
    emotion = None
    for tok in tokens:
        if tok in TESS_CANONICAL:
            emotion = TESS_CANONICAL[tok]
            break
    # Use parent dir as speaker if available, else prefix (OAF/YAF)
    speaker = os.path.basename(os.path.dirname(path)) or (tokens[0] if tokens else None)
    return emotion, speaker


def infer_savee_label_and_speaker(path: str) -> Tuple[Optional[str], Optional[str]]:
    # Filenames like DC_a01.wav; speaker is 2-letter prefix before '_'
    fn = os.path.basename(path).lower()
    stem = os.path.splitext(fn)[0]
    speaker = None
    emotion = None
    m = re.match(r"([a-z]{2})_(.+)", stem)
    if m:
        speaker = m.group(1).upper()
        rest = m.group(2)
        m2 = re.match(r"([a-z]+)\d+", rest)
        if m2:
            emo_code = m2.group(1)
            emotion = SAVEE_PREFIX_TO_EMOTION.get(emo_code)
    return emotion, speaker


def generate_metadata_for_dataset(dataset_name: str, dataset_root: str) -> List[Tuple[str, str, str]]:
    audio_files = locate_audio_files(dataset_root)
    rows: List[Tuple[str, str, str]] = []
    for f in audio_files:
        emo: Optional[str] = None
        spk: Optional[str] = None
        try:
            if dataset_name == "ravdess":
                emo, spk = infer_ravdess_label_and_speaker(f)
            elif dataset_name == "tess":
                emo, spk = infer_tess_label_and_speaker(f)
            elif dataset_name == "savee":
                emo, spk = infer_savee_label_and_speaker(f)
        except Exception:
            emo, spk = None, None
        if emo is None or spk is None:
            continue
        rows.append((os.path.normpath(f), emo, spk))
    return rows


def stratified_speaker_split(
    rows: List[Tuple[str, str, str]],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
) -> Dict[str, str]:
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6
    speakers = sorted(list({spk for _, _, spk in rows}))
    random.Random(RANDOM_SEED).shuffle(speakers)
    n = len(speakers)
    if n == 0:
        return {}
    n_train = max(1, int(round(n * train_ratio)))
    n_val = max(1, int(round(n * val_ratio)))
    n_test = max(1, n - n_train - n_val)
    while n_train + n_val + n_test > n:
        if n_test > 1:
            n_test -= 1
        elif n_val > 1:
            n_val -= 1
        else:
            n_train -= 1
    splits = {}
    for i, spk in enumerate(speakers):
        if i < n_train:
            splits[spk] = "train"
        elif i < n_train + n_val:
            splits[spk] = "val"
        else:
            splits[spk] = "test"
    return splits


def write_metadata_csv(rows: List[Tuple[str, str, str]], out_csv: str) -> None:
    if not rows:
        print("[metadata] No rows to write.")
        return
    ensure_dir(os.path.dirname(out_csv))
    speaker_split = stratified_speaker_split(rows)
    shuffled = rows[:]
    random.Random(RANDOM_SEED).shuffle(shuffled)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["filepath", "emotion_label", "speaker", "split"])
        for fp, emo, spk in shuffled:
            split = speaker_split.get(spk, "train")
            w.writerow([fp, emo, spk, split])
    print(f"[metadata] Wrote {out_csv} with {len(rows)} rows.")


def find_dataset_root(base: str, name: str) -> Optional[str]:
    """
    Try common subfolder names inside base for each dataset.
    """
    candidates = []
    if name == "ravdess":
        candidates = [
            "RAVDESS",
            os.path.join("RAVDESS", "Audio_Speech_Actors_01-24"),
            "ravdess",
            "",  # allow base itself to be the actors root
        ]
    elif name == "tess":
        candidates = [
            "TESS",
            os.path.join("TESS", "TESS Toronto emotional speech set data"),
            "tess",
        ]
    elif name == "savee":
        candidates = [
            "SAVEE",
            os.path.join("SAVEE", "ALL"),
            "savee",
        ]
    for c in candidates:
        p = base if c == "" else (c if os.path.isabs(c) else os.path.join(base, c))
        if os.path.isdir(p):
            return p
    # Fallback: search by keyword
    for dirpath, dirnames, _ in os.walk(base):
        low = os.path.basename(dirpath).lower()
        if name in low:
            return dirpath
    # Special case: detect RAVDESS actors layout directly under base
    if name == "ravdess":
        actors = list(pathlib.Path(base).glob("Actor_*"))
        if actors:
            return base
    return None


def main():
    ap = argparse.ArgumentParser(description="Index local speech emotion datasets and generate metadata.csv")
    ap.add_argument("--datasets", nargs="+", default=["ravdess", "tess", "savee"],
                    help="Datasets to scan: ravdess tess savee")
    ap.add_argument("--out", type=str, default="dataset",
                    help="Root folder where datasets already exist (e.g., dataset/)")
    ap.add_argument("--metadata", type=str, default="data/metadata.csv",
                    help="Path to write combined metadata CSV")
    args = ap.parse_args()

    base = args.out
    if not os.path.isdir(base):
        print(f"[error] Base dataset folder not found: {base}")
        sys.exit(1)

    selected = [d.lower() for d in args.datasets]
    valid = {"ravdess", "tess", "savee"}
    for d in selected:
        if d not in valid:
            print(f"[error] Unknown dataset: {d}. Valid: {sorted(list(valid))}")
            sys.exit(1)

    all_rows: List[Tuple[str, str, str]] = []
    for name in selected:
        root = find_dataset_root(base, name)
        if not root:
            print(f"[warn] Could not locate {name} under {base}. Skipping.")
            continue
        rows = generate_metadata_for_dataset(name, root)
        print(f"[{name}] Found {len(rows)} audio files.")
        all_rows.extend(rows)

    if not all_rows:
        print("[metadata] No audio files found in provided datasets.")
        sys.exit(0)

    write_metadata_csv(all_rows, args.metadata)
    print("Done.")


if __name__ == "__main__":
    main()


