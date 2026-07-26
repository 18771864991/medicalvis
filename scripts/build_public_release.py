#!/usr/bin/env python3
"""Build the public MedicalVis-35K dataset release from the local v5 files."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import random
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT.parents[1]
SOURCE_SPLIT = SOURCE_ROOT / "data_medicalvis" / "v5" / "split"
SOURCE_SCHEMA = SOURCE_ROOT / "data_medicalvis" / "schema"
SOURCE_VIS = SOURCE_ROOT / "data_medicalvis" / "v5" / "VIS"
OUT_DATA = ROOT / "data"
OUT_SPLIT = OUT_DATA / "splits" / "sql_disjoint"
OUT_SCHEMA = OUT_DATA / "schema"
OUT_EXAMPLES = ROOT / "examples"

SOURCE_FILES = {
    "legacy_train": "MedicalVis_train.json",
    "legacy_dev": "MedicalVis_dev.json",
    "legacy_test": "MedicalVis_test.json",
}

EXAMPLE_SOURCE_IDS = [
    ("legacy_train", "2104"),
    ("legacy_train", "26"),
    ("legacy_train", "61"),
    ("legacy_train", "25"),
    ("legacy_train", "2193"),
    ("legacy_train", "241"),
    ("legacy_train", "353"),
    ("legacy_train", "5741"),
]


def norm(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def data_signature(example: dict) -> str:
    data_part = example["vis_query"].get("data_part") or {}
    return norm(data_part.get("sql_part", ""))


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl_gz(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=6) as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_source() -> list[dict]:
    rows = []
    next_id = 1
    for source_split, filename in SOURCE_FILES.items():
        data = json.loads((SOURCE_SPLIT / filename).read_text(encoding="utf-8"))
        for source_id, example in data.items():
            row = dict(example)
            vis_obj = dict(row.get("vis_obj") or {})
            vis_obj.pop("x_data", None)
            vis_obj.pop("y_data", None)
            row["vis_obj"] = vis_obj
            row["id"] = f"MV{next_id:05d}"
            row["metadata"] = {
                "source_split": source_split,
                "source_id": source_id,
                "chart_type": row.get("vis_obj", {}).get("chart"),
                "hardness": row.get("vis_query", {}).get("hardness"),
                "sql_signature_sha1": hashlib.sha1(data_signature(row).encode("utf-8")).hexdigest(),
            }
            rows.append(row)
            next_id += 1
    return rows


def assign_sql_disjoint_splits(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[data_signature(row)].append(row)

    rng = random.Random(20260727)
    grouped = list(groups.values())
    rng.shuffle(grouped)
    grouped.sort(key=lambda g: (-len(g), hashlib.sha1(data_signature(g[0]).encode()).hexdigest()))

    targets = {
        "train": int(round(len(rows) * 0.80)),
        "dev": int(round(len(rows) * 0.10)),
        "test": len(rows) - int(round(len(rows) * 0.80)) - int(round(len(rows) * 0.10)),
    }
    splits = {"train": [], "dev": [], "test": []}

    for group in grouped:
        split = min(splits, key=lambda name: len(splits[name]) / targets[name])
        splits[split].extend(group)

    for split_rows in splits.values():
        split_rows.sort(key=lambda r: r["id"])
    return splits


def leakage_report(splits: dict[str, list[dict]]) -> dict:
    signature_sets = {name: {data_signature(row) for row in rows} for name, rows in splits.items()}
    pair_overlap = {}
    for a, b in [("train", "dev"), ("train", "test"), ("dev", "test")]:
        pair_overlap[f"{a}_{b}"] = len(signature_sets[a] & signature_sets[b])
    return {
        "split_protocol": "sql_disjoint_v1",
        "group_key": "normalized vis_query.data_part.sql_part",
        "cross_split_sql_signature_overlap": pair_overlap,
        "is_sql_disjoint": all(v == 0 for v in pair_overlap.values()),
    }


def stats(rows: list[dict], splits: dict[str, list[dict]]) -> dict:
    def summarize(subset: list[dict]) -> dict:
        return {
            "visualization_queries": len(subset),
            "nl_questions": sum(len(row.get("NLQs", [])) for row in subset),
            "chart_types": dict(Counter(row["metadata"]["chart_type"] for row in subset)),
            "hardness": dict(Counter(row["metadata"]["hardness"] for row in subset)),
            "sql_signature_groups": len({data_signature(row) for row in subset}),
        }

    return {
        "dataset": "MedicalVis-35K",
        "version": "1.0.0",
        "total": summarize(rows),
        "splits": {name: summarize(split_rows) for name, split_rows in splits.items()},
        "leakage_audit": leakage_report(splits),
    }


def write_question_csv(splits: dict[str, list[dict]]) -> None:
    path = OUT_DATA / "medicalvis_35k_questions.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "split",
                "id",
                "question_index",
                "question",
                "chart_type",
                "hardness",
                "sql",
            ],
        )
        writer.writeheader()
        for split, rows in splits.items():
            for row in rows:
                sql = row["vis_query"]["data_part"]["sql_part"]
                for idx, question in enumerate(row.get("NLQs", []), start=1):
                    writer.writerow(
                        {
                            "split": split,
                            "id": row["id"],
                            "question_index": idx,
                            "question": question,
                            "chart_type": row["metadata"]["chart_type"],
                            "hardness": row["metadata"]["hardness"],
                            "sql": sql,
                        }
                    )


def copy_schema() -> None:
    OUT_SCHEMA.mkdir(parents=True, exist_ok=True)
    for name in [
        "tables.json",
        "db_tables_columns.json",
        "db_tables_columns_types.json",
        "database_information.csv",
    ]:
        shutil.copy2(SOURCE_SCHEMA / name, OUT_SCHEMA / name)


def write_examples(rows: list[dict]) -> None:
    by_source = {(row["metadata"]["source_split"], row["metadata"]["source_id"]): row for row in rows}
    examples = []
    html_dir = OUT_EXAMPLES / "html"
    html_dir.mkdir(parents=True, exist_ok=True)
    for source_ref in EXAMPLE_SOURCE_IDS:
        row = by_source[source_ref]
        examples.append(
            {
                "id": row["id"],
                "chart_type": row["metadata"]["chart_type"],
                "hardness": row["metadata"]["hardness"],
                "natural_language": row.get("NLQs", [None])[0],
                "dvq": row["vis_query"]["DVQ"],
                "sql": row["vis_query"]["data_part"]["sql_part"],
                "html": f"html/VIS_{source_ref[1]}.html",
            }
        )
        src_html = SOURCE_VIS / f"VIS_{source_ref[1]}.html"
        if src_html.exists():
            shutil.copy2(src_html, html_dir / src_html.name)
    write_json(OUT_EXAMPLES / "representative_examples.json", examples)


def write_manifest(rows: list[dict], splits: dict[str, list[dict]], stats_obj: dict) -> None:
    files = [
        OUT_DATA / "medicalvis_35k.jsonl.gz",
        OUT_DATA / "medicalvis_35k_questions.csv",
        OUT_SPLIT / "train.jsonl.gz",
        OUT_SPLIT / "dev.jsonl.gz",
        OUT_SPLIT / "test.jsonl.gz",
    ]
    manifest = {
        "dataset": "MedicalVis-35K",
        "version": "1.0.0",
        "release_type": "public_dataset_only",
        "records": stats_obj,
        "files": {
            str(path.relative_to(ROOT)): {
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
            for path in files
        },
        "notes": [
            "The canonical split is SQL-disjoint and should be used for evaluation.",
            "Legacy random/internal splits are not included in this public release.",
            "Raw MIMIC database files are not redistributed in this repository.",
            "Full-dataset executed query results are not redistributed; eight representative HTML renderings are included as limited public examples.",
        ],
    }
    write_json(OUT_DATA / "manifest.json", manifest)


def main() -> None:
    for path in [OUT_DATA, OUT_EXAMPLES]:
        path.mkdir(parents=True, exist_ok=True)

    rows = load_source()
    splits = assign_sql_disjoint_splits(rows)
    stats_obj = stats(rows, splits)

    write_jsonl_gz(OUT_DATA / "medicalvis_35k.jsonl.gz", rows)
    for name, split_rows in splits.items():
        write_jsonl_gz(OUT_SPLIT / f"{name}.jsonl.gz", split_rows)
    write_json(OUT_SPLIT / "leakage_audit.json", leakage_report(splits))
    write_question_csv(splits)
    write_examples(rows)
    copy_schema()
    write_manifest(rows, splits, stats_obj)


if __name__ == "__main__":
    main()
