# March 30 Submission Artifacts

Main draft:
- `mar30_submission.md`

Core literature artifacts:
- `data/search_log.md`
- `data/papers_raw.csv`
- `data/top100_papers.csv`
- `data/above_knee_set.csv`
- `data/reading_matrix.csv`
- `data/knee_summary.json`
- `figures/knee_plot.png`
- `figures/overlap_figure.png`

Reproduction artifacts:
- `reproduction/smoke_test_matrix.md`
- `reproduction/baseline_output.md`
- `reproduction/rca_baselines_full_output.md`
- `reproduction/pyrca_baseline_output.md`
- `reproduction/idflakies_baseline_cases.csv`
- `reproduction/idflakies_baseline_summary.txt`
- `reproduction/rca_baselines_output/*` (FastPC baseline outputs)
- `reproduction/rca_synth/20211203/*` (generated FastPC-compatible inputs)
- `reproduction/scripts/generate_fastpc_synthetic_input.py`
- `reproduction/idf-demo/` (full local iDFlakies demo run project)
- `reproduction/idf-demo/.dtfixingtools/detection-results/list.txt`
- `reproduction/idf-demo/.dtfixingtools/detection-results/flaky-lists.json`
- `reproduction/work/PyRCA/pyrca/applications/example/models/*` (full PyRCA model artifacts from Docker run)
- `reproduction/work/rca_baselines/Baseline/Offline/FastPC/fastPC.py` (CPU/CUDA compatibility patch)
- `reproduction/work/rca_baselines/Baseline/Offline/FastPC/rca.py` (optional causalnex + FastPC runtime patch)
- `reproduction/work/iDFlakies/idflakies-maven-plugin/src/main/java/edu/illinois/cs/dt/tools/plugin/AbstractIDFlakiesMojo.java` (JDK-compatibility patch)
- `reproduction/logs/*`

## Regenerate literature artifacts

```bash
source mar30_submission/.venv/bin/activate
MPLCONFIGDIR=mar30_submission/.mpl python mar30_submission/scripts/generate_mar30_artifacts.py
```
