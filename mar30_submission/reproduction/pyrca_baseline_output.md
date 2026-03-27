# PyRCA Full Reproduction Output

Candidate: **PyRCA** (`salesforce/PyRCA`)

## Runtime Strategy

Local host install failed previously due Python 3.14 incompatibility (`scikit-learn<1.2` pin).  
Reproduction was completed in Docker with a compatible stack:
- Python `3.10`
- OpenJDK `21`
- `numpy<2` to avoid ABI mismatch with `scikit-learn==1.1.3`

## Full Command Used

```bash
docker run --rm \
  -v /Users/vatsaldp/Documents/se_proj:/workspace \
  -w /workspace/mar30_submission/reproduction/work/PyRCA \
  python:3.10-slim \
  bash -lc "apt-get update && apt-get install -y --no-install-recommends openjdk-21-jre-headless \
    && pip install --no-cache-dir 'setuptools<81' 'numpy<2' \
    && pip install --no-cache-dir -e . \
    && python tests/applications/example/run_rca.py"
```

## Result

- Exit code: `0`
- Main evidence log: `logs/pyrca_full_run.txt`
- Script executed successfully: `tests/applications/example/run_rca.py`

Generated model artifacts:
- `work/PyRCA/pyrca/applications/example/models/adjacency_df.pkl`
- `work/PyRCA/pyrca/applications/example/models/bn.bif`
- `work/PyRCA/pyrca/applications/example/models/bn_info.pkl`
- `work/PyRCA/pyrca/applications/example/models/graph.json`

## Key RCA Output (from log)

Top-ranked root causes returned by the example pipeline:
- `ROOT_conn_pool` with score `0.99`
- `ROOT_request` with score `0.6461522668010075`
- `ROOT_pod` with score `0.5324891917895469`
- `ROOT_gen_size` with score `0.5156904910266921`
