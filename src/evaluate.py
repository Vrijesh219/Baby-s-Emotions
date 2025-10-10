#!/usr/bin/env python3
"""
Evaluate a trained classifier on a test feature set.

Loads a features CSV with columns [filepath, label, f0..fN] and (optionally) a
split column (e.g., 'split') to select the test subset. Evaluates a saved model
(.joblib scikit-learn pipeline) and computes:
- classification_report
- macro and weighted F1
- accuracy

Saves plots to reports/:
- Normalized confusion matrix: reports/confusion_matrix.png
- ROC curves per class (if predict_proba available): reports/roc_curves.png
- Bar chart of per-class F1-scores: reports/f1_per_class.png

Also saves metrics to reports/metrics.json

Usage example:
  python src/evaluate.py --csv data/features.csv --model models/baseline_rf.joblib --split_col split --split_value test
"""

import argparse
import json
import os
from typing import List, Tuple, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    f1_score,
    roc_curve,
    auc,
)

try:
    import joblib
except Exception:
    joblib = None


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_features_csv(
    csv_path: str,
    split_col: Optional[str] = None,
    split_value: Optional[str] = None,
) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
    """
    Returns X, y, classes (sorted unique labels), and feature column names.
    If split_col and split_value are provided and present, filters rows.
    """
    df = pd.read_csv(csv_path)
    if split_col and split_col in df.columns and split_value is not None:
        df = df[df[split_col].astype(str).str.lower() == str(split_value).lower()].copy()
    if "label" not in df.columns:
        raise ValueError("CSV must contain a 'label' column")
    feature_cols = [c for c in df.columns if c not in ("filepath", "label")]
    X = df[feature_cols].to_numpy(dtype=np.float32)
    y = df["label"].astype(str).to_numpy()
    classes = sorted(list({*y}))
    return X, y, classes, feature_cols


def plot_confusion(y_true: np.ndarray, y_pred: np.ndarray, labels: List[str], out_path: str) -> None:
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    cm_norm = cm.astype(np.float32) / np.maximum(cm.sum(axis=1, keepdims=True), 1)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm_norm, annot=True, fmt=".2f", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Normalized Confusion Matrix")
    ensure_dir(os.path.dirname(out_path) or ".")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_roc_curves(
    y_true: np.ndarray,
    proba: np.ndarray,
    labels: List[str],
    out_path: str,
) -> None:
    """
    Plot one-vs-rest ROC per class if probabilities available.
    """
    # Binarize labels
    label_to_idx = {c: i for i, c in enumerate(labels)}
    y_indices = np.array([label_to_idx[l] for l in y_true], dtype=np.int64)
    y_bin = np.zeros((len(y_true), len(labels)), dtype=np.float32)
    y_bin[np.arange(len(y_true)), y_indices] = 1.0

    plt.figure(figsize=(8, 6))
    for i, cls in enumerate(labels):
        try:
            fpr, tpr, _ = roc_curve(y_bin[:, i], proba[:, i])
            roc_auc = auc(fpr, tpr)
            plt.plot(fpr, tpr, label=f"{cls} (AUC={roc_auc:.3f})")
        except Exception:
            continue
    plt.plot([0, 1], [0, 1], "k--", label="chance")
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curves (One-vs-Rest)")
    plt.legend(loc="lower right", fontsize=8)
    ensure_dir(os.path.dirname(out_path) or ".")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_f1_bars(report_dict: dict, out_path: str) -> None:
    """
    Expects classification_report output as a dict; plots per-class f1-scores.
    """
    rows = []
    for label, stats in report_dict.items():
        if label in ("accuracy", "macro avg", "weighted avg"):
            continue
        try:
            rows.append((label, float(stats.get("f1-score", 0.0))))
        except Exception:
            continue
    if not rows:
        return
    labels, f1s = zip(*sorted(rows, key=lambda x: x[0]))
    plt.figure(figsize=(10, 4))
    ax = plt.gca()
    bars = ax.bar(labels, f1s, color="#60a5fa")
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("F1-score")
    ax.set_title("Per-class F1-scores")
    for b, v in zip(bars, f1s):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.02, f"{v:.2f}", ha="center", va="bottom", fontsize=8)
    plt.xticks(rotation=30, ha="right")
    ensure_dir(os.path.dirname(out_path) or ".")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Evaluate classifier on test features")
    ap.add_argument("--csv", type=str, default="data/features.csv", help="Path to features CSV")
    ap.add_argument("--model", type=str, required=True, help="Path to trained model (.joblib scikit-learn)")
    ap.add_argument("--split_col", type=str, default=None, help="Optional split column name (e.g., 'split')")
    ap.add_argument("--split_value", type=str, default=None, help="Optional split value to select (e.g., 'test')")
    ap.add_argument("--out_dir", type=str, default="reports", help="Directory to save reports/plots")
    args = ap.parse_args()

    if joblib is None:
        raise RuntimeError("joblib is required to load the trained model")

    X, y, classes, feature_cols = load_features_csv(args.csv, args.split_col, args.split_value)
    if len(X) == 0:
        raise RuntimeError("No samples found after filtering. Check --csv/--split options.")

    model = joblib.load(args.model)
    y_pred = model.predict(X)

    # Metrics
    acc = accuracy_score(y, y_pred)
    f1_macro = f1_score(y, y_pred, average="macro")
    f1_weighted = f1_score(y, y_pred, average="weighted")
    report_txt = classification_report(y, y_pred, digits=4)
    report_dict = classification_report(y, y_pred, output_dict=True)

    # Save metrics JSON and text
    ensure_dir(args.out_dir)
    metrics = {
        "accuracy": float(acc),
        "f1_macro": float(f1_macro),
        "f1_weighted": float(f1_weighted),
        "classes": classes,
    }
    with open(os.path.join(args.out_dir, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    with open(os.path.join(args.out_dir, "classification_report.txt"), "w", encoding="utf-8") as f:
        f.write(report_txt)

    # Plots
    plot_confusion(y, y_pred, labels=sorted(list({*y, *y_pred})), out_path=os.path.join(args.out_dir, "confusion_matrix.png"))
    plot_f1_bars(report_dict, os.path.join(args.out_dir, "f1_per_class.png"))

    # ROC (if probabilities available)
    proba = None
    if hasattr(model, "predict_proba"):
        try:
            proba = model.predict_proba(X)
        except Exception:
            proba = None
    if proba is not None and isinstance(proba, np.ndarray) and proba.ndim == 2 and proba.shape[1] >= 2:
        # Align class order if the estimator exposes it
        est_classes = getattr(model, "classes_", None)
        labels = classes
        if est_classes is not None:
            # Reorder probabilities to match label order used for plotting (classes)
            idx_map = {c: i for i, c in enumerate(est_classes)}
            if all(c in idx_map for c in classes):
                proba = proba[:, [idx_map[c] for c in classes]]
                labels = classes
            else:
                labels = list(est_classes)
        plot_roc_curves(y, proba, labels=labels, out_path=os.path.join(args.out_dir, "roc_curves.png"))

    print("Evaluation complete.")
    print(f"Accuracy: {acc:.4f}  F1(macro): {f1_macro:.4f}  F1(weighted): {f1_weighted:.4f}")
    print(f"Reports saved under: {args.out_dir}")


if __name__ == "__main__":
    main()


