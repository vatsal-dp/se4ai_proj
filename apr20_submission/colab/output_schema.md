# Output Schema and Acceptance Checks

This document defines the output contract for:
- `pilot_fold_metrics.csv`
- `pilot_summary.json`
- `colab_run_log.txt`

## 1) `pilot_fold_metrics.csv`

One row per `(model, fold)`.

### Required columns

| Column | Type | Description |
|---|---|---|
| `model` | string | Model identifier: `majority_class`, `logistic_regression`, or `dl_cibuild_default`. |
| `fold` | int | Fold index in `[1,2,3,4,5]`, corresponding to repository online folds for `i=6..10`. |
| `train_rows` | int or null | Number of training rows in that fold. |
| `test_rows` | int or null | Number of test rows in that fold. |
| `status` | string | `ok`, `not_run`, or `error`. |
| `reason` | string | Empty for successful rows; explanatory text for `not_run`/`error`. |
| `auc` | float or null | ROC-AUC score. Null when unavailable (for example single-class test labels). |
| `f1` | float or null | F1 score. |
| `accuracy` | float or null | Accuracy score. |
| `precision` | float or null | Precision score. |
| `recall` | float or null | Recall score. |
| `train_time_sec` | float or null | Training time in seconds for the fold. |
| `seed` | int | Random seed used by baselines. |

### Acceptance checks

1. File exists and is readable as CSV.
2. Column set matches the required schema above.
3. Baseline coverage:
   - `majority_class` has exactly 5 rows (folds 1..5).
   - `logistic_regression` has exactly 5 rows (folds 1..5).
4. DL-CIBuild coverage:
   - `dl_cibuild_default` has exactly 5 rows (folds 1..5), with `status` either `ok`, `not_run`, or `error`.
5. For rows with `status == "ok"`:
   - `train_rows > 0`, `test_rows > 0`, `train_time_sec >= 0`.
   - Metric values in `[0, 1]` for `auc`, `f1`, `accuracy`, `precision`, `recall` when non-null.
6. For rows with `status in {"not_run","error"}`:
   - `reason` must be non-empty.

## 2) `pilot_summary.json`

Aggregate artifact with run metadata, fold protocol, per-model metric summaries, and pairwise deltas.

### Required top-level keys

- `run_metadata`
- `dataset`
- `fold_protocol`
- `models`
- `pairwise_deltas`

### Required structure

- `run_metadata` includes:
  - `created_at_utc`
  - `seed`
  - `skip_dl_cibuild`
  - `script`

- `dataset` includes:
  - `name` (`cloudify.csv`)
  - `rows`
  - `target_column` (`build_Failed`)
  - `timestamp_column` (`gh_build_started_at`)

- `fold_protocol` includes:
  - `num_folds` (expected 5)
  - `fold_size` (computed as `int(n*0.1)`)
  - `definition` (human-readable split logic)

- `models` is an object keyed by model name. For each model:
  - `row_count`
  - `status_counts`
  - `metrics`:
    - `auc`, `f1`, `accuracy`, `precision`, `recall`, `train_time_sec`
    - each metric has `count`, `mean`, `std`, `median`, `iqr`, `min`, `max`

- `pairwise_deltas.logistic_minus_majority` includes:
  - `left_model`
  - `right_model`
  - `folds_compared`
  - `metrics` with `mean_delta` and `median_delta` for:
    - `auc`, `f1`, `accuracy`, `precision`, `recall`

### Acceptance checks

1. JSON parses successfully.
2. All required keys and nested fields exist.
3. `fold_protocol.num_folds == 5`.
4. `models` contains keys for the three model IDs.
5. `status_counts` totals match each model’s `row_count`.

## 3) `colab_run_log.txt`

Text log with timestamped execution events.

### Required content

- Start configuration entries:
  - repo root
  - output dir
  - seed
  - DL-CIBuild mode (`skip` or attempted)
- Dataset load event
- Fold generation event
- Output write events for CSV and JSON
- Completion message

### Acceptance checks

1. File exists and is non-empty.
2. Contains at least one timestamped line with UTC offset.
3. Contains explicit output file write lines.
4. If DL-CIBuild is not run, log includes a reason (missing dependency or skip flag).
