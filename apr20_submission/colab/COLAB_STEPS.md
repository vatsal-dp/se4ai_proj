# Apr 20 Colab Runbook (Google Colab Only)

This runbook executes the Apr 20 pilot workflow entirely in Google Colab and writes outputs to Google Drive.

## 1) Open Colab and mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## 2) Get the repository into Colab

Pick one of the two options below.

### Option A (recommended): clone from GitHub

```bash
%cd /content
!git clone <YOUR_REPO_URL> se_proj
%cd /content/se_proj
```

### Option B: open existing repo from Drive

```bash
%cd /content/drive/MyDrive/<PATH_TO_REPO>/se_proj
```

## 3) Install dependencies

Install baseline dependencies:

```bash
!python -m pip install --upgrade pip
!pip install numpy pandas scikit-learn scipy
```

Install DL-CIBuild runtime dependencies (optional but recommended):

```bash
!pip install tensorflow==2.16.1 keras
```

If you skip TensorFlow/Keras, the script still runs and records DL-CIBuild rows as `not_run` with a reason.

## 4) Run the pilot script

Choose an output folder in Drive (example below).

```bash
!mkdir -p /content/drive/MyDrive/se_proj_apr20_outputs
!python apr20_submission/colab/apr20_pilot_colab.py \
  --repo-root /content/se_proj \
  --output-dir /content/drive/MyDrive/se_proj_apr20_outputs \
  --seed 42
```

If you want to intentionally skip DL-CIBuild execution:

```bash
!python apr20_submission/colab/apr20_pilot_colab.py \
  --repo-root /content/se_proj \
  --output-dir /content/drive/MyDrive/se_proj_apr20_outputs \
  --seed 42 \
  --skip-dl-cibuild
```

### Optional: run repeated setup variants (matrix mode)

This mode mirrors the "same tasks, multiple setups, repeated runs" pattern.

```bash
!mkdir -p /content/drive/MyDrive/se_proj_apr20_matrix_outputs
!python apr20_submission/colab/apr20_matrix_colab.py \
  --repo-root /content/se_proj \
  --output-dir /content/drive/MyDrive/se_proj_apr20_matrix_outputs \
  --experiment-name apr20_logreg_parameter_sensitivity \
  --tasks majority_class,logistic_regression \
  --setups baseline,conservative_regularization,expressive_regularization,short_history,long_history \
  --repeats 8 \
  --base-seed 42 \
  --max-folds 5
```

To include DL-CIBuild rows in matrix mode, add `dl_cibuild_default` to `--tasks`.
For faster smoke tests, reduce `--repeats` (for example `--repeats 2`).
You can control DL repeats independently with:
- `--dl-repeats <N>` (defaults to `--repeats` when omitted or `<=0`)
- `--dl-base-seed <S>` (defaults to `--base-seed`)
- `--dl-tuner default|tpe|ga|pso|bohb|rs` (default is `default`)

Example including DL-CIBuild with separate repeat settings:

```bash
!python apr20_submission/colab/apr20_matrix_colab.py \
  --repo-root /content/se_proj \
  --output-dir /content/drive/MyDrive/se_proj_apr20_matrix_outputs \
  --experiment-name apr20_full_matrix_with_dl \
  --tasks majority_class,logistic_regression,dl_cibuild_default \
  --setups baseline,long_history \
  --repeats 8 \
  --base-seed 42 \
  --dl-repeats 12 \
  --dl-base-seed 100 \
  --dl-tuner default \
  --max-folds 5
```

## 5) Verify outputs were created

```bash
!ls -lh /content/drive/MyDrive/se_proj_apr20_outputs
```

Expected files:
- `pilot_fold_metrics.csv`
- `pilot_summary.json`
- `colab_run_log.txt`
- `matrix_fold_metrics.csv` (if matrix mode is run)
- `matrix_summary.json` (if matrix mode is run)
- `matrix_run_log.txt` (if matrix mode is run)

## 6) Quick sanity checks in Colab

```python
import json
import pandas as pd

out_dir = "/content/drive/MyDrive/se_proj_apr20_outputs"
metrics = pd.read_csv(f"{out_dir}/pilot_fold_metrics.csv")
summary = json.load(open(f"{out_dir}/pilot_summary.json"))

print("Rows:", len(metrics))
print("Models:", sorted(metrics["model"].dropna().unique()))
print("Status counts:")
print(metrics.groupby(["model", "status"]).size())
print("Summary keys:", list(summary.keys()))
```

## 7) Share outputs back to writing workflow

Provide the three output files to the paper-writing step:
- fold-level CSV (`pilot_fold_metrics.csv`)
- aggregate summary JSON (`pilot_summary.json`)
- execution log (`colab_run_log.txt`)
