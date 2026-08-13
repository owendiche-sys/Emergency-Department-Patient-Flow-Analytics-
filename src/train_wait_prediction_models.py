"""Train and evaluate leakage-controlled extended-wait classifiers."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "nhamcs_2022_visits_clean.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "models"

TARGET = "extended_wait_2hr_flag"
FEATURES = [
    "visit_month",
    "visit_day",
    "arrival_hour",
    "age_years",
    "sex",
    "residence_type",
    "arrival_by_ambulance",
    "ambulance_transfer",
    "triage_level",
    "pain_scale",
    "pulse_bpm",
    "respiratory_rate",
    "systolic_bp",
    "diastolic_bp",
    "oxygen_saturation",
    "temperature_f",
    "chronic_condition_count",
    "region",
    "metropolitan_status",
]
LEAKAGE_FIELDS = {
    "wait_time_minutes",
    "visit_length_minutes",
    "left_without_being_seen",
    "left_before_treatment_complete",
    "left_against_medical_advice",
    "died_in_ed",
    "admitted_to_hospital",
    "observation_then_hospitalized",
    "observation_then_discharged",
    "admission_destination",
}


def load_model_data() -> pd.DataFrame:
    """Load visits with a known modelling target."""
    df = pd.read_csv(DATA_PATH, na_values=["NULL", "", " "])
    missing = sorted(set(FEATURES + [TARGET, "long_wait_4hr_flag"]) - set(df.columns))
    if missing:
        raise ValueError(f"Model data is missing required columns: {missing}")

    model_df = df[df[TARGET].notna()].copy()
    model_df[TARGET] = model_df[TARGET].astype(int)
    return model_df


def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    numeric_features = df[FEATURES].select_dtypes(include="number").columns.tolist()
    categorical_features = [column for column in FEATURES if column not in numeric_features]

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_features),
            ("categorical", categorical_pipeline, categorical_features),
        ]
    )


def build_models(df: pd.DataFrame) -> list[tuple[str, object]]:
    """Build independent pipelines so model fits cannot share transformer state."""
    return [
        ("majority_class_baseline", DummyClassifier(strategy="most_frequent")),
        (
            "logistic_regression_balanced",
            Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(df)),
                    ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
                ]
            ),
        ),
        (
            "random_forest_balanced",
            Pipeline(
                steps=[
                    ("preprocessor", build_preprocessor(df)),
                    (
                        "model",
                        RandomForestClassifier(
                            n_estimators=250,
                            min_samples_leaf=20,
                            class_weight="balanced",
                            random_state=42,
                            n_jobs=-1,
                        ),
                    ),
                ]
            ),
        ),
    ]


def evaluate_model(name, model, x_train, x_test, y_train, y_test) -> dict[str, float | int | str]:
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics: dict[str, float | int | str] = {
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),
        "balanced_accuracy": balanced_accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": 0.5,
        "pr_auc": float(y_test.mean()),
    }
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_test)[:, 1]
        metrics["roc_auc"] = roc_auc_score(y_test, probabilities)
        metrics["pr_auc"] = average_precision_score(y_test, probabilities)

    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    metrics.update(
        {
            "true_negative": int(tn),
            "false_positive": int(fp),
            "false_negative": int(fn),
            "true_positive": int(tp),
        }
    )
    return metrics


def write_feature_importance(model: Pipeline) -> None:
    preprocessor = model.named_steps["preprocessor"]
    estimator = model.named_steps["model"]
    feature_names = preprocessor.get_feature_names_out()

    if hasattr(estimator, "feature_importances_"):
        importance = estimator.feature_importances_
    elif hasattr(estimator, "coef_"):
        importance = abs(estimator.coef_[0])
    else:
        return

    feature_frame = (
        pd.DataFrame({"feature": feature_names, "importance": importance})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    feature_frame.to_csv(OUTPUT_DIR / "wait_prediction_feature_importance.csv", index=False)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if set(FEATURES).intersection(LEAKAGE_FIELDS):
        raise ValueError("Feature list contains post-arrival leakage fields.")

    model_df = load_model_data()
    x = model_df[FEATURES]
    y = model_df[TARGET]
    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    models = build_models(model_df)
    results = [evaluate_model(name, model, x_train, x_test, y_train, y_test) for name, model in models]
    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv(OUTPUT_DIR / "wait_prediction_model_metrics.csv", index=False)

    best_model_name = metrics_df.sort_values(["f1", "pr_auc", "recall"], ascending=False).iloc[0]["model"]
    best_model = dict(models)[best_model_name]
    joblib.dump(best_model, OUTPUT_DIR / "wait_prediction_model.joblib")
    if isinstance(best_model, Pipeline):
        write_feature_importance(best_model)

    target_summary = pd.DataFrame(
        {
            "target": ["extended_wait_2hr_flag", "long_wait_4hr_flag"],
            "positive_cases": [
                int(model_df["extended_wait_2hr_flag"].sum()),
                int(model_df["long_wait_4hr_flag"].sum()),
            ],
            "positive_rate_valid_waits": [
                model_df["extended_wait_2hr_flag"].mean() * 100,
                model_df["long_wait_4hr_flag"].mean() * 100,
            ],
        }
    )
    target_summary.to_csv(OUTPUT_DIR / "wait_target_balance.csv", index=False)

    metadata = {
        "target": TARGET,
        "features": FEATURES,
        "excluded_post_arrival_fields": sorted(LEAKAGE_FIELDS),
        "training_rows": len(x_train),
        "test_rows": len(x_test),
        "test_size": 0.2,
        "random_state": 42,
        "selected_model": best_model_name,
    }
    (OUTPUT_DIR / "wait_prediction_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )

    print(metrics_df.to_string(index=False))
    print(f"Selected model: {best_model_name}")


if __name__ == "__main__":
    main()
