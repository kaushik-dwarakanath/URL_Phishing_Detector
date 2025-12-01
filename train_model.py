import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from url_features import FEATURE_COLUMNS


DATA_PATH = Path("web-page-phishing.csv")
MODEL_DIR = Path("model")
MODEL_PATH = MODEL_DIR / "phishing_model.joblib"


def load_data() -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(DATA_PATH)
    if "phishing" not in df.columns:
        raise ValueError("Expected 'phishing' column in dataset.")

    X = df[FEATURE_COLUMNS]
    y = df["phishing"].astype(int)
    return X, y


def build_pipeline(n_features: int) -> Pipeline:
    numeric_features = list(range(n_features))

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
        ]
    )

    xgb = XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        reg_lambda=1.0,
        n_jobs=-1,
        tree_method="hist",
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", xgb),
        ]
    )

    return pipeline


def train_and_evaluate() -> None:
    X, y = load_data()
    X_train, X_val, y_train, y_val = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline(X_train.shape[1])
    pipeline.fit(X_train, y_train)

    y_proba = pipeline.predict_proba(X_val)[:, 1]

    # Default 0.5 threshold metrics
    y_pred_default = (y_proba >= 0.5).astype(int)

    print("Validation classification report:")
    print(classification_report(y_val, y_pred_default, digits=4))

    try:
        auc = roc_auc_score(y_val, y_proba)
        print(f"Validation ROC-AUC: {auc:.4f}")
    except Exception:
        pass

    # Tune a conservative decision threshold:
    # - Aim for high specificity on legitimate URLs (class 0),
    #   i.e. most real sites should be classified as safe.
    # - Among thresholds with good specificity, pick the one with best recall
    #   for phishing (class 1).
    best_threshold = 0.5
    best_spec_legit = 0.0
    best_rec_phish = 0.0

    for thr in np.linspace(0.1, 0.99, 45):
        y_pred_thr = (y_proba >= thr).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_val, y_pred_thr).ravel()
        # Specificity for legitimate class (0): TN / (TN + FP)
        spec_legit = tn / (tn + fp) if (tn + fp) > 0 else 0.0
        # Recall for phishing class (1): TP / (TP + FN)
        rec_phish = tp / (tp + fn) if (tp + fn) > 0 else 0.0

        # Prefer thresholds with high specificity; within that, better phishing recall
        if (spec_legit > best_spec_legit + 1e-3) or (
            abs(spec_legit - best_spec_legit) < 1e-3 and rec_phish > best_rec_phish
        ):
            best_spec_legit = spec_legit
            best_rec_phish = rec_phish
            best_threshold = float(thr)

    # As a safety net, clamp the threshold so we never classify as phishing
    # unless the model is extremely confident. This heavily reduces
    # false positives on popular legitimate sites.
    best_threshold = max(best_threshold, 0.99)

    print(
        f"Selected decision threshold={best_threshold:.3f} "
        f"(legit specificity={best_spec_legit:.4f}, phishing recall={best_rec_phish:.4f})"
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "feature_columns": FEATURE_COLUMNS,
            "decision_threshold": best_threshold,
        },
        MODEL_PATH,
    )
    print(f"Saved model to {MODEL_PATH.resolve()}")


if __name__ == "__main__":
    train_and_evaluate()


