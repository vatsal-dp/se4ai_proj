#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

docker run --rm \
  -v "${ROOT_DIR}:/workspace" \
  -w /workspace \
  tensorflow/tensorflow:2.16.1 \
  bash -lc "
set -euo pipefail
python -m pip install --no-cache-dir pandas scikit-learn
python - <<'PY'
import os
import sys
import json
import numpy as np

repo = '/workspace/reproduction/work/DL-CIBuild'
scripts_dir = os.path.join(repo, 'DL-CIBuild scripts')
os.chdir(repo)
sys.path.insert(0, scripts_dir)

import Utils
import LSTM_Tuner

dataset_name = 'cloudify.csv'
dataset = Utils.getDataset(dataset_name)
train_sets, test_sets = Utils.online_validation_folds(dataset)
k = 0

entry_train = LSTM_Tuner.evaluate_tuner('default', train_sets[k])
X_test, y_test = LSTM_Tuner.test_preprocess(train_sets[k], test_sets[k], entry_train['params']['time_step'])
entry_test = Utils.predict_lstm(entry_train['model'], X_test, y_test)

def to_jsonable(value):
    if isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    if isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {k: to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    return value

train_out = {k: v for k, v in entry_train.items() if k != 'model'}
result = {
    'paper_rank': 12,
    'paper_title': 'Improving the prediction of continuous integration build failures using deep learning',
    'repository': 'https://github.com/stilab-ets/DL-CIBuild',
    'dataset': dataset_name,
    'validation_mode': 'online_validation_folds',
    'fold_index': k,
    'train_rows': int(len(train_sets[k])),
    'test_rows': int(len(test_sets[k])),
    'tuner': 'default',
    'train_metrics': to_jsonable(train_out),
    'test_metrics': to_jsonable(entry_test),
}

output_path = '/workspace/reproduction/dl_cibuild_rank12_output.json'
with open(output_path, 'w') as handle:
    json.dump(result, handle, indent=2)

print(json.dumps(result, indent=2))
print('Saved:', output_path)
PY
"
