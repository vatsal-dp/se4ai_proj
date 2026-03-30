# March 30 (6.0) Submission Draft

**Topic:** Predictive Build Failure Analysis in CI/CD Pipelines  
**Date:** 2026-03-26

## 1 Introduction

Modern CI/CD systems expose teams to a large decision space: data artifacts, model choices, and deployment-time constraints all interact in ways that affect failure prediction quality and response cost. While this flexibility is useful, it creates a practical engineering problem: default settings and manual tuning do not scale when pipelines are large and fast-moving.

In this setting, delayed diagnosis is expensive. Teams often get high-quality explanations after a failure has already consumed compute and developer attention. This motivates a stronger emphasis on earlier signals and earlier intervention. In short, for CI failure handling, configurability without data-driven decision support becomes a liability.

Accordingly, this submission studies where current high-impact literature places its effort, then uses runnable baseline reproductions to anchor a feasible semester direction. The specific focus is whether **early/online failure detection** is underrepresented relative to **post-failure diagnosis/RCA**.

### Research Questions

1. How are AI methods currently applied to CI/CD failure-related tasks (prediction, diagnosis, prioritization, optimization)?
2. Within high-impact literature, how much emphasis is placed on **post-failure explanation** versus **early/online detection**?
3. Can a practical semester project be anchored on reproducible baseline artifacts while targeting earlier and lower-cost CI failure detection?

### Contributions (for 6.0)

- A citation-ranked literature mapping pipeline (375 merged papers, top-100 ranked, knee-selected above-knee set).
- A structured above-knee classification with overlap analysis that surfaces an early-detection gap.
- End-to-end baseline reproduction evidence across four tools/papers (FastPC baseline, PyRCA, iDFlakies, and DL-CIBuild).
- A concrete next-step experiment direction grounded in reproducible artifacts already generated in this repository.

### Roadmap

Section 2 summarizes the literature mapping process and states the gap in Section 2.3; Section 3 presents baseline reproduction evidence; Section 4 outlines the post-6.0 experimental direction.

## 2 Literature Mapping and Gap Analysis

### 2.1 Search Strategy and Data Collection

Citation metadata source: **OpenAlex API (live query run on 2026-03-26)**.

Exact query strings:
- `continuous integration build failure`
- `travis ci build failure`
- `continuous integration flaky tests`
- `ci/cd log analysis software`
- `continuous integration regression test selection`

Applied constraints:
- Year filter: 2015+
- CS filter: `concepts.id:C41008148`
- Retrieval scope: `title_and_abstract.search:<query>`

Artifacts:
- Search log: `data/search_log.md`
- Raw merged rows: `data/papers_raw.csv`
- De-duplicated top 100: `data/top100_papers.csv`

### 2.2 Citation Ranking, Knee Analysis, and Reading Set

To prioritize the most influential papers while keeping the review tractable, papers were ranked by citation count and a knee heuristic was used on the top-100 curve (maximum-distance bend from the line connecting first and last points).

Computed output:
- Top list size: `100`
- Knee rank: `14`
- Knee threshold: `52` citations
- Above-knee reading set size: `15`

Artifacts:
- Knee summary: `data/knee_summary.json`
- Knee figure: `figures/knee_plot.png`
- Frozen above-knee set: `data/above_knee_set.csv`

### 2.3 A Gap in the Literature

For each above-knee paper, a reading matrix was prepared with:
- input artifact
- model family
- task
- prediction timing
- evaluation metric
- code/data link
- detailed reading note (paper-specific)
- reading depth marker
- abstract evidence excerpt

Artifacts:
- Reading matrix: `data/reading_matrix.csv`
- Detailed per-paper notes: `data/above_knee_detailed_notes.md`
- 4-group literal Venn diagram + exact overlap counts: `figures/overlap_figure.png`

Note: if metadata did not include an abstract for a paper, the matrix and notes mark the excerpt as "Not available in retrieved metadata."

Grouping dimensions used for overlap analysis:
- log-text inputs
- LLM/generative methods
- early/online detection
- post-failure or RCA

Current above-knee snapshot (n=15):
- Log-text group hits: `5`
- LLM/generative hits: `0`
- Early/online hits: `7`
- Post-failure/RCA hits: `8`

This overlap pattern indicates that high-impact CI-related work is still weighted toward post-hoc diagnosis and test optimization, with no LLM-centered entries in the above-knee set. The central unexplored region for this project is therefore **early CI failure detection from partial and inexpensive signals**, where lead-time and runtime cost are first-class constraints.

## 3 Reproduction Sprint and Baseline Evidence

Three candidates were smoke-tested in the requested order:
1. `KnowledgeDiscovery/rca_baselines`
2. `salesforce/PyRCA`
3. Above-knee-aligned CI repo with public code: `UT-SE-Research/iDFlakies`

Additional implemented above-knee paper:
4. Rank 12: `stilab-ets/DL-CIBuild` (paper: *Improving the prediction of continuous integration build failures using deep learning*)

Results:
- Candidate 1: host setup is blocked on Python 3.14, but full FastPC baseline reproduction succeeds in Docker (`linux/amd64`) using generated FastPC-compatible input files; the run completes and writes metric-level + combined ranking outputs.
- Candidate 2: local host install is blocked on Python 3.14, but full reproduction succeeds in Docker using Python 3.10 + OpenJDK + `numpy<2`; the official application example (`tests/applications/example/run_rca.py`) runs end-to-end and produces model artifacts plus ranked root-cause output.
- Candidate 3: fully implemented locally. The iDFlakies Maven plugin was built and executed end-to-end on a runnable Maven demo project; detection succeeded and produced `.dtfixingtools` outputs with one identified order-dependent flaky test (`demo.ODFlakeTest.polluted`).
- Candidate 4: DL-CIBuild was executed in Docker (`tensorflow/tensorflow:2.16.1`) on `cloudify.csv` (online fold 0) using repo default LSTM settings, producing a saved baseline output (`test AUC=0.8843`, `accuracy=0.8885`, `F1=0.8694`).

Artifacts:
- Smoke matrix: `reproduction/smoke_test_matrix.md`
- Baseline run evidence: `reproduction/baseline_output.md`
- rca_baselines full run evidence: `reproduction/rca_baselines_full_output.md`
- PyRCA full run evidence: `reproduction/pyrca_baseline_output.md`
- Baseline summary table: `reproduction/idflakies_baseline_cases.csv`
- Baseline summary stats: `reproduction/idflakies_baseline_summary.txt`
- rca_baselines full run log: `reproduction/logs/rca_baselines_full_run.txt`
- rca_baselines output artifacts: `reproduction/rca_baselines_output/*`
- FastPC synthetic input generator: `reproduction/scripts/generate_fastpc_synthetic_input.py`
- PyRCA full run log: `reproduction/logs/pyrca_full_run.txt`
- PyRCA generated model artifacts: `reproduction/work/PyRCA/pyrca/applications/example/models/*`
- Full run log (plugin build): `reproduction/logs/idflakies_plugin_build.txt`
- Full run log (detector): `reproduction/logs/idflakies_detect_demo.txt`
- Full run detector output list: `reproduction/idf-demo/.dtfixingtools/detection-results/list.txt`
- Full run detector JSON: `reproduction/idf-demo/.dtfixingtools/detection-results/flaky-lists.json`
- DL-CIBuild run notes: `reproduction/dl_cibuild_rank12_run.md`
- DL-CIBuild baseline output JSON: `reproduction/dl_cibuild_rank12_output.json`
- DL-CIBuild rerun script: `reproduction/scripts/run_dl_cibuild_rank12.sh`
- Command logs: `reproduction/logs/*`

## 4 Next-Step Experiment Direction (Post-6.0)

With 6.0 evidence in place (question + mapped literature + runnable baseline), the next step is to build an **early-warning CI detector** that predicts likely failure before full pipeline completion, then compare:
- detection lead time,
- compute/runtime cost,
- acceptable precision/recall tradeoff against post-mortem baselines.
