# Early CI Build Failure Warning with Reproducible Matrix Evaluation (Apr 20 Submission)

## Abstract

This submission defines and executes a reproducible study for early warning of CI build failures using chronologically ordered folds from `cloudify.csv`. Building on the Mar 30 milestone (citation-guided gap analysis + baseline reproductions), this Apr 20 paper contributes a fully specified methods pipeline and completed pilot matrix outputs. The matrix run evaluates three models (`majority_class`, `logistic_regression`, `dl_cibuild_default`) across two setups (`baseline`, `long_history`) on five online folds, with repeated seeds for stability. Across 280 successful fold-level runs, DL-CIBuild is consistently strongest on AUC and F1 (mean AUC `0.725`, mean F1 `0.509`), while simple baselines expose class-imbalance behavior and decision-threshold tradeoffs. The full run log, per-fold metrics, and aggregate summary are archived for traceability.

## 1. Introduction

### 1.1 Goal

The goal is to evaluate an evidence-based path toward **early CI failure warning** using low-cost pre/post-commit signals, instead of relying only on post-failure diagnosis after full pipeline execution.

This goal is motivated by two prior project outcomes:

1. A curated high-impact literature map (Mar 30) showing substantial post-failure/RCA emphasis.
2. Runnable reproductions of prior systems (FastPC baseline, PyRCA, iDFlakies, DL-CIBuild), confirming feasibility of baseline-first experimentation.

### 1.2 Research Questions

RQ1. How are AI methods distributed across early/online detection versus post-failure diagnosis in the project’s high-impact CI/failure literature slice?

RQ2. Can a reproducible online-fold protocol on CI build data distinguish stronger early-warning models from simple baselines?

RQ3. Under practical runtime constraints, what metric tradeoffs (AUC/F1/accuracy/precision/recall) appear across baseline and deep models?

### 1.3 Contributions

1. A complete Apr 20 methods protocol with explicit variables, dataset origin, split logic, run settings, and analysis steps.
2. A finished repeated matrix run (not placeholder-only) with archived artifacts:
   - `apr20_submission/artifacts/matrix_fold_metrics.csv`
   - `apr20_submission/artifacts/matrix_summary.json`
   - `apr20_submission/artifacts/matrix_run_log.txt`
3. Quantitative comparison across 280 fold-level evaluations showing strong DL-CIBuild gains in ranking/early-detection quality metrics over simple baselines.
4. A transparent discussion of practical implications and threats (imbalance, temporal shift, setup sensitivity, and summary-pipeline caveats).

## 2. Background

### 2.1 Motivation and Problem Validity

CI failures are frequent and expensive interruptions. If failure risk can be flagged earlier, teams can avoid wasted compute and reduce developer waiting time. In this project’s curated above-knee literature set, post-failure/RCA remains a strong emphasis, so early warning remains a valid and actionable study target for this semester scope.

### 2.2 Related Work (Project-Specific)

The Mar 30 evidence pipeline produced a 375-paper corpus (2015+), top-100 citation shortlist, knee-based prioritization (knee rank 14, threshold 52 citations), and an above-knee set of 15 papers. That set was coded across:

- log-text inputs,
- LLM/generative methods,
- early/online detection,
- post-failure/RCA.

Observed counts from archived artifacts:

- early/online: 7,
- post-failure/RCA: 8,
- log-text: 5,
- LLM/generative: 0.

This motivates an empirical focus on early warning with reproducible baselines rather than purely post-hoc diagnosis.

### 2.3 Origin of Data and Participants

This work is artifact-based (no human-subject recruitment).

1. Data source:
   - `mar30_submission/reproduction/work/DL-CIBuild/dataset/cloudify.csv`
2. Target variable:
   - `build_Failed` (binary)
3. Temporal ordering field:
   - `gh_build_started_at`
4. Record count:
   - 5,742 rows

Participants in this milestone are software artifacts, scripts, and repository-derived records.

## 3. Methods

### 3.1 Variables and Measures

#### Outcome Variable

- `build_Failed` (binary CI failure label).

#### Predictor Variables

Predictors include PR/build context, churn, file-type deltas, and project/test-density attributes, including:
`gh_is_pr`, `git_prev_commit_resolution_status`, `gh_team_size`, `gh_num_commit_comments`, `git_diff_src_churn`, `git_diff_test_churn`, `gh_diff_files_added`, `gh_diff_files_deleted`, `gh_diff_files_modified`, `gh_diff_tests_added`, `gh_diff_tests_deleted`, `gh_diff_src_files`, `gh_diff_doc_files`, `gh_diff_other_files`, `gh_sloc`, `gh_test_lines_per_kloc`, `gh_test_cases_per_kloc`, `gh_asserts_cases_per_kloc`.

#### Evaluation Metrics

Primary metrics:

- AUC
- F1
- Accuracy
- Precision
- Recall

Operational metric:

- `train_time_sec` (per-fold runtime cost)

### 3.2 Selection Strategy

#### Why this dataset

`cloudify.csv` is selected because it is directly tied to a reproduced baseline package (DL-CIBuild), supports chronological online folds, and is already versioned with runnable scripts in this repository.

#### Why these models

- `majority_class` for calibration and class-imbalance baseline,
- `logistic_regression` as an interpretable low-cost baseline,
- `dl_cibuild_default` as the reproduced deep baseline from prior work.

#### Why these parameters

Two setups were evaluated:

- `baseline`: `logreg_max_iter=1000`, `class_weight=none`, threshold `0.5`
- `long_history`: `logreg_max_iter=2000`, `class_weight=balanced`, threshold `0.5`

DL-CIBuild used default tuner (`dl_tuner=default`) to preserve reproducibility before broad hyperparameter search.

### 3.3 Methodology (Replicable Protocol)

1. Load `cloudify.csv` and sort by `gh_build_started_at`.
2. Build online folds (`i=6..10`) with fold size `574`, yielding 5 chronological train/test splits.
3. Evaluate all selected models on aligned folds:
   - classic baselines: `8` repeats/setup (`seeds 42..49`)
   - DL-CIBuild: `12` repeats/setup (`seeds 100..111`)
4. Record fold-level outputs and runtime in CSV.
5. Aggregate summary statistics in JSON.
6. Emit traceable text log with run lifecycle and output paths.

Execution metadata from log:

- Start: `2026-04-20T01:18:15+00:00`
- End: `2026-04-20T04:49:35+00:00`
- Total wall time: `3:31:20`
- Status: all runs completed successfully.

### 3.4 Data Analysis and Appropriateness

Data analysis converts fold-level outputs into:

- descriptive summaries (mean, std, median, IQR),
- model comparisons under identical temporal folds,
- practical runtime interpretation.

This is appropriate because:

- folds are chronological and shared across models,
- repeated seeds reduce single-run noise,
- CI settings require quality and latency tradeoff interpretation, not metric-only reporting.

## 4. Matrix Output Analysis (Apr 20)

### 4.1 Artifact Integrity Checks

- Total fold-level rows in CSV: `280`
- Status counts: `ok=280`, no failures or missing rows
- Models per setup:
  - DL rows: `60`
  - Logistic rows: `40`
  - Majority rows: `40`

### 4.2 Aggregate Performance by Setup and Model

| Setup | Model | Row count | AUC mean | F1 mean | Accuracy mean | Precision mean | Recall mean | Mean train time (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | majority_class | 40 | 0.500 | 0.000 | 0.803 | 0.000 | 0.000 | 0.001 |
| baseline | logistic_regression | 40 | 0.499 | 0.146 | 0.669 | 0.211 | 0.221 | 0.260 |
| baseline | dl_cibuild_default | 60 | 0.725 | 0.509 | 0.815 | 0.459 | 0.599 | 98.811 |
| long_history | majority_class | 40 | 0.500 | 0.000 | 0.803 | 0.000 | 0.000 | 0.001 |
| long_history | logistic_regression | 40 | 0.498 | 0.206 | 0.564 | 0.307 | 0.415 | 0.277 |
| long_history | dl_cibuild_default | 60 | 0.725 | 0.509 | 0.815 | 0.459 | 0.599 | 100.088 |

Key observations:

1. **DL-CIBuild is the strongest model on AUC and F1** in both setups.
2. Majority baseline gets high accuracy due class imbalance, but has zero precision/recall/F1 for failures.
3. Long-history logistic settings increase recall and F1, but sharply reduce accuracy (more false positives), showing threshold/class-weight tradeoffs.
4. DL predictive means are numerically identical across setups (expected, since setup changes only logistic parameters).

### 4.3 Temporal Fold Behavior

DL fold means (averaged across repeats) show a clear degradation from early to later folds:

| Fold | Mean AUC | Mean F1 | Mean Accuracy | Implied failure rate in test fold (from majority baseline) |
|---:|---:|---:|---:|---:|
| 1 | 0.885 | 0.870 | 0.888 | 0.436 |
| 2 | 0.706 | 0.483 | 0.829 | 0.150 |
| 3 | 0.720 | 0.507 | 0.801 | 0.171 |
| 4 | 0.697 | 0.405 | 0.790 | 0.124 |
| 5 | 0.618 | 0.280 | 0.769 | 0.105 |

Interpretation: as positive prevalence drops across later chronological folds, failure detection becomes harder, and F1 declines substantially. This validates the need for threshold calibration and imbalance-aware analysis in the next phase.

### 4.4 Runtime and Practicality

Total train time by setup/model (sum of fold-level `train_time_sec`):

- baseline DL: `5928.667s` (~98.8 min)
- long_history DL: `6005.282s` (~100.1 min)
- baseline logistic: `10.395s`
- long_history logistic: `11.094s`
- majority baselines: ~`0.02s` each setup

Practical implication:

- DL provides large quality gains but dominates compute cost.
- Logistic/majority are extremely cheap and useful for sanity checks, but insufficient for reliable early warning quality.

### 4.5 Data-Quality Note on Summary Deltas

`matrix_summary.json` includes `pairwise_deltas_by_setup` with `folds_compared=320` for logistic-vs-majority because repeat combinations are cross-paired, not one-to-one repeat-matched. To avoid ambiguity, this submission relies primarily on the raw fold metrics CSV for fold-mean and trend interpretation.

## 5. Discussion and Apr 20 Scope Fit

This submission satisfies the Apr 20 (6a) expectations:

- **Introduction**: clear goal, research questions, contributions.
- **Background**: motivation, related work framing, and origin of data.
- **Methods**: variables, selection strategy, replicable methodology, analysis definition and appropriateness.

The added matrix outputs strengthen the methods section with concrete empirical evidence while remaining conservative about claims. The Apr 27 extension can build directly on these artifacts for full Results/Discussion/Conclusion with broader validity analysis and, if needed, additional threshold tuning and effect-size reporting.

## Artifact Pointers

- `apr20_submission/artifacts/matrix_fold_metrics.csv`
- `apr20_submission/artifacts/matrix_summary.json`
- `apr20_submission/artifacts/matrix_run_log.txt`
- `apr20_submission/artifacts/pilot_fold_metrics.csv` (alias copy)
- `apr20_submission/artifacts/pilot_summary.json` (alias copy)
- `apr20_submission/artifacts/colab_run_log.txt` (alias copy)
