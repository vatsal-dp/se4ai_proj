#!/usr/bin/env python3
"""Colab-first Apr 20 pilot workflow for Cloudify CI failure prediction.

This script is designed to be run inside Google Colab (either in a cell via
`!python` or by copy/pasting blocks). It produces three outputs:
  - pilot_fold_metrics.csv
  - pilot_summary.json
  - colab_run_log.txt
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import random
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

TARGET_COLUMN = "build_Failed"
TIMESTAMP_COLUMN = "gh_build_started_at"
DEFAULT_DATASET_REL = (
    "mar30_submission/reproduction/work/DL-CIBuild/dataset/cloudify.csv"
)
DEFAULT_DATASET_CANDIDATE_RELS = [
    DEFAULT_DATASET_REL,
    "reproduction/work/DL-CIBuild/dataset/cloudify.csv",
    "DL-CIBuild/dataset/cloudify.csv",
    "dataset/cloudify.csv",
]
DEFAULT_DL_CIBUILD_REPO_REL = "mar30_submission/reproduction/work/DL-CIBuild"
DEFAULT_NUM_FOLDS = 5
DEFAULT_SEED = 42

METRIC_COLUMNS = [
    "auc",
    "f1",
    "accuracy",
    "precision",
    "recall",
    "train_time_sec",
]
CSV_COLUMNS = [
    "model",
    "fold",
    "train_rows",
    "test_rows",
    "status",
    "reason",
    "auc",
    "f1",
    "accuracy",
    "precision",
    "recall",
    "train_time_sec",
    "seed",
]


@dataclass
class RunLogger:
    lines: List[str] = field(default_factory=list)

    def log(self, message: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        line = f"{timestamp} | {message}"
        self.lines.append(line)
        print(line)

    def dump(self, path: Path) -> None:
        text = "\n".join(self.lines).strip() + "\n"
        path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[2]

    parser = argparse.ArgumentParser(
        description="Run Apr20 Colab-first CI failure pilot on cloudify.csv"
    )
    parser.add_argument(
        "--repo-root",
        default=str(default_repo_root),
        help="Absolute path to repository root.",
    )
    parser.add_argument(
        "--dataset-relpath",
        default=DEFAULT_DATASET_REL,
        help="Path to cloudify.csv relative to --repo-root.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where outputs will be written.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="Random seed for deterministic baselines.",
    )
    parser.add_argument(
        "--skip-dl-cibuild",
        action="store_true",
        help="Skip DL-CIBuild execution even if dependencies are available.",
    )
    return parser.parse_args()


def set_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def to_optional_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        out = float(value)
        if np.isnan(out):
            return None
        return out
    except Exception:
        return None


def safe_auc(y_true: Sequence[int], y_score: Sequence[float]) -> Optional[float]:
    y_true_arr = np.asarray(y_true).reshape(-1)
    y_score_arr = np.asarray(y_score).reshape(-1)
    if len(np.unique(y_true_arr)) < 2:
        return None
    try:
        return float(roc_auc_score(y_true_arr, y_score_arr))
    except Exception:
        return None


def compute_classification_metrics(
    y_true: Sequence[int], y_pred: Sequence[int], y_score: Sequence[float]
) -> Dict[str, Optional[float]]:
    y_true_arr = np.asarray(y_true).reshape(-1)
    y_pred_arr = np.asarray(y_pred).reshape(-1)
    y_score_arr = np.asarray(y_score).reshape(-1)
    return {
        "auc": safe_auc(y_true_arr, y_score_arr),
        "f1": to_optional_float(f1_score(y_true_arr, y_pred_arr, zero_division=0)),
        "accuracy": to_optional_float(accuracy_score(y_true_arr, y_pred_arr)),
        "precision": to_optional_float(
            precision_score(y_true_arr, y_pred_arr, zero_division=0)
        ),
        "recall": to_optional_float(recall_score(y_true_arr, y_pred_arr, zero_division=0)),
    }


def _unique_paths(paths: Iterable[Path]) -> List[Path]:
    seen: set[str] = set()
    out: List[Path] = []
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        out.append(path)
    return out


def resolve_dataset_path(repo_root: Path, dataset_relpath: str, logger: RunLogger) -> Path:
    requested = Path(dataset_relpath).expanduser()
    requested_candidate = requested if requested.is_absolute() else (repo_root / requested)

    candidates: List[Path] = [requested_candidate]
    for rel in DEFAULT_DATASET_CANDIDATE_RELS:
        candidates.append(repo_root / rel)
    candidates = _unique_paths(candidates)

    existing = [path for path in candidates if path.exists() and path.is_file()]
    if existing:
        chosen = existing[0]
        if chosen != requested_candidate:
            logger.log(
                "Requested dataset path was missing; auto-resolved cloudify.csv at: "
                f"{chosen}"
            )
        return chosen

    # Final fallback for Colab/local layout drift: search the repo for cloudify.csv.
    discovered = sorted(
        [path for path in repo_root.rglob("cloudify.csv") if path.is_file()],
        key=lambda path: (len(path.parts), str(path)),
    )
    if discovered:
        chosen = discovered[0]
        logger.log(
            "Requested dataset path was missing; discovered cloudify.csv by recursive "
            f"search at: {chosen}"
        )
        return chosen

    checked = "\n".join(f"  - {path}" for path in candidates)
    raise FileNotFoundError(
        "Dataset not found. Checked the following paths:\n"
        f"{checked}\n"
        "Also searched recursively under repo root for 'cloudify.csv' with no match.\n"
        "Provide an explicit dataset location with:\n"
        "  --dataset-relpath <relative-or-absolute-path-to-cloudify.csv>"
    )


def load_dataset(repo_root: Path, dataset_relpath: str, logger: RunLogger) -> pd.DataFrame:
    dataset_path = resolve_dataset_path(
        repo_root=repo_root,
        dataset_relpath=dataset_relpath,
        logger=logger,
    )

    logger.log(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path, parse_dates=[TIMESTAMP_COLUMN])

    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Required target column '{TARGET_COLUMN}' is missing.")
    if TIMESTAMP_COLUMN not in df.columns:
        raise ValueError(f"Required timestamp column '{TIMESTAMP_COLUMN}' is missing.")

    df = df.sort_values(TIMESTAMP_COLUMN).reset_index(drop=True)
    logger.log(f"Loaded {len(df)} rows and {len(df.columns)} columns.")
    return df


def online_validation_folds(df: pd.DataFrame) -> Tuple[List[pd.DataFrame], List[pd.DataFrame], int]:
    train_sets: List[pd.DataFrame] = []
    test_sets: List[pd.DataFrame] = []
    fold_size = int(len(df) * 0.1)
    for i in range(6, 11):
        train_sets.append(df.iloc[0 : (fold_size * (i - 1))].copy())
        test_sets.append(df.iloc[(fold_size * (i - 1)) : (fold_size * i)].copy())
    return train_sets, test_sets, fold_size


def preprocess_datetime_columns(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    for col in out.columns:
        if np.issubdtype(out[col].dtype, np.datetime64):
            out[col] = out[col].astype("int64") // 10**9
    return out


def split_xy(frame: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    x = frame.drop(columns=[TARGET_COLUMN])
    y = frame[TARGET_COLUMN].astype(int).to_numpy()
    return x, y


def run_majority_baseline(
    train_df: pd.DataFrame, test_df: pd.DataFrame, model_name: str = "majority_class"
) -> Dict[str, Any]:
    _, y_train = split_xy(train_df)
    _, y_test = split_xy(test_df)

    start = time.perf_counter()
    majority_class = int(pd.Series(y_train).mode(dropna=False).iloc[0])
    train_time = time.perf_counter() - start

    positive_rate = float(np.mean(y_train))
    y_pred = np.full(shape=len(y_test), fill_value=majority_class, dtype=int)
    y_score = np.full(shape=len(y_test), fill_value=positive_rate, dtype=float)

    metrics = compute_classification_metrics(y_test, y_pred, y_score)
    return {
        "model": model_name,
        "status": "ok",
        "reason": "",
        "train_time_sec": train_time,
        **metrics,
    }


def build_logistic_pipeline(x_train: pd.DataFrame, seed: int) -> Pipeline:
    numeric_cols = list(x_train.select_dtypes(include=["number", "bool"]).columns)
    categorical_cols = [col for col in x_train.columns if col not in numeric_cols]

    transformers: List[Tuple[str, Pipeline, List[str]]] = [
        (
            "num",
            Pipeline(
                steps=[
                    ("impute", SimpleImputer(strategy="median")),
                    ("scale", StandardScaler()),
                ]
            ),
            numeric_cols,
        )
    ]
    if categorical_cols:
        transformers.append(
            (
                "cat",
                Pipeline(
                    steps=[
                        ("impute", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_cols,
            )
        )

    preprocessor = ColumnTransformer(transformers=transformers)
    classifier = LogisticRegression(max_iter=1000, random_state=seed)
    return Pipeline(steps=[("prep", preprocessor), ("clf", classifier)])


def run_logistic_baseline(
    train_df: pd.DataFrame, test_df: pd.DataFrame, seed: int
) -> Dict[str, Any]:
    x_train, y_train = split_xy(train_df)
    x_test, y_test = split_xy(test_df)

    x_train = preprocess_datetime_columns(x_train)
    x_test = preprocess_datetime_columns(x_test)

    if len(np.unique(y_train)) < 2:
        return {
            "model": "logistic_regression",
            "status": "not_run",
            "reason": "Training fold has a single class; logistic regression requires two classes.",
            "auc": None,
            "f1": None,
            "accuracy": None,
            "precision": None,
            "recall": None,
            "train_time_sec": None,
        }

    model = build_logistic_pipeline(x_train, seed)
    start = time.perf_counter()
    model.fit(x_train, y_train)
    train_time = time.perf_counter() - start

    y_score = model.predict_proba(x_test)[:, 1]
    y_pred = (y_score >= 0.5).astype(int)
    metrics = compute_classification_metrics(y_test, y_pred, y_score)
    return {
        "model": "logistic_regression",
        "status": "ok",
        "reason": "",
        "train_time_sec": train_time,
        **metrics,
    }


def modules_missing(module_names: Iterable[str]) -> List[str]:
    missing = []
    for name in module_names:
        if importlib.util.find_spec(name) is None:
            missing.append(name)
    return missing


def dl_not_run_rows(reason: str, seed: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for fold in range(1, DEFAULT_NUM_FOLDS + 1):
        rows.append(
            {
                "model": "dl_cibuild_default",
                "fold": fold,
                "train_rows": None,
                "test_rows": None,
                "status": "not_run",
                "reason": reason,
                "auc": None,
                "f1": None,
                "accuracy": None,
                "precision": None,
                "recall": None,
                "train_time_sec": None,
                "seed": seed,
            }
        )
    return rows


def run_dl_cibuild_default(
    repo_root: Path, seed: int, logger: RunLogger
) -> List[Dict[str, Any]]:
    dl_repo = repo_root / DEFAULT_DL_CIBUILD_REPO_REL
    scripts_dir = dl_repo / "DL-CIBuild scripts"

    if not dl_repo.exists():
        return dl_not_run_rows(f"Missing DL-CIBuild path: {dl_repo}", seed)
    if not scripts_dir.exists():
        return dl_not_run_rows(f"Missing DL-CIBuild scripts path: {scripts_dir}", seed)

    missing = modules_missing(["tensorflow", "keras"])
    if missing:
        reason = f"Missing DL-CIBuild runtime dependencies: {', '.join(missing)}"
        logger.log(reason)
        return dl_not_run_rows(reason, seed)

    current_cwd = Path.cwd()
    rows: List[Dict[str, Any]] = []

    try:
        os.chdir(dl_repo)
        scripts_path = str(scripts_dir.resolve())
        if scripts_path not in sys.path:
            sys.path.insert(0, scripts_path)

        import Utils as DLUtils  # type: ignore
        import LSTM_Tuner as DLLSTM  # type: ignore

        dataset = DLUtils.getDataset("cloudify.csv")
        train_sets, test_sets = DLUtils.online_validation_folds(dataset)
        logger.log(
            f"DL-CIBuild online folds loaded: train/test pairs={len(train_sets)} / {len(test_sets)}"
        )

        for fold_index, (train_set, test_set) in enumerate(zip(train_sets, test_sets), start=1):
            row = {
                "model": "dl_cibuild_default",
                "fold": fold_index,
                "train_rows": int(len(train_set)),
                "test_rows": int(len(test_set)),
                "status": "ok",
                "reason": "",
                "auc": None,
                "f1": None,
                "accuracy": None,
                "precision": None,
                "recall": None,
                "train_time_sec": None,
                "seed": seed,
            }

            try:
                fold_start = time.perf_counter()
                entry_train = DLLSTM.evaluate_tuner("default", train_set)
                time_step = int(entry_train["params"]["time_step"])
                x_test, y_test = DLLSTM.test_preprocess(train_set, test_set, time_step)
                entry_test = DLUtils.predict_lstm(entry_train["model"], x_test, y_test)

                # Reconstruct precision/recall from predicted probabilities using
                # DL-CIBuild thresholding behavior.
                y_true = np.asarray(y_test).reshape(-1).astype(int)
                y_score = np.asarray(entry_train["model"].predict(x_test)).reshape(-1)

                if getattr(DLUtils, "with_smote", False) and not getattr(
                    DLUtils, "hybrid_option", False
                ):
                    decision_threshold = 0.5
                else:
                    try:
                        decision_threshold = float(DLUtils.getBestThreshold(y_score, y_true))
                    except Exception:
                        decision_threshold = 0.5

                y_pred = (y_score >= decision_threshold).astype(int)

                row.update(
                    {
                        "auc": to_optional_float(entry_test.get("AUC"))
                        or safe_auc(y_true, y_score),
                        "f1": to_optional_float(entry_test.get("F1"))
                        or to_optional_float(f1_score(y_true, y_pred, zero_division=0)),
                        "accuracy": to_optional_float(entry_test.get("accuracy"))
                        or to_optional_float(accuracy_score(y_true, y_pred)),
                        "precision": to_optional_float(
                            precision_score(y_true, y_pred, zero_division=0)
                        ),
                        "recall": to_optional_float(recall_score(y_true, y_pred, zero_division=0)),
                        "train_time_sec": to_optional_float(entry_train.get("time"))
                        or (time.perf_counter() - fold_start),
                    }
                )
            except Exception as exc:
                row.update(
                    {
                        "status": "error",
                        "reason": f"{type(exc).__name__}: {exc}",
                        "auc": None,
                        "f1": None,
                        "accuracy": None,
                        "precision": None,
                        "recall": None,
                        "train_time_sec": None,
                    }
                )
                logger.log(
                    f"DL-CIBuild fold {fold_index} failed: {type(exc).__name__}: {exc}"
                )
                logger.log(traceback.format_exc())

            rows.append(row)

        # If DL-CIBuild returns fewer folds than expected, pad for schema stability.
        if len(rows) < DEFAULT_NUM_FOLDS:
            missing_count = DEFAULT_NUM_FOLDS - len(rows)
            logger.log(
                f"DL-CIBuild returned {len(rows)} folds; padding {missing_count} fold(s) as not_run."
            )
            for fold in range(len(rows) + 1, DEFAULT_NUM_FOLDS + 1):
                rows.append(
                    {
                        "model": "dl_cibuild_default",
                        "fold": fold,
                        "train_rows": None,
                        "test_rows": None,
                        "status": "not_run",
                        "reason": "DL-CIBuild returned fewer folds than expected.",
                        "auc": None,
                        "f1": None,
                        "accuracy": None,
                        "precision": None,
                        "recall": None,
                        "train_time_sec": None,
                        "seed": seed,
                    }
                )
    except Exception as exc:
        reason = f"DL-CIBuild setup/import failed: {type(exc).__name__}: {exc}"
        logger.log(reason)
        logger.log(traceback.format_exc())
        return dl_not_run_rows(reason, seed)
    finally:
        os.chdir(current_cwd)

    return rows[:DEFAULT_NUM_FOLDS]


def summarize_series(series: pd.Series) -> Dict[str, Optional[float]]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {
            "count": 0,
            "mean": None,
            "std": None,
            "median": None,
            "iqr": None,
            "min": None,
            "max": None,
        }
    q1 = float(clean.quantile(0.25))
    q3 = float(clean.quantile(0.75))
    return {
        "count": int(clean.shape[0]),
        "mean": float(clean.mean()),
        "std": float(clean.std(ddof=0)),
        "median": float(clean.median()),
        "iqr": float(q3 - q1),
        "min": float(clean.min()),
        "max": float(clean.max()),
    }


def compute_pairwise_deltas(
    metrics_df: pd.DataFrame, left_model: str, right_model: str, fields: Sequence[str]
) -> Dict[str, Any]:
    left = metrics_df[
        (metrics_df["model"] == left_model) & (metrics_df["status"] == "ok")
    ][["fold", *fields]].copy()
    right = metrics_df[
        (metrics_df["model"] == right_model) & (metrics_df["status"] == "ok")
    ][["fold", *fields]].copy()

    if left.empty or right.empty:
        return {
            "left_model": left_model,
            "right_model": right_model,
            "folds_compared": [],
            "metrics": {field: {"mean_delta": None, "median_delta": None} for field in fields},
        }

    merged = left.merge(right, on="fold", suffixes=("_left", "_right"))
    out: Dict[str, Any] = {
        "left_model": left_model,
        "right_model": right_model,
        "folds_compared": sorted(merged["fold"].astype(int).tolist()),
        "metrics": {},
    }

    for field in fields:
        delta = pd.to_numeric(merged[f"{field}_left"], errors="coerce") - pd.to_numeric(
            merged[f"{field}_right"], errors="coerce"
        )
        delta = delta.dropna()
        if delta.empty:
            out["metrics"][field] = {"mean_delta": None, "median_delta": None}
        else:
            out["metrics"][field] = {
                "mean_delta": float(delta.mean()),
                "median_delta": float(delta.median()),
            }
    return out


def build_summary(
    metrics_df: pd.DataFrame,
    dataset_rows: int,
    fold_size: int,
    seed: int,
    skip_dl_cibuild: bool,
) -> Dict[str, Any]:
    models_summary: Dict[str, Any] = {}
    for model_name, group in metrics_df.groupby("model"):
        ok_group = group[group["status"] == "ok"]
        models_summary[model_name] = {
            "row_count": int(group.shape[0]),
            "status_counts": {k: int(v) for k, v in group["status"].value_counts().to_dict().items()},
            "metrics": {field: summarize_series(ok_group[field]) for field in METRIC_COLUMNS},
        }

    pairwise = compute_pairwise_deltas(
        metrics_df,
        left_model="logistic_regression",
        right_model="majority_class",
        fields=["auc", "f1", "accuracy", "precision", "recall"],
    )

    return {
        "run_metadata": {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "seed": seed,
            "skip_dl_cibuild": skip_dl_cibuild,
            "script": "apr20_submission/colab/apr20_pilot_colab.py",
        },
        "dataset": {
            "name": "cloudify.csv",
            "rows": int(dataset_rows),
            "target_column": TARGET_COLUMN,
            "timestamp_column": TIMESTAMP_COLUMN,
        },
        "fold_protocol": {
            "num_folds": DEFAULT_NUM_FOLDS,
            "fold_size": int(fold_size),
            "definition": "fold_size=int(n*0.1); for i in 6..10: train=0:fold_size*(i-1), test=fold_size*(i-1):fold_size*i",
        },
        "models": models_summary,
        "pairwise_deltas": {
            "logistic_minus_majority": pairwise,
        },
    }


def main() -> int:
    args = parse_args()
    logger = RunLogger()
    set_determinism(args.seed)

    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.log(f"Repo root: {repo_root}")
    logger.log(f"Output dir: {output_dir}")
    logger.log(f"Seed: {args.seed}")
    logger.log(f"skip_dl_cibuild: {args.skip_dl_cibuild}")

    df = load_dataset(repo_root, args.dataset_relpath, logger)
    train_sets, test_sets, fold_size = online_validation_folds(df)
    logger.log(
        f"Computed online folds using repo logic (i=6..10): fold_size={fold_size}, pairs={len(train_sets)}"
    )

    rows: List[Dict[str, Any]] = []

    for fold_index, (train_df, test_df) in enumerate(zip(train_sets, test_sets), start=1):
        logger.log(
            f"Fold {fold_index}: train_rows={len(train_df)}, test_rows={len(test_df)}"
        )

        base = {
            "fold": fold_index,
            "train_rows": int(len(train_df)),
            "test_rows": int(len(test_df)),
            "seed": args.seed,
        }

        # Majority class baseline
        try:
            maj = run_majority_baseline(train_df, test_df)
        except Exception as exc:
            logger.log(f"majority_class failed on fold {fold_index}: {type(exc).__name__}: {exc}")
            logger.log(traceback.format_exc())
            maj = {
                "model": "majority_class",
                "status": "error",
                "reason": f"{type(exc).__name__}: {exc}",
                "auc": None,
                "f1": None,
                "accuracy": None,
                "precision": None,
                "recall": None,
                "train_time_sec": None,
            }
        rows.append({**base, **maj})

        # Logistic regression baseline
        try:
            logreg = run_logistic_baseline(train_df, test_df, seed=args.seed)
        except Exception as exc:
            logger.log(
                f"logistic_regression failed on fold {fold_index}: {type(exc).__name__}: {exc}"
            )
            logger.log(traceback.format_exc())
            logreg = {
                "model": "logistic_regression",
                "status": "error",
                "reason": f"{type(exc).__name__}: {exc}",
                "auc": None,
                "f1": None,
                "accuracy": None,
                "precision": None,
                "recall": None,
                "train_time_sec": None,
            }
        rows.append({**base, **logreg})

    # Optional DL-CIBuild default model.
    if args.skip_dl_cibuild:
        logger.log("Skipping DL-CIBuild path due to --skip-dl-cibuild.")
        rows.extend(dl_not_run_rows("Skipped by --skip-dl-cibuild flag.", args.seed))
    else:
        logger.log("Attempting DL-CIBuild default-model execution.")
        dl_rows = run_dl_cibuild_default(repo_root=repo_root, seed=args.seed, logger=logger)
        rows.extend(dl_rows)

    metrics_df = pd.DataFrame(rows)
    for col in CSV_COLUMNS:
        if col not in metrics_df.columns:
            metrics_df[col] = None
    metrics_df = metrics_df[CSV_COLUMNS].sort_values(by=["model", "fold"]).reset_index(drop=True)

    metrics_path = output_dir / "pilot_fold_metrics.csv"
    summary_path = output_dir / "pilot_summary.json"
    log_path = output_dir / "colab_run_log.txt"

    metrics_df.to_csv(metrics_path, index=False)
    summary = build_summary(
        metrics_df=metrics_df,
        dataset_rows=len(df),
        fold_size=fold_size,
        seed=args.seed,
        skip_dl_cibuild=args.skip_dl_cibuild,
    )
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.log(f"Wrote metrics: {metrics_path}")
    logger.log(f"Wrote summary: {summary_path}")
    logger.log("Run complete.")
    logger.dump(log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
