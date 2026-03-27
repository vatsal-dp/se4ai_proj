#!/usr/bin/env python3
"""
Curate detailed above-knee reading matrix and create a literal Venn-style overlap figure.

Inputs:
- data/above_knee_set.csv
- data/papers_raw.csv

Outputs:
- data/reading_matrix.csv
- data/above_knee_detailed_notes.md
- figures/overlap_figure.png
"""

from __future__ import annotations

import csv
import os
from collections import Counter
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import pandas as pd


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIG_DIR = os.path.join(ROOT_DIR, "figures")


MANUAL_ANNOTATIONS: Dict[str, Dict[str, str]] = {
    "Reinforcement learning for automatic test case prioritization and selection in continuous integration": {
        "input_artifact": "mixed_artifacts",
        "model_family": "reinforcement_learning",
        "task": "optimization",
        "prediction_timing": "early_or_online",
        "evaluation_metric": "apfd,napfd,fault_detection_rate",
        "detailed_reading_note": "RL-based policy for CI test prioritization/selection using historical execution outcomes and change context.",
    },
    "Oops, My Tests Broke the Build: An Explorative Analysis of Travis CI with GitHub": {
        "input_artifact": "log_text",
        "model_family": "statistical_empirical",
        "task": "diagnosis_or_rca",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "failure_rate,category_proportions,descriptive_statistics",
        "detailed_reading_note": "Empirical characterization of CI failures/testing behavior in Travis+GitHub workflows.",
    },
    "iDFlakies: A Framework for Detecting and Partially Classifying Flaky Tests": {
        "input_artifact": "log_text",
        "model_family": "rule_or_statistical",
        "task": "diagnosis_or_rca",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "flaky_detection_rate,classification_precision",
        "detailed_reading_note": "Detects order-dependent flaky tests via controlled reordering/reruns and partial flake classification.",
    },
    "Test case selection and prioritization using machine learning: a systematic literature review": {
        "input_artifact": "mixed_artifacts",
        "model_family": "traditional_ml",
        "task": "optimization",
        "prediction_timing": "early_or_online",
        "evaluation_metric": "study_counts,taxonomy_coverage",
        "detailed_reading_note": "SLR summarizing ML methods for test selection/prioritization in CI-like settings.",
    },
    "Root causing flaky tests in a large-scale industrial setting": {
        "input_artifact": "log_text",
        "model_family": "rule_or_statistical",
        "task": "diagnosis_or_rca",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "diagnosis_precision,time_to_diagnosis",
        "detailed_reading_note": "Industrial flaky-test root-cause localization pipeline integrated into CI troubleshooting.",
    },
    "How Open Source Projects Use Static Code Analysis Tools in Continuous Integration Pipelines": {
        "input_artifact": "code_or_commit",
        "model_family": "statistical_empirical",
        "task": "explanation",
        "prediction_timing": "early_or_online",
        "evaluation_metric": "adoption_rate,warning_density,usage_patterns",
        "detailed_reading_note": "Studies integration and usage patterns of static analysis in CI pipelines.",
    },
    "An Empirical Analysis of Build Failures in the Continuous Integration Workflows of Java-Based Open-Source Software": {
        "input_artifact": "log_text",
        "model_family": "statistical_empirical",
        "task": "diagnosis_or_rca",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "failure_category_distribution,failure_frequency",
        "detailed_reading_note": "Empirical taxonomy and frequency analysis of build failures in Java OSS CI workflows.",
    },
    "Test Case Prioritization in Continuous Integration environments: A systematic mapping study": {
        "input_artifact": "mixed_artifacts",
        "model_family": "traditional_ml",
        "task": "optimization",
        "prediction_timing": "early_or_online",
        "evaluation_metric": "study_counts,taxonomy_coverage",
        "detailed_reading_note": "Mapping study of CI test prioritization strategies and evidence trends.",
    },
    "An empirical characterization of bad practices in continuous integration": {
        "input_artifact": "code_or_commit",
        "model_family": "statistical_empirical",
        "task": "explanation",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "anti_pattern_frequency,association_statistics",
        "detailed_reading_note": "Characterizes CI anti-patterns and links them to quality/process degradation.",
    },
    "HireBuild": {
        "input_artifact": "code_or_commit",
        "model_family": "deep_learning",
        "task": "optimization",
        "prediction_timing": "early_or_online",
        "evaluation_metric": "build_success_rate,time_saved",
        "detailed_reading_note": "AI-assisted build maintenance/repair direction targeting developer productivity in build workflows.",
    },
    "A Tale of CI Build Failures: An Open Source and a Financial Organization Perspective": {
        "input_artifact": "log_text",
        "model_family": "statistical_empirical",
        "task": "diagnosis_or_rca",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "failure_category_distribution,cross_context_comparison",
        "detailed_reading_note": "Comparative build-failure characterization across OSS and industrial financial CI contexts.",
    },
    "Improving the prediction of continuous integration build failures using deep learning": {
        "input_artifact": "mixed_artifacts",
        "model_family": "deep_learning",
        "task": "prediction",
        "prediction_timing": "early_or_online",
        "evaluation_metric": "precision,recall,f1,auc",
        "detailed_reading_note": "Deep-learning model for CI build-failure prediction from historical CI artifacts.",
    },
    "Test prioritization in continuous integration environments": {
        "input_artifact": "mixed_artifacts",
        "model_family": "traditional_ml",
        "task": "optimization",
        "prediction_timing": "early_or_online",
        "evaluation_metric": "apfd,time_to_first_failure",
        "detailed_reading_note": "Prioritization strategy for CI test suites to detect failures earlier under time budget.",
    },
    "A Study on the Interplay between Pull Request Review and Continuous Integration Builds": {
        "input_artifact": "code_or_commit",
        "model_family": "statistical_empirical",
        "task": "explanation",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "correlation_effect_size,descriptive_statistics",
        "detailed_reading_note": "Examines relationship between PR review dynamics and CI build outcomes.",
    },
    "Who broke the build? Automatically identifying changes that induce test failures in continuous integration at Google Scale": {
        "input_artifact": "code_or_commit",
        "model_family": "rule_or_statistical",
        "task": "diagnosis_or_rca",
        "prediction_timing": "post_failure_or_rca",
        "evaluation_metric": "topk_accuracy,precision,recall",
        "detailed_reading_note": "At-scale culprit-change localization for CI test failures in fast development cycles.",
    },
}


def ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)


def clip_text(text: str, max_chars: int = 420) -> str:
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars - 1].rstrip() + "…"


def safe_text(value) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if text.lower() in {"nan", "none"}:
        return ""
    return text


def write_detailed_notes(matrix: pd.DataFrame, raw_by_title: Dict[str, Dict], out_path: str) -> None:
    lines: List[str] = [
        "# Above-Knee Detailed Reading Notes",
        "",
        "Source set: `data/above_knee_set.csv`",
        "Rows: all papers above knee threshold, each with explicit classification rationale.",
        "",
    ]

    for _, row in matrix.sort_values(by="above_knee_rank").iterrows():
        title = str(row["title"])
        raw_row = raw_by_title.get(title, {})
        abstract = safe_text(raw_row.get("abstract", "")) if raw_row is not None else ""
        abstract_excerpt = clip_text(abstract) if abstract else "Not available in retrieved metadata."

        lines.extend(
            [
                f"## {int(row['above_knee_rank'])}. {title}",
                f"- Year/Venue/Citations: {int(row['year'])} / {row['venue']} / {int(row['citationCount'])}",
                f"- Input artifact: `{row['input_artifact']}`",
                f"- Model family: `{row['model_family']}`",
                f"- Task: `{row['task']}`",
                f"- Prediction timing: `{row['prediction_timing']}`",
                f"- Evaluation metric(s): `{row['evaluation_metric']}`",
                f"- Detailed reading note: {row['detailed_reading_note']}",
                f"- Abstract evidence excerpt: {abstract_excerpt}",
                "",
            ]
        )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")


def make_literal_venn(df: pd.DataFrame, out_path: str) -> None:
    # Binary mask counts for exact overlaps among 4 groups:
    # bit0=LogText, bit1=LLM, bit2=Early, bit3=Post.
    region_counts = Counter()
    for _, row in df.iterrows():
        mask = (
            int(row["group_log_text_inputs"]) * 1
            + int(row["group_llm_or_generative"]) * 2
            + int(row["group_early_or_online"]) * 4
            + int(row["group_post_failure_or_rca"]) * 8
        )
        region_counts[mask] += 1

    log_n = int(df["group_log_text_inputs"].sum())
    llm_n = int(df["group_llm_or_generative"].sum())
    early_n = int(df["group_early_or_online"].sum())
    post_n = int(df["group_post_failure_or_rca"].sum())
    all4_n = sum(
        1
        for _, r in df.iterrows()
        if r["group_log_text_inputs"] == 1
        and r["group_llm_or_generative"] == 1
        and r["group_early_or_online"] == 1
        and r["group_post_failure_or_rca"] == 1
    )

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.2, 1.0]}
    )

    # Literal Venn-style circles.
    circles = [
        Circle((-0.35, 0.25), 0.58, color="#4c78a8", alpha=0.35, ec="#2f4f6f", lw=1.5),
        Circle((0.35, 0.25), 0.58, color="#f58518", alpha=0.30, ec="#8a4a08", lw=1.5),
        Circle((-0.35, -0.25), 0.58, color="#54a24b", alpha=0.30, ec="#2f5f2a", lw=1.5),
        Circle((0.35, -0.25), 0.58, color="#e45756", alpha=0.30, ec="#7d2c2b", lw=1.5),
    ]
    for c in circles:
        ax1.add_patch(c)

    ax1.set_xlim(-1.2, 1.2)
    ax1.set_ylim(-1.05, 1.05)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("Venn Diagram (4 Groups, Above-Knee Set)", fontsize=12)

    ax1.text(-0.85, 0.78, f"Log-text inputs\nn={log_n}", fontsize=10, ha="left")
    ax1.text(0.45, 0.78, f"LLM/generative\nn={llm_n}", fontsize=10, ha="left")
    ax1.text(-0.98, -0.92, f"Early/online\nn={early_n}", fontsize=10, ha="left")
    ax1.text(0.53, -0.92, f"Post-failure/RCA\nn={post_n}", fontsize=10, ha="left")
    ax1.text(0.0, 0.0, f"All 4 overlap: {all4_n}", fontsize=10, ha="center", weight="bold")

    # A few high-signal overlap labels near major overlap regions.
    pair_counts = {
        "Log∩LLM": int(
            ((df["group_log_text_inputs"] == 1) & (df["group_llm_or_generative"] == 1)).sum()
        ),
        "Log∩Early": int(
            ((df["group_log_text_inputs"] == 1) & (df["group_early_or_online"] == 1)).sum()
        ),
        "Log∩Post": int(
            ((df["group_log_text_inputs"] == 1) & (df["group_post_failure_or_rca"] == 1)).sum()
        ),
        "Early∩Post": int(
            ((df["group_early_or_online"] == 1) & (df["group_post_failure_or_rca"] == 1)).sum()
        ),
    }
    ax1.text(0.0, 0.52, f"Log∩LLM: {pair_counts['Log∩LLM']}", fontsize=9, ha="center")
    ax1.text(-0.62, 0.0, f"Log∩Early: {pair_counts['Log∩Early']}", fontsize=9, ha="center")
    ax1.text(0.0, -0.55, f"Early∩Post: {pair_counts['Early∩Post']}", fontsize=9, ha="center")
    ax1.text(0.62, 0.0, f"Log∩Post: {pair_counts['Log∩Post']}", fontsize=9, ha="center")

    # Exact region counts table on the right.
    ax2.axis("off")
    ax2.set_title("Exact Overlap Region Sizes", fontsize=12)
    bit_label = {
        1: "Log only",
        2: "LLM only",
        3: "Log+LLM",
        4: "Early only",
        5: "Log+Early",
        6: "LLM+Early",
        7: "Log+LLM+Early",
        8: "Post only",
        9: "Log+Post",
        10: "LLM+Post",
        11: "Log+LLM+Post",
        12: "Early+Post",
        13: "Log+Early+Post",
        14: "LLM+Early+Post",
        15: "Log+LLM+Early+Post",
        0: "None of the 4 groups",
    }
    y = 0.95
    for mask, cnt in sorted(region_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        ax2.text(0.02, y, f"{bit_label.get(mask, str(mask))}: {cnt}", fontsize=10, ha="left")
        y -= 0.055
    if not region_counts:
        ax2.text(0.02, y, "No regions found", fontsize=10, ha="left")

    plt.tight_layout()
    plt.savefig(out_path, dpi=220)
    plt.close()


def main() -> None:
    ensure_dirs()

    above_path = os.path.join(DATA_DIR, "above_knee_set.csv")
    raw_path = os.path.join(DATA_DIR, "papers_raw.csv")
    out_matrix = os.path.join(DATA_DIR, "reading_matrix.csv")
    out_notes = os.path.join(DATA_DIR, "above_knee_detailed_notes.md")
    out_venn = os.path.join(FIG_DIR, "overlap_figure.png")

    above = pd.read_csv(above_path)
    raw = pd.read_csv(raw_path)
    raw_by_title = {
        str(row["title"]): row for _, row in raw.iterrows() if isinstance(row.get("title"), str)
    }

    records: List[Dict] = []
    for _, row in above.iterrows():
        title = str(row["title"])
        ann = MANUAL_ANNOTATIONS.get(title)
        if not ann:
            # Keep strict: all above-knee should be manually classified in detail.
            raise KeyError(f"Missing manual annotation for above-knee title: {title}")

        raw_row = raw_by_title.get(title, {})
        abstract = safe_text(raw_row.get("abstract", "")) if raw_row is not None else ""
        code_link = row["openAccessPdf"] if isinstance(row.get("openAccessPdf"), str) and row["openAccessPdf"] else row["url"]

        rec = {
            "above_knee_rank": int(row["rank"]),
            "title": title,
            "year": int(row["year"]),
            "venue": row["venue"],
            "citationCount": int(row["citationCount"]),
            "input_artifact": ann["input_artifact"],
            "model_family": ann["model_family"],
            "task": ann["task"],
            "prediction_timing": ann["prediction_timing"],
            "evaluation_metric": ann["evaluation_metric"],
            "code_or_data_link": code_link,
            "detailed_reading_note": ann["detailed_reading_note"],
            "reading_depth": "detailed",
            "abstract_chars": int(len(abstract)),
            "abstract_excerpt": clip_text(abstract) if abstract else "Not available in retrieved metadata.",
        }

        rec["group_log_text_inputs"] = 1 if rec["input_artifact"] == "log_text" else 0
        rec["group_llm_or_generative"] = 1 if rec["model_family"] == "llm_or_generative" else 0
        rec["group_early_or_online"] = 1 if rec["prediction_timing"] in {"early_or_online", "both"} else 0
        rec["group_post_failure_or_rca"] = 1 if rec["prediction_timing"] in {"post_failure_or_rca", "both"} else 0
        records.append(rec)

    matrix = pd.DataFrame(records).sort_values(by="above_knee_rank")
    matrix.to_csv(out_matrix, index=False, quoting=csv.QUOTE_MINIMAL)
    write_detailed_notes(matrix, raw_by_title, out_notes)

    make_literal_venn(matrix, out_venn)

    # Print compact summary for caller.
    print(
        {
            "rows": len(matrix),
            "log_text": int(matrix["group_log_text_inputs"].sum()),
            "llm_or_generative": int(matrix["group_llm_or_generative"].sum()),
            "early_or_online": int(matrix["group_early_or_online"].sum()),
            "post_failure_or_rca": int(matrix["group_post_failure_or_rca"].sum()),
        }
    )


if __name__ == "__main__":
    main()
