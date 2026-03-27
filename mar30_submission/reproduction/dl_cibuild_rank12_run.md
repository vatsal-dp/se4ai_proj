# DL-CIBuild Rank-12 Reproduction Notes

Paper: **Improving the prediction of continuous integration build failures using deep learning**  
Rank in top-100 sheet: **12**  
Official repo: <https://github.com/stilab-ets/DL-CIBuild>

## What was executed

- Runtime: Docker image `tensorflow/tensorflow:2.16.1` (amd64 on Apple Silicon host).
- Dependencies installed in-container: `pandas`, `scikit-learn`.
- Dataset: `dataset/cloudify.csv`.
- Validation protocol: `online_validation_folds`.
- Run scope: first online fold (`fold_index = 0`), default tuner settings from the repo (`evaluate_tuner("default", train_sets[0])`), then fold-0 test prediction.

## Compatibility hardening applied

To allow default-mode execution without installing every optional tuner framework:

- File: `work/DL-CIBuild/DL-CIBuild scripts/LSTM_Tuner.py`
- Changes:
  - Made optional imports resilient (`hyperopt`, `optunity`, `ConfigSpace`, `hpbandster`, `GA.GARunner`, `imblearn.SMOTE`).
  - Added explicit branch guards so `tpe`, `rs`, `pso`, `bohb`, and `ga` raise clear import errors when optional deps are missing.
  - Ensured hyperopt search-space construction only occurs when `hyperopt` is available.
  - Kept behavior unchanged for the `default` tuner path.

## Output artifact

- JSON output: `dl_cibuild_rank12_output.json`
- Key metrics (fold 0, cloudify):
  - Train AUC: `0.8790`
  - Train Accuracy: `0.8972`
  - Train F1: `0.8328`
  - Test AUC: `0.8843`
  - Test Accuracy: `0.8885`
  - Test F1: `0.8694`
  - Train wall-clock time reported by script: `42.82s`
