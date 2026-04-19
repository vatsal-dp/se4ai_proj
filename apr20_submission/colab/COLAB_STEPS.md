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

## 5) Verify outputs were created

```bash
!ls -lh /content/drive/MyDrive/se_proj_apr20_outputs
```

Expected files:
- `pilot_fold_metrics.csv`
- `pilot_summary.json`
- `colab_run_log.txt`

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
