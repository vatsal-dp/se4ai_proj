# Reproduction Smoke-Test Matrix

Run date: 2026-03-26
Environment snapshot: `reproduction/environment.txt`

| Order | Candidate | Repo | Smoke Command(s) | Status | Evidence |
|---|---|---|---|---|---|
| 1 | LEMMA-RCA baselines | https://github.com/KnowledgeDiscovery/rca_baselines | 1) Host smoke: `python test_FastPC_pod_metric.py -h` 2) Full Docker run (amd64) of `test_FastPC_pod_metric.py` with generated FastPC-compatible input files | Pass (Docker) | Host path fails on Python 3.14 (`logs/rca_baselines_smoke.txt`, `logs/rca_baselines_install3.txt`), but full amd64 Docker reproduction succeeds with output artifacts (`logs/rca_baselines_full_run.txt`, `rca_baselines_output/*`) |
| 2 | PyRCA | https://github.com/salesforce/PyRCA | 1) Local host attempt: `pip install -e .` 2) Full Docker run: install OpenJDK + `numpy<2`, then execute `python tests/applications/example/run_rca.py` in `python:3.10-slim` | Pass (Docker) | Host install fails on Python 3.14 (`logs/pyrca_install.txt`), but full Docker reproduction succeeds with model artifacts + RCA output (`logs/pyrca_full_run.txt`, `work/PyRCA/pyrca/applications/example/models/*`) |
| 3 | iDFlakies | https://github.com/UT-SE-Research/iDFlakies | 1) Build plugin locally: `mvn ... -pl idflakies-maven-plugin -am -DskipTests install` 2) Run detector goal: `mvn ... idflakies-maven-plugin:2.0.1-SNAPSHOT:detect ...` on `reproduction/idf-demo` | Pass | Full local run succeeded with detected OD flaky test `demo.ODFlakeTest.polluted`. Logs: `logs/idflakies_plugin_build.txt`, `logs/idflakies_detect_demo.txt`; artifacts: `idf-demo/.dtfixingtools/detection-results/list.txt`, `idf-demo/.dtfixingtools/detection-results/flaky-lists.json` |

## Notes

- Candidate 1 is reproducible in an amd64 Docker runtime (needed for bundled x86 `libspot.so` and dependency isolation).
- Candidate 2 is reproducible when pinned to a compatible runtime (Python 3.10 + Java + `numpy<2`) in Docker.
- Candidate 3 was first validated with included minimized artifacts, then executed end-to-end locally with the detector plugin on a runnable Maven project.
