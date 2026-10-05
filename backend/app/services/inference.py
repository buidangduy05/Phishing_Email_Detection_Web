from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from gensim.models.doc2vec import Doc2Vec

from app.core.config import ARTIFACTS_DIR
from app.services.feature_extractor import FEATURE_NAMES
from app.services.preprocessing import tokenize


class InferenceResult:
    def __init__(self, is_phishing: bool, model: str) -> None:
        self.is_phishing = is_phishing
        self.model = model


@lru_cache(maxsize=1)
def _load_artifacts() -> tuple[Doc2Vec, Any, Any] | None:
    paths = (
        ARTIFACTS_DIR / "doc2vec.model",
        ARTIFACTS_DIR / "feature_scaler.pkl",
        ARTIFACTS_DIR / "selected_model.pkl",
    )
    present = [path.is_file() for path in paths]
    if not any(present):
        return None
    if not all(present):
        missing = ", ".join(path.name for path, exists in zip(paths, present) if not exists)
        raise RuntimeError(f"Incomplete model artifacts; missing: {missing}.")
    doc2vec = Doc2Vec.load(str(paths[0]))
    scaler = joblib.load(paths[1])
    model = joblib.load(paths[2])
    return doc2vec, scaler, model


def _is_positive_label(label: Any) -> bool:
    if isinstance(label, (bool, np.bool_)):
        return bool(label)
    if isinstance(label, (int, np.integer, float, np.floating)) and label in (0, 1):
        return bool(label)
    normalized = str(label).strip().lower()
    if normalized in {"1", "true", "phishing", "phish", "spam", "malicious"}:
        return True
    if normalized in {"0", "false", "legitimate", "ham", "safe", "benign"}:
        return False
    raise RuntimeError(f"Unsupported class label in selected_model.pkl: {label!r}.")


def _rule_based_result(features: dict[str, float]) -> InferenceResult:
    weights = {
        "sender_reply_to_domain_mismatch": 2,
        "sender_return_path_domain_mismatch": 1,
        "sender_display_name_mismatch": 1,
        "urgency_word_count": 1,
        "credential_word_count": 2,
        "threat_word_count": 1,
        "shortener_url_count": 2,
        "ip_url_count": 2,
        "html_has_form": 2,
        "html_has_password_input": 3,
        "html_has_iframe": 1,
        "html_has_hidden_element": 1,
        "link_text_mismatch_count": 2,
        "url_uses_punycode": 2,
    }
    risk_score = sum(weight for name, weight in weights.items() if features.get(name, 0) > 0)
    return InferenceResult(risk_score >= 3, "heuristic-fallback")


def predict_email(
    subject: str,
    body: str,
    features: dict[str, float],
) -> InferenceResult:
    artifacts = _load_artifacts()
    if artifacts is None:
        return _rule_based_result(features)

    doc2vec, scaler, model = artifacts
    embedding = np.asarray(doc2vec.infer_vector(tokenize(f"{subject} {body}")), dtype=float).reshape(1, -1)
    feature_vector = np.asarray([[features[name] for name in FEATURE_NAMES]], dtype=float)
    combined = np.concatenate((embedding, feature_vector), axis=1)
    scaler_size = getattr(scaler, "n_features_in_", None)
    if scaler_size == len(FEATURE_NAMES):
        transformed = np.concatenate((embedding, scaler.transform(feature_vector)), axis=1)
    elif scaler_size in (None, combined.shape[1]):
        transformed = scaler.transform(combined)
    else:
        raise RuntimeError(
            f"feature_scaler.pkl expects {scaler_size} features; expected "
            f"{len(FEATURE_NAMES)} or {combined.shape[1]}."
        )
    model_size = getattr(model, "n_features_in_", transformed.shape[1])
    if model_size != transformed.shape[1]:
        raise RuntimeError(
            f"selected_model.pkl expects {model_size} features; received {transformed.shape[1]}."
        )
    prediction = model.predict(transformed)[0]
    return InferenceResult(_is_positive_label(prediction), "doc2vec-model")
