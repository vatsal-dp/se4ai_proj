# rca_baselines Full Reproduction Output

Candidate: **LEMMA-RCA baselines** (`KnowledgeDiscovery/rca_baselines`)  
Method executed: **FastPC metric-only baseline**

## Runtime Strategy

Two compatibility constraints had to be handled:
- `libspot.so` in the repo is an **x86-64** shared object.
- The host machine is ARM-based and uses Python 3.14 by default.

To reproduce successfully, execution was done in Docker with:
- `--platform linux/amd64`
- Python `3.10`
- `libgomp1` installed (required by `libspot.so`)

## Local Compatibility Patches (in workspace copy)

Files patched to support CPU-compatible execution:
- `work/rca_baselines/Baseline/Offline/FastPC/fastPC.py`
  - fixed CUDA gating so CPU fallback is respected
  - removed hard dependency on `numba`/`miceforest`
  - made matplotlib import optional
- `work/rca_baselines/Baseline/Offline/FastPC/rca.py`
  - made `causalnex` optional (only needed for `dynotears`)
  - FastPC path now requests CUDA only when available

## Synthetic Input Used

Because official preprocessed dataset files were not bundled in the repository, valid FastPC inputs were generated in:
- `reproduction/rca_synth/20211203/`

Generator script:
- `reproduction/scripts/generate_fastpc_synthetic_input.py`

## Full Command Used

```bash
docker run --rm --platform linux/amd64 \
  -v /Users/vatsaldp/Documents/se_proj:/workspace \
  -w /workspace/mar30_submission/reproduction/work/rca_baselines/Baseline/Offline/FastPC \
  python:3.10-slim \
  bash -lc "apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && pip install --no-cache-dir 'numpy<2' pandas scikit-learn scipy networkx torch pingouin \
    && python test_FastPC_pod_metric.py \
      --dataset 20211203 \
      --path_dir /workspace/mar30_submission/reproduction/rca_synth/20211203/ \
      --output_dir /workspace/mar30_submission/reproduction/rca_baselines_output/"
```

## Result

- Exit code: `0`
- Main evidence log: `reproduction/logs/rca_baselines_full_run.txt`
- Output directory: `reproduction/rca_baselines_output/`

Generated output artifacts include:
- `Pod_level_combine_ranking.csv`
- `learned_metric_weight_pod.csv`
- `inrc_pod_<metric>.npy` and `inrc_pod_<metric>_ranking.csv` for all six metrics

Per-metric rankings were produced successfully (example top results):
- `cpu_usage`: `details-v1` score `0.8679`
- `memory_usage`: `ratings-v1` score `0.8676`
- `rate_transmitted_packets`: `reviews-v3` score `0.8653`
- `rate_received_packets`: `productpage-v1` score `0.8675`
