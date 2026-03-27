#!/usr/bin/env python3
"""Generate synthetic FastPC input files for rca_baselines.

This creates the six `pod_level_data_<metric>.npy` files expected by:
`Baseline/Offline/FastPC/test_FastPC_pod_metric.py`.
"""

from pathlib import Path

import numpy as np


def main() -> None:
    root = Path(
        "/Users/vatsaldp/Documents/se_proj/mar30_submission/reproduction/rca_synth/20211203"
    )
    root.mkdir(parents=True, exist_ok=True)

    label = "ratings.book-info.svc.cluster.local:9080/*"
    pods = ["details-v1", "ratings-v1", "reviews-v3", "productpage-v1"]
    total_steps = 20000
    rng = np.random.default_rng(42)

    metrics = [
        "cpu_usage",
        "memory_usage",
        "rate_transmitted_packets",
        "rate_received_packets",
        "received_bandwidth",
        "transmit_bandwidth",
    ]

    for idx, metric in enumerate(metrics):
        base = rng.normal(loc=0.0, scale=1.0 + 0.1 * idx, size=(total_steps, len(pods)))
        drift = np.linspace(0.0, 2.5 + 0.1 * idx, total_steps).reshape(-1, 1)
        sequence = base + drift

        # Inject a stronger anomaly signal in one pod per metric.
        hotspot_col = idx % len(pods)
        sequence[total_steps // 2 :, hotspot_col] += 5.0 + 0.2 * idx

        # Last column is the KPI feature used as result indicator in FastPC.
        kpi = (
            0.3 * sequence[:, hotspot_col]
            + 0.1 * sequence.mean(axis=1)
            + rng.normal(0.0, 0.2, total_steps)
        )
        full = np.concatenate([sequence, kpi.reshape(-1, 1)], axis=1).astype(np.float32)

        payload = {
            label: {
                "Pod_Name": pods,
                "Sequence": full,
                "KPI_Feature": ["kpi"],
            }
        }
        np.save(root / f"pod_level_data_{metric}.npy", payload, allow_pickle=True)

    print(f"Synthetic FastPC input generated at: {root}")


if __name__ == "__main__":
    main()
