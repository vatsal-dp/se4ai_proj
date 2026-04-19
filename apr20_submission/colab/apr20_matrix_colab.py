#!/usr/bin/env python3
"""Colab-first experiment matrix runner for Apr 20 pilot baselines.

This script runs setup variants with repeated seeds, then writes:
  - matrix_fold_metrics.csv
  - matrix_summary.json
  - matrix_run_log.txt
"""

from __future__ import annotations

import argparse
import json
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import pandas as pd

import apr20_pilot_colab as pilot

DEFAULT_EXPERIMENT_NAME = "apr20_logreg_parameter_sensitivity"
DEFAULT_REPEATS = 8
DEFAULT_BASE_SEED = 42
DEFAULT_TASKS = ("majority_class", "logistic_regression")
TASK_CHOICES = ("majority_class", "logistic_regression", "dl_cibuild_default")
DEFAULT_MAX_FOLDS = pilot.DEFAULT_NUM_FOLDS
DEFAULT_PROGRESS_EVERY = 0
DEFAULT_HEARTBEAT_SEC = 120

METRIC_FIELDS = ["auc", "f1", "accuracy", "precision", "recall"]
CSV_COLUMNS = [
    "experiment",
    "setup",
    "repeat",
    "seed",
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
    "logreg_c",
    "logreg_max_iter",
    "logreg_class_weight",
    "decision_threshold",
    "train_fraction",
]


@dataclass(frozen=True)
class SetupVariant:
    name: str
    logreg_c: float
    logreg_max_iter: int
    logreg_class_weight: str
    decision_threshold: float
    train_fraction: float


DEFAULT_SETUPS: Sequence[SetupVariant] = (
    SetupVariant(
        name="baseline",
        logreg_c=1.0,
        logreg_max_iter=1000,
        logreg_class_weight="none",
        decision_threshold=0.50,
        train_fraction=1.00,
    ),
    SetupVariant(
        name="conservative_regularization",
        logreg_c=0.30,
        logreg_max_iter=1000,
        logreg_class_weight="none",
        decision_threshold=0.50,
        train_fraction=1.00,
    ),
    SetupVariant(
        name="expressive_regularization",
        logreg_c=3.00,
        logreg_max_iter=1000,
        logreg_class_weight="none",
        decision_threshold=0.50,
        train_fraction=1.00,
    ),
    SetupVariant(
        name="short_history",
        logreg_c=1.0,
        logreg_max_iter=500,
        logreg_class_weight="none",
        decision_threshold=0.50,
        train_fraction=0.70,
    ),
    SetupVariant(
        name="long_history",
        logreg_c=1.0,
        logreg_max_iter=2000,
        logreg_class_weight="balanced",
        decision_threshold=0.50,
        train_fraction=1.00,
    ),
)


def parse_csv_list(value: str) -> List[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[2]
    default_setups = ",".join(setup.name for setup in DEFAULT_SETUPS)
    default_tasks = ",".join(DEFAULT_TASKS)

    parser = argparse.ArgumentParser(
        description="Run repeated setup-variant matrix for Apr20 Colab pilot baselines."
    )
    parser.add_argument(
        "--repo-root",
        default=str(default_repo_root),
        help="Absolute path to repository root.",
    )
    parser.add_argument(
        "--dataset-relpath",
        default=pilot.DEFAULT_DATASET_REL,
        help="Path to cloudify.csv relative to --repo-root.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where outputs will be written.",
    )
    parser.add_argument(
        "--experiment-name",
        default=DEFAULT_EXPERIMENT_NAME,
        help="Name recorded in outputs for this matrix run.",
    )
    parser.add_argument(
        "--tasks",
        default=default_tasks,
        help=(
            "Comma-separated tasks/models to run. "
            f"Choices: {', '.join(TASK_CHOICES)}"
        ),
    )
    parser.add_argument(
        "--setups",
        default=default_setups,
        help="Comma-separated setup names to run.",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=DEFAULT_REPEATS,
        help="Repeats per setup (seed increments each repeat).",
    )
    parser.add_argument(
        "--base-seed",
        type=int,
        default=DEFAULT_BASE_SEED,
        help="Base seed for repeat #1. Repeat i uses seed=base_seed+(i-1).",
    )
    parser.add_argument(
        "--max-folds",
        type=int,
        default=DEFAULT_MAX_FOLDS,
        help="Cap number of online folds to run (1..5).",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=DEFAULT_PROGRESS_EVERY,
        help="Log repeat progress every N folds (0 disables fold-progress logs).",
    )
    parser.add_argument(
        "--runner-heartbeat-sec",
        type=int,
        default=DEFAULT_HEARTBEAT_SEC,
        help="Emit periodic heartbeat logs every N seconds.",
    )
    parser.add_argument(
        "--skip-dl-cibuild",
        action="store_true",
        help="Skip DL-CIBuild execution if task list includes it.",
    )
    return parser.parse_args()


def choose_tasks(raw_tasks: str) -> List[str]:
    tasks = parse_csv_list(raw_tasks)
    if not tasks:
        raise ValueError("No tasks selected. Provide at least one task.")
    invalid = sorted(task for task in tasks if task not in TASK_CHOICES)
    if invalid:
        raise ValueError(
            "Invalid task name(s): "
            f"{', '.join(invalid)}. Allowed: {', '.join(TASK_CHOICES)}"
        )
    return tasks


def choose_setups(raw_setups: str) -> List[SetupVariant]:
    setup_by_name = {setup.name: setup for setup in DEFAULT_SETUPS}
    names = parse_csv_list(raw_setups)
    if not names:
        raise ValueError("No setups selected. Provide at least one setup.")

    selected: List[SetupVariant] = []
    missing: List[str] = []
    seen = set()

    for name in names:
        if name in seen:
            continue
        seen.add(name)
        setup = setup_by_name.get(name)
        if setup is None:
            missing.append(name)
            continue
        selected.append(setup)

    if missing:
        raise ValueError(
            "Unknown setup name(s): "
            f"{', '.join(sorted(missing))}. Allowed: {', '.join(setup_by_name)}"
        )
    return selected


def maybe_trim_train_history(train_df: pd.DataFrame, train_fraction: float) -> pd.DataFrame:
    fraction = float(train_fraction)
    if fraction >= 1.0:
        return train_df
    if fraction <= 0:
        raise ValueError("train_fraction must be > 0.")
    keep = max(2, int(round(len(train_df) * fraction)))
    keep = min(keep, len(train_df))
    return train_df.iloc[:keep].copy()


def format_error_row(model_name: str, exc: Exception) -> Dict[str, Any]:
    return {
        "model": model_name,
        "status": "error",
        "reason": f"{type(exc).__name__}: {exc}",
        "auc": None,
        "f1": None,
        "accuracy": None,
        "precision": None,
        "recall": None,
        "train_time_sec": None,
    }


def run_non_dl_tasks_for_fold(
    setup: SetupVariant,
    tasks: Sequence[str],
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    seed: int,
    fold_index: int,
    logger: pilot.RunLogger,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    if "majority_class" in tasks:
        try:
            rows.append(pilot.run_majority_baseline(train_df, test_df))
        except Exception as exc:
            logger.log(
                f"majority_class failed on fold {fold_index} for setup={setup.name}: "
                f"{type(exc).__name__}: {exc}"
            )
            logger.log(traceback.format_exc())
            rows.append(format_error_row("majority_class", exc))

    if "logistic_regression" in tasks:
        try:
            rows.append(
                pilot.run_logistic_baseline(
                    train_df=train_df,
                    test_df=test_df,
                    seed=seed,
                    c=setup.logreg_c,
                    max_iter=setup.logreg_max_iter,
                    class_weight=setup.logreg_class_weight,
                    decision_threshold=setup.decision_threshold,
                )
            )
        except Exception as exc:
            logger.log(
                f"logistic_regression failed on fold {fold_index} for setup={setup.name}: "
                f"{type(exc).__name__}: {exc}"
            )
            logger.log(traceback.format_exc())
            rows.append(format_error_row("logistic_regression", exc))

    return rows


def maybe_emit_heartbeat(
    logger: pilot.RunLogger,
    heartbeat_sec: int,
    last_heartbeat_ts: float,
    context: str,
) -> float:
    if heartbeat_sec <= 0:
        return last_heartbeat_ts
    now = time.monotonic()
    if (now - last_heartbeat_ts) >= heartbeat_sec:
        logger.log(f"Heartbeat: {context}")
        return now
    return last_heartbeat_ts


def summarize_by_setup_and_model(metrics_df: pd.DataFrame) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for setup_name, setup_group in metrics_df.groupby("setup"):
        per_model: Dict[str, Any] = {}
        for model_name, model_group in setup_group.groupby("model"):
            ok_group = model_group[model_group["status"] == "ok"]
            per_model[model_name] = {
                "row_count": int(model_group.shape[0]),
                "status_counts": {
                    key: int(value)
                    for key, value in model_group["status"].value_counts().to_dict().items()
                },
                "metrics": {
                    field: pilot.summarize_series(ok_group[field])
                    for field in pilot.METRIC_COLUMNS
                },
            }
        summary[str(setup_name)] = per_model
    return summary


def build_summary(
    args: argparse.Namespace,
    setup_variants: Sequence[SetupVariant],
    selected_tasks: Sequence[str],
    dataset_path: Path,
    dataset_rows: int,
    fold_size: int,
    metrics_df: pd.DataFrame,
) -> Dict[str, Any]:
    pairwise_by_setup: Dict[str, Any] = {}
    if "majority_class" in selected_tasks and "logistic_regression" in selected_tasks:
        for setup_name, setup_group in metrics_df.groupby("setup"):
            pairwise_by_setup[str(setup_name)] = pilot.compute_pairwise_deltas(
                setup_group,
                left_model="logistic_regression",
                right_model="majority_class",
                fields=METRIC_FIELDS,
            )

    return {
        "run_metadata": {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "experiment_name": args.experiment_name,
            "script": "apr20_submission/colab/apr20_matrix_colab.py",
        },
        "global_settings": {
            "tasks": list(selected_tasks),
            "repeats_per_setup": int(args.repeats),
            "base_seed": int(args.base_seed),
            "max_folds": int(args.max_folds),
            "progress_every": int(args.progress_every),
            "runner_heartbeat_sec": int(args.runner_heartbeat_sec),
            "skip_dl_cibuild": bool(args.skip_dl_cibuild),
        },
        "setups": [asdict(setup) for setup in setup_variants],
        "dataset": {
            "path": str(dataset_path),
            "name": dataset_path.name,
            "rows": int(dataset_rows),
            "target_column": pilot.TARGET_COLUMN,
            "timestamp_column": pilot.TIMESTAMP_COLUMN,
        },
        "fold_protocol": {
            "num_folds": int(args.max_folds),
            "fold_size": int(fold_size),
            "definition": (
                "online folds from apr20 pilot: fold_size=int(n*0.1); "
                "for i in 6..10 train=0:fold_size*(i-1), "
                "test=fold_size*(i-1):fold_size*i"
            ),
        },
        "results": {
            "by_setup_and_model": summarize_by_setup_and_model(metrics_df),
            "pairwise_deltas_by_setup": pairwise_by_setup,
        },
    }


def main() -> int:
    args = parse_args()
    selected_tasks = choose_tasks(args.tasks)
    setup_variants = choose_setups(args.setups)

    if args.repeats <= 0:
        raise ValueError("--repeats must be > 0.")
    if args.max_folds <= 0:
        raise ValueError("--max-folds must be > 0.")

    logger = pilot.RunLogger()
    pilot.set_determinism(args.base_seed)

    repo_root = Path(args.repo_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.log(f"Repo root: {repo_root}")
    logger.log(f"Output dir: {output_dir}")
    logger.log(f"Experiment: {args.experiment_name}")
    logger.log(f"Selected tasks: {', '.join(selected_tasks)}")
    logger.log(f"Selected setups: {', '.join(setup.name for setup in setup_variants)}")
    logger.log(f"Repeats per setup: {args.repeats}")
    logger.log(
        "Shared speed caps: "
        f"max_folds={args.max_folds}, progress_every={args.progress_every}, "
        f"runner_heartbeat_sec={args.runner_heartbeat_sec}"
    )

    dataset_path = pilot.resolve_dataset_path(repo_root, args.dataset_relpath, logger)
    df = pilot.load_dataset(repo_root, args.dataset_relpath, logger)
    train_sets, test_sets, fold_size = pilot.online_validation_folds(df)

    if args.max_folds < len(train_sets):
        train_sets = train_sets[: args.max_folds]
        test_sets = test_sets[: args.max_folds]

    logger.log(f"Using {len(train_sets)} fold(s) with fold_size={fold_size}.")

    rows: List[Dict[str, Any]] = []
    last_heartbeat_ts = time.monotonic()

    for setup in setup_variants:
        logger.log(
            "Setup parameters | "
            f"name={setup.name}, logreg_c={setup.logreg_c}, "
            f"logreg_max_iter={setup.logreg_max_iter}, "
            f"logreg_class_weight={setup.logreg_class_weight}, "
            f"decision_threshold={setup.decision_threshold}, "
            f"train_fraction={setup.train_fraction}"
        )

        for repeat_index in range(1, args.repeats + 1):
            run_seed = int(args.base_seed + repeat_index - 1)
            pilot.set_determinism(run_seed)
            repeat_start = time.perf_counter()
            logger.log(
                f"Running setup={setup.name}, repeat={repeat_index}/{args.repeats}, seed={run_seed}"
            )

            for fold_index, (train_df, test_df) in enumerate(
                zip(train_sets, test_sets), start=1
            ):
                train_slice = maybe_trim_train_history(
                    train_df=train_df,
                    train_fraction=setup.train_fraction,
                )

                base = {
                    "experiment": args.experiment_name,
                    "setup": setup.name,
                    "repeat": repeat_index,
                    "seed": run_seed,
                    "fold": fold_index,
                    "train_rows": int(len(train_slice)),
                    "test_rows": int(len(test_df)),
                    "logreg_c": setup.logreg_c,
                    "logreg_max_iter": setup.logreg_max_iter,
                    "logreg_class_weight": setup.logreg_class_weight,
                    "decision_threshold": setup.decision_threshold,
                    "train_fraction": setup.train_fraction,
                }

                fold_rows = run_non_dl_tasks_for_fold(
                    setup=setup,
                    tasks=selected_tasks,
                    train_df=train_slice,
                    test_df=test_df,
                    seed=run_seed,
                    fold_index=fold_index,
                    logger=logger,
                )
                rows.extend({**base, **row} for row in fold_rows)

                if args.progress_every > 0 and (fold_index % args.progress_every == 0):
                    logger.log(
                        f"Progress setup={setup.name} repeat={repeat_index}: "
                        f"completed fold {fold_index}/{len(train_sets)}"
                    )

                last_heartbeat_ts = maybe_emit_heartbeat(
                    logger=logger,
                    heartbeat_sec=args.runner_heartbeat_sec,
                    last_heartbeat_ts=last_heartbeat_ts,
                    context=(
                        f"setup={setup.name}, repeat={repeat_index}/{args.repeats}, "
                        f"fold={fold_index}/{len(train_sets)}"
                    ),
                )

            if "dl_cibuild_default" in selected_tasks:
                if args.skip_dl_cibuild:
                    dl_rows = pilot.dl_not_run_rows(
                        "Skipped by --skip-dl-cibuild flag.", run_seed
                    )
                else:
                    dl_rows = pilot.run_dl_cibuild_default(
                        repo_root=repo_root,
                        seed=run_seed,
                        logger=logger,
                    )

                for row in dl_rows:
                    try:
                        fold_number = int(row.get("fold", 0) or 0)
                    except Exception:
                        fold_number = 0
                    if fold_number <= 0 or fold_number > len(train_sets):
                        continue
                    rows.append(
                        {
                            "experiment": args.experiment_name,
                            "setup": setup.name,
                            "repeat": repeat_index,
                            "seed": run_seed,
                            "logreg_c": setup.logreg_c,
                            "logreg_max_iter": setup.logreg_max_iter,
                            "logreg_class_weight": setup.logreg_class_weight,
                            "decision_threshold": setup.decision_threshold,
                            "train_fraction": setup.train_fraction,
                            **row,
                        }
                    )

            repeat_duration = time.perf_counter() - repeat_start
            logger.log(
                f"Completed setup={setup.name}, repeat={repeat_index} "
                f"in {repeat_duration:.2f}s"
            )

    metrics_df = pd.DataFrame(rows)
    for column in CSV_COLUMNS:
        if column not in metrics_df.columns:
            metrics_df[column] = None
    metrics_df = metrics_df[CSV_COLUMNS].sort_values(
        by=["setup", "repeat", "model", "fold"]
    )

    metrics_path = output_dir / "matrix_fold_metrics.csv"
    summary_path = output_dir / "matrix_summary.json"
    log_path = output_dir / "matrix_run_log.txt"

    metrics_df.to_csv(metrics_path, index=False)
    summary = build_summary(
        args=args,
        setup_variants=setup_variants,
        selected_tasks=selected_tasks,
        dataset_path=dataset_path,
        dataset_rows=len(df),
        fold_size=fold_size,
        metrics_df=metrics_df,
    )
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    logger.log(f"Wrote metrics: {metrics_path}")
    logger.log(f"Wrote summary: {summary_path}")
    logger.log("Matrix run complete.")
    logger.dump(log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
