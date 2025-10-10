#!/usr/bin/env python3
"""
Minimal Flask API for audio emotion recognition.

Routes:
- GET /            → simple HTML upload form
- POST /predict    → accepts multipart/form-data (field: 'file') or JSON/base64 ('audio_b64')
                     returns JSON {"emotion": "happy", "confidence": 0.89}

Configuration via environment variables:
- MODEL_PATH: path to model file/dir (.joblib for scikit-learn, .h5 or SavedModel dir for Keras)
- PORT: port to bind (default 8080)

This app delegates preprocessing/feature extraction + inference to src/infer.py
"""

import base64
import io
import json
import logging
import os
import tempfile
from typing import Optional, Tuple

from flask import Flask, request, jsonify, Response
from werkzeug.utils import secure_filename

# Ensure we can import from src/
import sys
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.infer import predict_from_file  # type: ignore
except Exception as e:
    predict_from_file = None  # type: ignore
    _import_error = e
else:
    _import_error = None


def create_app() -> Flask:
    app = Flask(__name__)

    # Logging configuration
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
    app.logger.setLevel(getattr(logging, log_level, logging.INFO))

    model_path = os.getenv("MODEL_PATH", os.path.join("models", "emotion_cnn.h5"))

    if predict_from_file is None:
        app.logger.error("Failed to import src.infer.predict_from_file: %s", _import_error)

    @app.get("/")
    def index() -> Response:
        html = (
            """
            <!doctype html>
            <html>
              <head>
                <meta charset="utf-8">
                <title>Emotion Recognition</title>
                <style>
                  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; padding: 24px; }
                  form { display: grid; gap: 12px; max-width: 520px; }
                  input[type=file] { padding: 8px; border: 1px solid #ccc; border-radius: 6px; }
                  button { padding: 10px 14px; border: none; background: #2563EB; color: #fff; border-radius: 6px; cursor: pointer; }
                  button:hover { background: #1E40AF; }
                  pre { background: #111827; color: #E5E7EB; padding: 12px; border-radius: 6px; overflow: auto; }
                </style>
              </head>
              <body>
                <h1>Upload an audio file</h1>
                <form id="f" action="/predict" method="post" enctype="multipart/form-data">
                  <input type="file" name="file" accept="audio/*" required />
                  <button type="submit">Predict emotion</button>
                </form>
                <h2>Result</h2>
                <pre id="out">(submit a file)</pre>
                <script>
                  const form = document.getElementById('f');
                  const out = document.getElementById('out');
                  form.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const fd = new FormData(form);
                    out.textContent = 'Predicting...';
                    try {
                      const res = await fetch('/predict', { method: 'POST', body: fd });
                      const txt = await res.text();
                      out.textContent = txt;
                    } catch (err) {
                      out.textContent = String(err);
                    }
                  });
                </script>
              </body>
            </html>
            """
        )
        return Response(html, mimetype="text/html")

    def _write_temp_audio(data: bytes, suffix: str = ".wav") -> str:
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        return path

    def _run_prediction(tmp_path: str) -> Tuple[str, float]:
        nonlocal model_path
        if predict_from_file is None:
            raise RuntimeError(f"Inference unavailable: {_import_error}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at MODEL_PATH='{model_path}'")
        return predict_from_file(model_path, tmp_path)

    @app.post("/predict")
    def predict() -> Response:
        try:
            # Priority 1: multipart file field named 'file'
            if "file" in request.files:
                file_storage = request.files["file"]
                filename = secure_filename(file_storage.filename or "audio.wav")
                ext = os.path.splitext(filename)[1] or ".wav"
                data = file_storage.read()
                tmp_path = _write_temp_audio(data, suffix=ext)
                try:
                    label, conf = _run_prediction(tmp_path)
                finally:
                    try:
                        os.remove(tmp_path)
                    except Exception:
                        pass
                return jsonify({"emotion": str(label), "confidence": float(conf)})

            # Priority 2: JSON with base64 string under 'audio_b64'
            if request.is_json:
                payload = request.get_json(silent=True) or {}
                audio_b64 = payload.get("audio_b64")
                if audio_b64:
                    try:
                        raw = base64.b64decode(audio_b64, validate=True)
                    except Exception:
                        return jsonify({"error": "Invalid base64 payload"}), 400
                    tmp_path = _write_temp_audio(raw, suffix=".wav")
                    try:
                        label, conf = _run_prediction(tmp_path)
                    finally:
                        try:
                            os.remove(tmp_path)
                        except Exception:
                            pass
                    return jsonify({"emotion": str(label), "confidence": float(conf)})

            return jsonify({"error": "No audio provided. Use multipart form field 'file' or JSON 'audio_b64'."}), 400

        except FileNotFoundError as e:
            app.logger.warning("Model/file not found: %s", e)
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            app.logger.exception("Prediction failed: %s", e)
            return jsonify({"error": "Prediction failed", "detail": str(e)}), 500

    return app


app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)


