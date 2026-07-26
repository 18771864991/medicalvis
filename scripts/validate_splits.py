#!/usr/bin/env python3
"""Validate that the public MedicalVis-35K splits are SQL-disjoint."""

from __future__ import annotations

import gzip
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPLIT_DIR = ROOT / "data" / "splits"


def norm(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().lower())


def data_signature(row: dict) -> str:
    data_part = row["vis_query"].get("data_part") or {}
    return norm(data_part.get("sql_part", ""))


def load_jsonl_gz(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def main() -> None:
    splits = {name: load_jsonl_gz(SPLIT_DIR / f"{name}.jsonl.gz") for name in ["train", "dev", "test"]}
    signatures = {name: {data_signature(row) for row in rows} for name, rows in splits.items()}

    ok = True
    for a, b in [("train", "dev"), ("train", "test"), ("dev", "test")]:
        overlap = signatures[a] & signatures[b]
        print(f"{a}/{b} SQL signature overlap: {len(overlap)}")
        ok = ok and not overlap

    total_rows = sum(len(rows) for rows in splits.values())
    total_nlq = sum(len(row.get("NLQs", [])) for rows in splits.values() for row in rows)
    print(f"visualization queries: {total_rows}")
    print(f"natural-language questions: {total_nlq}")

    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
