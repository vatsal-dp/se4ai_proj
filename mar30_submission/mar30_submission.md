# March 30 (6.0) Submission Draft

**Topic:** Predictive Build Failure Analysis in CI/CD Pipelines  
**Date:** 2026-03-26

## 1. Problem Framing

Modern CI/CD pipelines generate high-volume signals (build outcomes, test results, logs, and metadata), but teams still spend significant time reacting to failures after resources are already consumed. This study maps how AI methods are currently used to detect, classify, and explain build failures in CI workflows, then identifies whether early detection from partial pipeline evidence is underexplored relative to post-failure diagnosis.

## 2. Research Questions

1. How are AI methods currently applied to CI/CD failure-related tasks (prediction, diagnosis, prioritization, optimization)?
2. Within high-impact literature, how much emphasis is placed on **post-failure explanation** versus **early/online detection**?
3. Can a practical semester project be anchored on a reproducible baseline artifact while targeting early, lower-cost detection in CI/CD settings?

## 3. Search Strategy and Data Collection

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

## 4. Knee Analysis and Reading Set

Knee method: maximum-distance bend from line connecting first and last points of the sorted top-100 citation curve.

Computed output:
- Top list size: `100`
- Knee rank: `14`
- Knee threshold: `52` citations
- Above-knee reading set size: `15`

Artifacts:
- Knee summary: `data/knee_summary.json`
- Knee figure: `figures/knee_plot.png`
- Frozen above-knee set: `data/above_knee_set.csv`

## 5. Above-Knee Classification and Overlap

For each above-knee paper, a reading matrix was prepared with:
- input artifact
- model family
- task
- prediction timing
- evaluation metric
- code/data link

Artifacts:
- Reading matrix: `data/reading_matrix.csv`
- 4-group overlap figure: `figures/overlap_figure.png`

4-group overlap groups:
- log-text inputs
- LLM/generative methods
- early/online detection
- post-failure or RCA

Current above-knee snapshot (n=15):
- Log-text group hits: `2`
- LLM/generative hits: `0`
- Early/online hits: `1`
- Post-failure/RCA hits: `1`

Interpretation: highly cited CI literature in this set is dominated by flaky tests, test prioritization, and build-failure characterization; explicit LLM-centered CI methods appear newer and not yet above the citation knee.

## 6. Candidate Gap (Unexplored Region)

The above-knee corpus is concentrated on post-hoc failure analysis, flaky-test behavior, and test-selection efficiency. A reasonable underexplored direction is **early CI failure detection from partial logs and early pipeline signals**, especially with lightweight AI models where runtime and cost are explicit optimization targets (instead of only final classification accuracy).

## 7. Reproduction Sprint and Baseline Evidence

Three candidates were smoke-tested in the requested order:
1. `KnowledgeDiscovery/rca_baselines`
2. `salesforce/PyRCA`
3. Above-knee-aligned CI repo with public code: `UT-SE-Research/iDFlakies`

Results:
- Candidate 1: host setup is blocked on Python 3.14, but full FastPC baseline reproduction succeeds in Docker (`linux/amd64`) using generated FastPC-compatible input files; the run completes and writes metric-level + combined ranking outputs.
- Candidate 2: local host install is blocked on Python 3.14, but full reproduction succeeds in Docker using Python 3.10 + OpenJDK + `numpy<2`; the official application example (`tests/applications/example/run_rca.py`) runs end-to-end and produces model artifacts plus ranked root-cause output.
- Candidate 3: fully implemented locally. The iDFlakies Maven plugin was built and executed end-to-end on a runnable Maven demo project; detection succeeded and produced `.dtfixingtools` outputs with one identified order-dependent flaky test (`demo.ODFlakeTest.polluted`).

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
- Command logs: `reproduction/logs/*`

## 8. Next-Step Experiment Direction (Post-6.0)

With 6.0 evidence in place (question + mapped literature + runnable baseline), the next step is to build an **early-warning CI detector** that predicts likely failure before full pipeline completion, then compare:
- detection lead time,
- compute/runtime cost,
- acceptable precision/recall tradeoff against post-mortem baselines.
