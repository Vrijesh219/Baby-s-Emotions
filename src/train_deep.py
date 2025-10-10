#!/usr/bin/env python3
"""
Train a deep model (CNN) on mel-spectrogram or MFCC tensors saved in data/.

Expected inputs:
- Mel-spectrogram array: data/melspec.npy (shape: [N, n_mels, T])
  or
- MFCC array: data/mfcc.npy (shape: [N, n_mfcc, T])

Labels:
- data/features.csv will be used to derive labels in the same order as arrays are generated.
  If needed, you can pass --labels_csv to point to a CSV with [filepath,label] rows aligned with the arrays used.

Training config:
- epochs=60, batch_size=32, Adam(learning_rate=1e-3)
- callbacks: EarlyStopping(patience=8, restore_best_weights=True), ModelCheckpoint
- saves model to models/emotion_cnn.h5 and training curve to reports/train_history.png

Quick smoke test (small subset):
  python src/train_deep.py --melspec data/melspec.npy --labels_csv data/features.csv --limit 128 --epochs 2
"""

import argparse
import os
from typing import Tuple, List

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import matplotlib.pyplot as plt


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_array_and_labels(melspec_path: str = None, mfcc_path: str = None, labels_csv: str = None, limit: int = None) -> Tuple[np.ndarray, np.ndarray]:
    if (melspec_path is None) == (mfcc_path is None):
        raise ValueError("Provide exactly one of --melspec or --mfcc")
    arr_path = melspec_path or mfcc_path
    X = np.load(arr_path)
    if limit is not None:
        X = X[:limit]

    if labels_csv is None:
        raise ValueError("--labels_csv is required to map examples to labels")
    df = pd.read_csv(labels_csv)
    # The CSV rows should align to the same order as arrays saved; features.py writes rows in the same order it iterates files.
    labels = df["label"].astype(str).values
    if limit is not None:
        labels = labels[:limit]

    # Encode labels to integers
    classes = sorted(list({*labels}))
    class_to_idx = {c: i for i, c in enumerate(classes)}
    y = np.array([class_to_idx.get(l, -1) for l in labels], dtype=np.int64)
    if np.any(y < 0):
        raise ValueError("Found unlabeled samples. Ensure labels exist in CSV.")

    # Expand dims for channels-last CNN: (N, H, W, 1)
    if X.ndim == 3:
        X = X[..., np.newaxis]

    return X.astype(np.float32), y.astype(np.int64)


def build_cnn(input_shape: Tuple[int, int, int], num_classes: int) -> keras.Model:
    inputs = keras.Input(shape=input_shape)
    x = layers.BatchNormalization()(inputs)

    x = layers.Conv2D(32, (3, 3), padding="same", activation=None)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.2)(x)

    x = layers.Conv2D(64, (3, 3), padding="same", activation=None)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.3)(x)

    x = layers.Conv2D(128, (3, 3), padding="same", activation=None)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling2D((2, 2))(x)
    x = layers.Dropout(0.3)(x)

    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dense(128, activation=None)(x)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.Dropout(0.4)(x)

    outputs = layers.Dense(num_classes, activation="softmax")(x)
    model = keras.Model(inputs, outputs)
    return model


def make_datasets(X: np.ndarray, y: np.ndarray, batch_size: int = 32, val_split: float = 0.2, shuffle_seed: int = 42):
    N = len(X)
    idx = np.arange(N)
    rng = np.random.default_rng(shuffle_seed)
    rng.shuffle(idx)
    X = X[idx]
    y = y[idx]

    n_val = max(1, int(N * val_split))
    X_train, X_val = X[:-n_val], X[-n_val:]
    y_train, y_val = y[:-n_val], y[-n_val:]

    def _tfdata(xs, ys, training=False):
        ds = tf.data.Dataset.from_tensor_slices((xs, ys))
        if training:
            ds = ds.shuffle(min(1000, len(xs)), seed=shuffle_seed, reshuffle_each_iteration=True)
        ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
        return ds

    return _tfdata(X_train, y_train, training=True), _tfdata(X_val, y_val, training=False)


def plot_history(history: keras.callbacks.History, out_path: str):
    ensure_dir(os.path.dirname(out_path) or ".")
    h = history.history
    plt.figure(figsize=(8, 4))
    plt.subplot(1, 2, 1)
    plt.plot(h.get("loss", []), label="train")
    plt.plot(h.get("val_loss", []), label="val")
    plt.title("Loss")
    plt.legend()
    plt.subplot(1, 2, 2)
    plt.plot(h.get("accuracy", []), label="train")
    plt.plot(h.get("val_accuracy", []), label="val")
    plt.title("Accuracy")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    ap = argparse.ArgumentParser(description="Train CNN on mel-spectrogram or MFCC arrays")
    ap.add_argument("--melspec", type=str, default=None, help="Path to data/melspec.npy")
    ap.add_argument("--mfcc", type=str, default=None, help="Path to data/mfcc.npy")
    ap.add_argument("--labels_csv", type=str, default="data/features.csv", help="CSV containing labels in order")
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--batch_size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--model_out", type=str, default="models/emotion_cnn.h5")
    ap.add_argument("--history_plot", type=str, default="reports/train_history.png")
    ap.add_argument("--limit", type=int, default=None, help="Optional: train on a subset for quick smoke test")
    args = ap.parse_args()

    X, y = load_array_and_labels(args.melspec, args.mfcc, args.labels_csv, args.limit)
    num_classes = int(np.max(y) + 1)

    train_ds, val_ds = make_datasets(X, y, batch_size=args.batch_size)

    input_shape = X.shape[1:]
    model = build_cnn(input_shape, num_classes)

    opt = keras.optimizers.Adam(learning_rate=args.lr)
    model.compile(optimizer=opt, loss="sparse_categorical_crossentropy", metrics=["accuracy"])

    ensure_dir(os.path.dirname(args.model_out) or ".")
    ensure_dir(os.path.dirname(args.history_plot) or ".")

    callbacks = [
        keras.callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(args.model_out, monitor="val_loss", save_best_only=True)
    ]

    history = model.fit(train_ds, validation_data=val_ds, epochs=args.epochs, callbacks=callbacks)

    # Save final model (best already saved by checkpoint)
    model.save(args.model_out)
    plot_history(history, args.history_plot)
    print(f"Saved model to {args.model_out}")
    print(f"Saved training curves to {args.history_plot}")


if __name__ == "__main__":
    main()


