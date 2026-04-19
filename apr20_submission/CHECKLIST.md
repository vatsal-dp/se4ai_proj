# Apr 20 (6a) Rubric Coverage Checklist

Use this checklist to verify that the Apr 20 draft covers every required rubric item with concrete section headings and evidence files.

## Terminology and Naming Consistency

- Use `early/online detection` for pre-failure warning tasks.
- Use `post-failure/RCA` for diagnosis after a failure occurs.
- Refer to the pilot protocol as `cloudify 5 folds` (online splits `i=6..10`).
- Keep Apr 20 artifact filenames exactly:
  - `pilot_fold_metrics.csv`
  - `pilot_summary.json`
  - `colab_run_log.txt`

## Rubric-to-Section Mapping

| Rubric requirement | Required section heading in draft | Primary file | Supporting evidence files |
|---|---|---|---|
| Introduction: clear goal | `## 1 Introduction` + `### Goal` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/mar30_submission/mar30_submission.md` |
| Research questions/objectives | `### Research Questions` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/mar30_submission/submission_mar30_paper.md` |
| List of contributions | `### Contributions` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/mar30_submission/submission_mar30_paper.md` |
| Background: motivation and validity | `## 2 Background` + `### Motivation and Problem Validity` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/mar30_submission/data/knee_summary.json` |
| Related work + origin of data/participants | `### Related Work` + `### Origin of Data and Evidence` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/ARTIFACT_LINKS.md` |
| Methods: variables (metrics/measures definitions) | `## 3 Methods` + `### Variables and Measures` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/colab/apr20_pilot_colab.py` |
| Methods: selection strategy (datasets/metrics/parameters) | `### Selection Strategy` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/mar30_submission/reproduction/work/DL-CIBuild/dataset/cloudify.csv` |
| Methods: methodology (replicable steps) | `### Methodology (Replicable Protocol)` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/colab/COLAB_STEPS.md` |
| Methods: data analysis definition + appropriateness | `### Data Analysis and Appropriateness` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/apr20_working_draft.md` | `/Users/vatsaldp/Documents/se_proj/apr20_submission/artifacts/pilot_fold_metrics.csv`, `/Users/vatsaldp/Documents/se_proj/apr20_submission/artifacts/pilot_summary.json` |

## Final QA Checks Before Submission Writing Freeze

- [ ] All listed section headings are present verbatim in `apr20_working_draft.md`.
- [ ] Terminology is consistent: `early/online detection` and `post-failure/RCA`.
- [ ] Pilot scope is written as `cloudify 5 folds`.
- [ ] Output file names match the naming contract in this checklist.
