#!/usr/bin/env python3
"""
Generate March 30 submission artifacts for the CI/CD failure-analysis topic.

Outputs:
- data/search_log.md
- data/papers_raw.csv
- data/top100_papers.csv
- data/above_knee_set.csv
- data/reading_matrix.csv
- data/knee_summary.json
- figures/knee_plot.png
- figures/overlap_figure.png
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import math
import os
import re
import time
from collections import Counter
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import requests


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIG_DIR = os.path.join(ROOT_DIR, "figures")

OPENALEX_WORKS = "https://api.openalex.org/works"

SEARCH_QUERIES = [
    "continuous integration build failure",
    "travis ci build failure",
    "continuous integration flaky tests",
    "ci/cd log analysis software",
    "continuous integration regression test selection",
]

OPENALEX_SELECT = (
    "id,display_name,publication_year,cited_by_count,doi,primary_location,"
    "abstract_inverted_index,concepts,primary_topic"
)

# Relevance keywords to suppress unrelated papers.
STRONG_RELEVANCE_KEYWORDS = [
    "continuous integration",
    "ci/cd",
    "ci cd",
    "build failure",
    "build failures",
    "root cause",
    "software pipeline",
    "pipeline failure",
]

WEAK_RELEVANCE_KEYWORDS = [
    "build",
    "pipeline",
    "log",
    "failure",
    "devops",
    "software engineering",
    "test selection",
    "flaky",
    "ci ",
]

OBVIOUS_FALSE_POSITIVE_KEYWORDS = [
    "cardio",
    "clinical",
    "oncology",
    "surgery",
    "heart",
    "biomedical",
    "medicine",
    "patient",
    "brain",
    "genomics",
    "microbial",
    "psychotherapy",
    "operations management",
    "supply chain",
    "wind farm",
]

TITLE_MUST_HAVE_KEYWORDS = [
    "continuous integration",
    "ci/cd",
    "travis",
    "build",
    "flaky",
    "regression test",
    "test",
    "pipeline",
    "pull request",
    "log",
]


def ensure_dirs() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(FIG_DIR, exist_ok=True)


def norm_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def deinvert_abstract(inverted_index: Dict | None) -> str:
    if not inverted_index:
        return ""
    if not isinstance(inverted_index, dict):
        return ""
    positioned: List[Tuple[int, str]] = []
    for word, positions in inverted_index.items():
        if not isinstance(positions, list):
            continue
        for pos in positions:
            if isinstance(pos, int):
                positioned.append((pos, word))
    if not positioned:
        return ""
    positioned.sort(key=lambda x: x[0])
    return " ".join(word for _, word in positioned)


def relevance_score(title: str, abstract: str, venue: str) -> int:
    text = f"{title} {abstract} {venue}".lower()
    strong_hits = sum(1 for kw in STRONG_RELEVANCE_KEYWORDS if kw in text)
    weak_hits = sum(1 for kw in WEAK_RELEVANCE_KEYWORDS if kw in text)
    score = strong_hits * 3 + weak_hits
    # Boost likely SE venues.
    if any(v in text for v in ["icse", "fse", "ase", "tosem", "emse", "msr"]):
        score += 2
    return score


def is_obvious_false_positive(title: str, abstract: str, venue: str) -> bool:
    text = f"{title} {abstract} {venue}".lower()
    return any(kw in text for kw in OBVIOUS_FALSE_POSITIVE_KEYWORDS)


def title_has_ci_signal(title: str) -> bool:
    t = title.lower()
    return any(kw in t for kw in TITLE_MUST_HAVE_KEYWORDS)


def classify_input_artifact(text: str) -> str:
    t = text.lower()
    if "log" in t:
        return "log_text"
    if any(x in t for x in ["metric", "trace", "telemetry", "timeseries", "time series"]):
        return "metrics_or_traces"
    if any(x in t for x in ["source code", "code change", "commit", "pull request"]):
        return "code_or_commit"
    if any(x in t for x in ["multi-modal", "multimodal", "heterogeneous"]):
        return "mixed_artifacts"
    return "unspecified"


def classify_model_family(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ["llm", "large language model", "gpt", "transformer", "generative"]):
        return "llm_or_generative"
    if any(x in t for x in ["neural", "deep learning", "bert", "lstm", "cnn"]):
        return "deep_learning"
    if any(x in t for x in ["random forest", "xgboost", "svm", "classification", "machine learning"]):
        return "traditional_ml"
    if any(x in t for x in ["rule-based", "heuristic", "statistical"]):
        return "rule_or_statistical"
    return "unspecified"


def classify_task(text: str) -> str:
    t = text.lower()
    if any(x in t for x in ["predict", "forecast", "failure prediction", "risk"]):
        return "prediction"
    if any(x in t for x in ["root cause", "diagnosis", "localization", "debug"]):
        return "diagnosis_or_rca"
    if any(x in t for x in ["optimization", "test selection", "scheduling"]):
        return "optimization"
    if any(x in t for x in ["explain", "explanation", "summarization"]):
        return "explanation"
    return "mixed_or_unspecified"


def classify_timing(text: str) -> str:
    t = text.lower()
    early = any(x in t for x in ["early", "online", "stream", "real-time", "realtime", "proactive"])
    post = any(
        x in t
        for x in ["post-mortem", "postmortem", "root cause", "diagnosis", "after failure", "incident analysis"]
    )
    if early and post:
        return "both"
    if early:
        return "early_or_online"
    if post:
        return "post_failure_or_rca"
    return "unspecified"


def infer_eval_metric(text: str) -> str:
    t = text.lower()
    metric_candidates = [
        "f1",
        "precision",
        "recall",
        "accuracy",
        "auc",
        "auroc",
        "mrr",
        "map",
        "latency",
        "runtime",
    ]
    found = [m for m in metric_candidates if m in t]
    if not found:
        return "not_stated_in_metadata"
    return ",".join(found)


def fetch_papers_for_query(query: str, limit: int = 120, year_from: int = 2015) -> List[Dict]:
    all_rows: List[Dict] = []
    page = 1
    page_size = 50
    session = requests.Session()

    while len(all_rows) < limit:
        filter_expr = (
            f"from_publication_date:{year_from}-01-01,"
            f"title_and_abstract.search:{query},"
            "concepts.id:C41008148"
        )
        params = {
            "page": page,
            "per-page": page_size,
            "filter": filter_expr,
            "sort": "cited_by_count:desc",
            "select": OPENALEX_SELECT,
            "mailto": "student@example.edu",
        }
        response = session.get(OPENALEX_WORKS, params=params, timeout=40)
        response.raise_for_status()
        payload = response.json()
        data = payload.get("results", [])
        if not data:
            break

        for item in data:
            primary_location = item.get("primary_location") or {}
            source = primary_location.get("source") or {}
            venue = source.get("display_name") or primary_location.get("raw_source_name") or ""
            abstract = deinvert_abstract(item.get("abstract_inverted_index"))
            row = {
                "source_query": query,
                "paperId": item.get("id"),
                "title": norm_text(item.get("display_name")),
                "year": item.get("publication_year"),
                "venue": norm_text(venue),
                "citationCount": item.get("cited_by_count") or 0,
                "url": item.get("doi") or item.get("id") or "",
                "abstract": norm_text(item.get("abstract")),
                "publicationTypes": "",
                "openAccessPdf": primary_location.get("pdf_url") or "",
                "primary_topic": "",
            }
            if abstract:
                row["abstract"] = abstract
            primary_topic = item.get("primary_topic") or {}
            if isinstance(primary_topic, dict):
                row["primary_topic"] = norm_text(primary_topic.get("display_name"))
            all_rows.append(row)

        if len(all_rows) >= limit:
            all_rows = all_rows[:limit]
            break

        page += 1
        time.sleep(0.4)

    return all_rows


def dedupe_rows(rows: List[Dict]) -> List[Dict]:
    by_id: Dict[str, Dict] = {}
    by_title: Dict[str, Dict] = {}

    for row in rows:
        pid = row.get("paperId") or ""
        title_key = norm_text(row.get("title", "")).lower()
        row["year"] = int(row["year"]) if row.get("year") else None
        row["citationCount"] = int(row.get("citationCount") or 0)
        row["relevance_score"] = relevance_score(row.get("title", ""), row.get("abstract", ""), row.get("venue", ""))

        if pid:
            if pid not in by_id:
                by_id[pid] = row
            else:
                existing = by_id[pid]
                # Keep the highest-citation version if duplicates differ.
                if row["citationCount"] > existing["citationCount"]:
                    by_id[pid] = row
            continue

        if title_key:
            if title_key not in by_title:
                by_title[title_key] = row
            else:
                existing = by_title[title_key]
                if row["citationCount"] > existing["citationCount"]:
                    by_title[title_key] = row

    known_titles = {norm_text(x.get("title", "")).lower() for x in by_id.values()}
    deduped = list(by_id.values()) + [r for k, r in by_title.items() if k not in known_titles]
    return deduped


def knee_index(citations: List[int]) -> int:
    """
    Kneedle-like distance from line connecting first and last points.
    """
    if len(citations) < 3:
        return max(len(citations) - 1, 0)

    x1, y1 = 0, citations[0]
    x2, y2 = len(citations) - 1, citations[-1]
    denom = math.hypot(y2 - y1, x2 - x1) or 1.0

    max_dist = -1.0
    max_i = 0
    for i, y0 in enumerate(citations):
        x0 = i
        dist = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1) / denom
        if dist > max_dist:
            max_dist = dist
            max_i = i
    return max_i


def make_knee_plot(citations: List[int], knee_i: int, out_path: str) -> None:
    xs = list(range(1, len(citations) + 1))
    plt.figure(figsize=(10, 5))
    plt.plot(xs, citations, marker="o", markersize=3, linewidth=1.5, label="Citation count")
    plt.axvline(knee_i + 1, linestyle="--", linewidth=1.5, color="red", label=f"Knee rank: {knee_i + 1}")
    plt.axhline(citations[knee_i], linestyle=":", linewidth=1.5, color="darkred", label=f"Knee cites: {citations[knee_i]}")
    plt.title("Top-100 Citation Curve and Knee Point")
    plt.xlabel("Rank (1=highest citations)")
    plt.ylabel("Citation Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def make_overlap_figure(df: pd.DataFrame, out_path: str) -> None:
    combos = []
    for _, row in df.iterrows():
        flags = []
        if row["group_log_text_inputs"] == 1:
            flags.append("Log")
        if row["group_llm_or_generative"] == 1:
            flags.append("LLM")
        if row["group_early_or_online"] == 1:
            flags.append("Early")
        if row["group_post_failure_or_rca"] == 1:
            flags.append("Post/RCA")
        combos.append(" + ".join(flags) if flags else "None")

    counts = Counter(combos)
    labels = [k for k, _ in counts.most_common()]
    values = [counts[k] for k in labels]

    plt.figure(figsize=(11, 5))
    plt.bar(range(len(labels)), values)
    plt.xticks(range(len(labels)), labels, rotation=30, ha="right")
    plt.ylabel("Paper Count")
    plt.title("4-Group Overlap (Above-Knee Set)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def write_search_log(path: str, query_results: Dict[str, int]) -> None:
    today = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# Search Log",
        "",
        f"- Date run: {today}",
        "- Data source for counts/metadata: OpenAlex API (queried live).",
        "- Target venues in review focus: ICSE, FSE, ASE, TOSEM, EMSE, arXiv where relevant.",
        "- Year filter: 2015+",
        "",
        "## Query Strings",
        "",
    ]
    for q in SEARCH_QUERIES:
        lines.append(f"- `{q}`")
    lines += ["", "## Raw Hits Collected", ""]
    for q, n in query_results.items():
        lines.append(f"- `{q}`: {n}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    ensure_dirs()

    all_rows: List[Dict] = []
    query_results: Dict[str, int] = {}

    for q in SEARCH_QUERIES:
        rows = fetch_papers_for_query(q, limit=120, year_from=2015)
        query_results[q] = len(rows)
        all_rows.extend(rows)

    deduped = dedupe_rows(all_rows)
    df = pd.DataFrame(deduped)
    if df.empty:
        raise RuntimeError("No papers fetched. Check network/API availability.")

    # Keep only plausible SE/CI relevance for the ranked list.
    ranked = df[(df["year"].fillna(0) >= 2015) & (df["relevance_score"] >= 3)].copy()
    if len(ranked) < 100:
        ranked = df[(df["year"].fillna(0) >= 2015) & (df["relevance_score"] >= 2)].copy()
    ranked = ranked[ranked["title"].fillna("").apply(title_has_ci_signal)].copy()
    ranked["false_positive_flag"] = ranked.apply(
        lambda r: is_obvious_false_positive(r.get("title", ""), r.get("abstract", ""), r.get("venue", "")),
        axis=1,
    )
    ranked = ranked[ranked["false_positive_flag"] == False].copy()
    ranked = ranked.sort_values(by=["citationCount", "relevance_score", "year"], ascending=[False, False, False])
    top100 = ranked.head(100).copy()
    top100.insert(0, "rank", list(range(1, len(top100) + 1)))

    citations = top100["citationCount"].tolist()
    knee_i = knee_index(citations)
    knee_cites = citations[knee_i]

    above_knee = top100[top100["citationCount"] >= knee_cites].copy()
    above_knee = above_knee.sort_values(by="citationCount", ascending=False)
    above_knee.insert(0, "above_knee_rank", list(range(1, len(above_knee) + 1)))

    # Build reading matrix classifications.
    matrix = above_knee.copy()
    full_text = (matrix["title"].fillna("") + " " + matrix["abstract"].fillna("") + " " + matrix["venue"].fillna(""))
    matrix["input_artifact"] = full_text.apply(classify_input_artifact)
    matrix["model_family"] = full_text.apply(classify_model_family)
    matrix["task"] = full_text.apply(classify_task)
    matrix["prediction_timing"] = full_text.apply(classify_timing)
    matrix["evaluation_metric"] = full_text.apply(infer_eval_metric)

    # Required overlap groups.
    matrix["group_log_text_inputs"] = matrix["input_artifact"].apply(lambda x: 1 if x == "log_text" else 0)
    matrix["group_llm_or_generative"] = matrix["model_family"].apply(lambda x: 1 if x == "llm_or_generative" else 0)
    matrix["group_early_or_online"] = matrix["prediction_timing"].apply(lambda x: 1 if x in {"early_or_online", "both"} else 0)
    matrix["group_post_failure_or_rca"] = matrix["prediction_timing"].apply(
        lambda x: 1 if x in {"post_failure_or_rca", "both"} else 0
    )
    matrix["code_or_data_link"] = matrix["openAccessPdf"].where(matrix["openAccessPdf"].astype(str) != "", matrix["url"])

    # Persist.
    raw_cols = [
        "source_query",
        "paperId",
        "title",
        "year",
        "venue",
        "citationCount",
        "relevance_score",
        "url",
        "openAccessPdf",
        "publicationTypes",
        "abstract",
    ]
    top_cols = [
        "rank",
        "title",
        "year",
        "venue",
        "citationCount",
        "url",
        "openAccessPdf",
        "source_query",
        "relevance_score",
    ]
    matrix_cols = [
        "above_knee_rank",
        "title",
        "year",
        "venue",
        "citationCount",
        "input_artifact",
        "model_family",
        "task",
        "prediction_timing",
        "evaluation_metric",
        "code_or_data_link",
        "group_log_text_inputs",
        "group_llm_or_generative",
        "group_early_or_online",
        "group_post_failure_or_rca",
    ]

    df[raw_cols].to_csv(os.path.join(DATA_DIR, "papers_raw.csv"), index=False, quoting=csv.QUOTE_MINIMAL)
    top100[top_cols].to_csv(os.path.join(DATA_DIR, "top100_papers.csv"), index=False, quoting=csv.QUOTE_MINIMAL)
    above_knee[top_cols].to_csv(os.path.join(DATA_DIR, "above_knee_set.csv"), index=False, quoting=csv.QUOTE_MINIMAL)
    matrix[matrix_cols].to_csv(os.path.join(DATA_DIR, "reading_matrix.csv"), index=False, quoting=csv.QUOTE_MINIMAL)

    write_search_log(os.path.join(DATA_DIR, "search_log.md"), query_results)

    make_knee_plot(citations, knee_i, os.path.join(FIG_DIR, "knee_plot.png"))
    make_overlap_figure(matrix, os.path.join(FIG_DIR, "overlap_figure.png"))

    summary = {
        "generated_at": dt.datetime.now().isoformat(),
        "raw_rows": int(len(df)),
        "top100_rows": int(len(top100)),
        "knee_rank": int(knee_i + 1),
        "knee_citation_threshold": int(knee_cites),
        "above_knee_rows": int(len(above_knee)),
        "query_results": query_results,
    }
    with open(os.path.join(DATA_DIR, "knee_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
