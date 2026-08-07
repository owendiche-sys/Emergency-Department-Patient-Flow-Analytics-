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
    df = pd.read_csv(DATA_PATH, na_values=["NULL", "", " "])
    model_df = df[df["wait_time_minutes"].notna()].copy()
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


def evaluate_model(name, model, x_train, x_test, y_train, y_test) -> dict:
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "model": name,
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions, zero_division=0),
        "recall": recall_score(y_test, predictions, zero_division=0),
        "f1": f1_score(y_test, predictions, zero_division=0),
        "roc_auc": None,
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_test)[:, 1]
        metrics["roc_auc"] = roc_auc_score(y_test, probabilities)

    tn, fp, fn, tp = confusion_matrix(y_test, predictions).ravel()
    metrics.update({"true_negative": tn, "false_positive": fp, "false_negative": fn, "true_positive": tp})

    return metrics


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

    preprocessor = build_preprocessor(model_df)

    models = [
        ("majority_class_baseline", DummyClassifier(strategy="most_frequent")),
        (
            "logistic_regression_balanced",
            Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
                    ("model", LogisticRegression(max_iter=1000, class_weight="balanced")),
                ]
            ),
        ),
        (
            "random_forest_balanced",
            Pipeline(
                steps=[
                    ("preprocessor", preprocessor),
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

    results = [evaluate_model(name, model, x_train, x_test, y_train, y_test) for name, model in models]
    metrics_df = pd.DataFrame(results)
    metrics_df.to_csv(OUTPUT_DIR / "week5_wait_prediction_model_metrics.csv", index=False)

    best_model_name = metrics_df.sort_values(["f1", "roc_auc"], ascending=False).iloc[0]["model"]
    best_model = dict(models)[best_model_name]
    joblib.dump(best_model, OUTPUT_DIR / "week5_best_wait_prediction_model.joblib")

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
    target_summary.to_csv(OUTPUT_DIR / "week5_wait_target_balance.csv", index=False)

    print(metrics_df.to_string(index=False))
    print(f"Best model saved: {best_model_name}")


if __name__ == "__main__":
    main()
