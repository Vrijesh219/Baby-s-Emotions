#!/usr/bin/env python3
"""
Train baseline RandomForest on extracted features.

Loads data/features.csv, builds a pipeline (StandardScaler + RandomForest),
performs GridSearchCV with StratifiedKFold(5), prints metrics, saves best
model to models/baseline_rf.joblib, and writes confusion matrix plot to
reports/confusion_baseline.png

Usage:
  python src/train_baseline.py --csv data/features.csv --model models/baseline_rf.joblib
"""

import argparse
import os
import numpy as np
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import matplotlib.pyplot as plt
import seaborn as sns


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_dataset(csv_path: str):
    df = pd.read_csv(csv_path)
    # Expect first two columns: filepath, label; rest are numeric features
    if "label" not in df.columns:
        raise ValueError("CSV must contain a 'label' column")
    feature_cols = [c for c in df.columns if c not in ("filepath", "label")]
    X = df[feature_cols].to_numpy(dtype=np.float32)
    y = df["label"].astype(str).to_numpy()
    return X, y, feature_cols


def plot_confusion(y_true, y_pred, out_path: str):
    labels = sorted(list({*y_true, *y_pred}))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title("Baseline RandomForest Confusion Matrix")
    ensure_dir(os.path.dirname(out_path) or ".")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main():
    ap = argparse.ArgumentParser(description="Train baseline RF with GridSearchCV")
    ap.add_argument("--csv", type=str, default="data/features.csv", help="Path to features CSV")
    ap.add_argument("--model", type=str, default="models/baseline_rf.joblib", help="Output model path")
    ap.add_argument("--report", type=str, default="reports/confusion_baseline.png", help="Confusion matrix image path")
    args = ap.parse_args()

    X, y, feature_cols = load_dataset(args.csv)

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("rf", RandomForestClassifier(random_state=42))
    ])

    param_grid = {
        "rf__n_estimators": [100, 200],
        "rf__max_depth": [None, 10, 20],
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    grid = GridSearchCV(pipe, param_grid=param_grid, cv=cv, n_jobs=-1, scoring="accuracy", verbose=1)
    grid.fit(X, y)

    best_model = grid.best_estimator_
    ensure_dir(os.path.dirname(args.model) or ".")
    joblib.dump(best_model, args.model)
    print(f"Saved best model to {args.model}")
    print("Best params:", grid.best_params_)

    # Evaluate with cross-val predictions via best model on the same data (note: optimistic)
    y_pred = best_model.predict(X)
    acc = accuracy_score(y, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print(classification_report(y, y_pred))

    plot_confusion(y, y_pred, args.report)
    print(f"Saved confusion matrix to {args.report}")


if __name__ == "__main__":
    main()


