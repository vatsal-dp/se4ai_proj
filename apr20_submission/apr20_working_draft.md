# Apr 20 (6a) Working Draft (Content-Only)

## 1. Introduction

### 1.1 Goal

The goal of this project is to define and test an evidence-based path toward **early warning of CI build failures** using low-cost, pre/post-commit signals, instead of relying only on post-failure diagnosis after pipeline resources and developer time are already consumed.

This goal is grounded in two completed project stages from the March 30 milestone: (1) a citation-guided map of influential CI/failure-related literature and (2) runnable reproductions of representative baselines. The April 20 milestone focuses on turning that foundation into a methodologically explicit study design that is ready for reproducible pilot execution in Google Colab.

### 1.2 Research Questions

RQ1. How are AI methods currently applied to CI/CD failure-related tasks (prediction, diagnosis, prioritization, optimization) in the high-impact literature collected for this project?

RQ2. Within the above-knee literature set, how is emphasis distributed between early/online detection and post-failure diagnosis/root-cause analysis?

RQ3. Can a practical semester project be evaluated using reproducible baselines while targeting earlier and lower-cost CI failure warning?

### 1.3 List of Contributions

1. A reproducible literature evidence base with archived artifacts: 375 raw rows, top-100 ranked set, knee selection, and above-knee detailed matrix.
2. A gap statement supported by structured overlap coding, showing that post-failure/RCA remains a major center of emphasis while early intervention opportunities remain underexplored for this project context.
3. Reproduction evidence across four baseline implementations (FastPC baseline from `rca_baselines`, PyRCA, iDFlakies, and DL-CIBuild), demonstrating that the project stands on runnable prior work.
4. A fully specified Apr 20 methods protocol with explicit variables, selection strategy, replicable steps, and analysis plan, including clear insertion points for pending multi-fold pilot outputs from Colab.

## 2. Background

### 2.1 Motivation and Validity of the Problem

CI build failures are frequent, expensive interruptions in modern software delivery. Teams often detect and diagnose failures only after full pipeline execution, which increases developer wait time and compute waste. In this repository's March 30 review artifacts, influential papers include substantial work on failure diagnosis, flaky-test analysis, and build troubleshooting, but comparatively less emphasis on a direct early-warning framing where lead time and runtime cost are first-class objectives.

The validity of this problem is supported by:

- Literature evidence showing many high-impact studies that characterize failures and diagnose causes after failure events.
- Reproduction evidence showing practical tools and baselines are available and executable, enabling concrete comparative work rather than speculative claims.
- Course project guidance that explicitly asks students to identify an underexplored region and build from reproducible prior systems.

This makes the proposed problem both academically grounded and practically relevant: if early warning can achieve acceptable predictive quality at lower cost, teams can intervene sooner and reduce downstream disruption.

### 2.2 Related Work (Project-Specific Mapping)

The March 30 literature pipeline used OpenAlex metadata queries (2015+) with five CI/failure-focused search strings. The archived outputs are:

- `mar30_submission/data/papers_raw.csv` (375 rows),
- `mar30_submission/data/top100_papers.csv` (citation-ranked shortlist),
- `mar30_submission/data/knee_summary.json` (knee rank 14, threshold 52 citations, above-knee size 15),
- `mar30_submission/data/above_knee_set.csv`,
- `mar30_submission/data/reading_matrix.csv`,
- `mar30_submission/figures/knee_plot.png`,
- `mar30_submission/figures/overlap_figure.png`.

Within the above-knee set (`n=15`), the coded grouping dimensions were:

- log-text inputs,
- LLM/generative methods,
- early/online detection,
- post-failure/RCA.

From the March artifacts and draft:

- early/online: 7 papers,
- post-failure/RCA: 8 papers,
- log-text: 5 papers,
- LLM/generative: 0 papers.

The overlap figure indicates a sparse center overlap and a strong presence of post-failure-oriented work. This supports the project decision to focus on **early CI failure warning** as the next experimental region, while keeping claims conservative: this is a gap in this project's curated high-impact slice, not a claim that no such work exists globally.

### 2.3 Origin of Data and Participants

This study currently uses **artifact-based data**, not human-subject participant recruitment.

1. Literature corpus origin:
   - OpenAlex API queries recorded in `mar30_submission/data/search_log.md`.
   - Query counts and timestamp archived in `mar30_submission/data/knee_summary.json`.

2. Empirical build-failure data origin:
   - DL-CIBuild repository copy under `mar30_submission/reproduction/work/DL-CIBuild/`.
   - Dataset for pilot modeling: `mar30_submission/reproduction/work/DL-CIBuild/dataset/cloudify.csv`.
   - Data is sorted by `gh_build_started_at` in the upstream utility function before fold construction.

3. Baseline reproduction origins:
   - FastPC baseline (`rca_baselines`) with synthetic input generation for compatibility (`mar30_submission/reproduction/rca_synth/20211203/*`).
   - PyRCA example pipeline artifacts.
   - iDFlakies detector outputs from a runnable Maven demo project.
   - DL-CIBuild fold-0 baseline output in `mar30_submission/reproduction/dl_cibuild_rank12_output.json`.

No direct end-user participants are enrolled in this milestone. The term "participants" in this context refers to software artifacts and repository-derived records used for analysis.

## 3. Methods

### 3.1 Variables (Definitions of Metrics and Measures)

#### 3.1.1 Outcome Variable

- `build_Failed` (binary target from `cloudify.csv`), representing whether a CI build failed.

#### 3.1.2 Predictor Variables

From the current dataset header (as archived in repo), predictors include:

- Pull-request/context indicators: `gh_is_pr`, `git_prev_commit_resolution_status`, `gh_team_size`, `gh_num_commit_comments`.
- Change/churn features: `git_diff_src_churn`, `git_diff_test_churn`, `gh_diff_files_added`, `gh_diff_files_deleted`, `gh_diff_files_modified`.
- Test and artifact-change features: `gh_diff_tests_added`, `gh_diff_tests_deleted`, `gh_diff_src_files`, `gh_diff_doc_files`, `gh_diff_other_files`.
- Size/test-density features: `gh_sloc`, `gh_test_lines_per_kloc`, `gh_test_cases_per_kloc`, `gh_asserts_cases_per_kloc`.
- Metadata fields used for split/traceability: `tr_build_id`, `gh_build_started_at`.

#### 3.1.3 Evaluation Measures

Primary predictive measures:

- AUC,
- F1,
- accuracy,
- precision,
- recall.

Operational measure:

- runtime per fold (seconds), to reflect practicality/cost.

For context, the existing reproduced DL-CIBuild fold-0 baseline reports:

- test AUC = 0.8843,
- test accuracy = 0.8885,
- test F1 = 0.8694,

as stored in `mar30_submission/reproduction/dl_cibuild_rank12_output.json`. These values are prior evidence and not yet the full Apr 20 multi-fold result.

### 3.2 Selection Strategy

#### 3.2.1 Why this dataset

`cloudify.csv` is selected because:

- it is tied to a reproduced, above-knee-related baseline (DL-CIBuild, rank 12 in the project's top-100 list),
- it supports chronologically ordered online validation in the upstream codebase,
- it is already present in the repository with runnable scripts and documented baseline output.

This choice prioritizes reproducibility and comparability over expanding to multiple datasets before the protocol is stabilized.

#### 3.2.2 Why these models/baselines

The pilot compares:

- DL-CIBuild default model path (existing reproduced baseline),
- simple predictive baselines (majority and logistic regression) for sanity-check and calibration.

This follows a baseline-first strategy from lecture guidance: if a complex model does not outperform simple baselines under comparable conditions, claims should be revised.

#### 3.2.3 Why these parameters ("magic parameters")

For the DL-CIBuild pilot path, default tuner settings are retained initially (e.g., `nb_units=64`, `nb_layers=3`, `time_step=30`, `nb_epochs=10`, `nb_batch=64`, `drop_proba=0.1` from the archived fold-0 run output). The rationale is to avoid premature hyperparameter search before a stable reproducible baseline protocol is complete.

### 3.3 Methodology (Replicable Steps)

This subsection defines the exact Apr 20 execution flow. The experiment itself is planned to run in Google Colab, not in local host execution for this milestone report.

1. Environment setup:
   - Open Colab notebook and install required Python packages (`tensorflow`, `pandas`, `numpy`, `scikit-learn`, `scipy`).
   - Load repository contents (Drive mount + clone/upload).

2. Data loading:
   - Load `cloudify.csv`.
   - Parse and sort by `gh_build_started_at` (matching upstream utility behavior).

3. Fold creation:
   - Use online validation folds from the repository logic (`for i in range(6,11)`), producing 5 train/test pairs.
   - Each fold trains on earlier builds and tests on the next chronological block.

4. Model execution:
   - Run DL-CIBuild default configuration per fold.
   - Run majority and logistic-regression baselines per fold on aligned splits.

5. Metric capture:
   - Save fold-level metrics to `artifacts/pilot_fold_metrics.csv`.
   - Save aggregate summaries and pairwise deltas to `artifacts/pilot_summary.json`.

6. Traceability:
   - Save a plain-text run log (`artifacts/colab_run_log.txt`) with package versions and command history.

7. Manuscript integration:
   - Insert resulting tables/values into placeholders listed in Section 3.4.3.

Planned output schema (pending Colab run):

- `pilot_fold_metrics.csv`: `model,fold,train_rows,test_rows,auc,f1,accuracy,precision,recall,train_time_sec`
- `pilot_summary.json`: per-model aggregate stats + model-to-model deltas.

### 3.4 Data Analysis (Definition and Appropriateness)

#### 3.4.1 Definition

Data analysis in this study means converting fold-level predictive outputs into:

- descriptive summaries (mean/std, median/IQR),
- comparative summaries between models (paired fold deltas),
- practical interpretation with both quality and runtime signals.

#### 3.4.2 Why these techniques are appropriate

- **Fold-wise paired comparison** is appropriate because all models are evaluated on the same temporal splits.
- **Non-parametric or effect-size-oriented interpretation** is appropriate because the fold count is small and distribution assumptions are weak.
- **Baseline comparison first** is appropriate because it prevents overclaiming improvements from model complexity alone.
- **Operational metrics (runtime) alongside predictive metrics** are appropriate for CI settings where fast intervention matters.

Planned statistical reporting (pending Colab outputs):

- paired Wilcoxon-style significance check where applicable,
- effect size (e.g., A12/Cliff-style interpretation),
- explicit note when effect is small or practically negligible.

These choices align with course lecture guidance on empirical rigor and avoiding p-value-only conclusions.

#### 3.4.3 Planned Artifact Insertion Points (Pending Colab Run)

- **[PLACEHOLDER A]** Table: per-fold metrics for each model from `pilot_fold_metrics.csv`.
- **[PLACEHOLDER B]** Table: aggregate metrics and runtime summary from `pilot_summary.json`.
- **[PLACEHOLDER C]** Short paragraph: paired model comparison with effect-size interpretation.

Until these artifacts are generated in Colab, no new performance claim beyond the already archived fold-0 DL-CIBuild baseline is asserted.

## 4. Lecture Concepts Applied

This project currently applies four lecture concepts directly:

1. **Baseline-first rigor**  
   The method requires simple predictive baselines (majority/logistic) before claiming gains from deeper models.

2. **Reproducibility discipline**  
   Every major stage is artifacted (search logs, curated matrices, reproduction logs, and planned Colab output contracts).

3. **Statistics/effect-size mindset**  
   Planned analysis uses fold-wise paired comparison with effect-size interpretation, not single-run headline numbers.

4. **Threats to validity framing**  
   Internal (config bias), external (single dataset scope), construct (predictive metrics vs practical utility), and conclusion (small-sample inference) threats are explicitly tracked.

## 5. Current Status and Scope Boundary

Completed as of this draft:

- Citation-guided corpus construction and knee-based prioritization.
- Above-knee classification and overlap analysis artifacts.
- Reproduction evidence for FastPC baseline, PyRCA, iDFlakies, and DL-CIBuild fold-0.
- Apr 20 methods protocol and placeholder map for Colab pilot insertion.

Not yet completed in this draft:

- Multi-fold Colab pilot execution outputs (`pilot_fold_metrics.csv`, `pilot_summary.json`, statistical delta tables).
- Apr 27 sections (Results, Discussion, Conclusion expansion, full validity write-up).
- LaTeX submission formatting (explicitly out of scope for current request).
