#!/usr/bin/env python3
"""Evaluate skill routing against a small regression set.

Each line in evals/routing-cases.jsonl is:
  {"query": "...", "skill": "archify", "decision": "inject"}

`decision` is optional. The script reports Hit@1, MRR, inject precision,
false-positive rate, and decision accuracy.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "bin" / "ajia"
CASES = ROOT / "evals" / "routing-cases.jsonl"


def load_cases() -> list[dict[str, str]]:
    cases: list[dict[str, str]] = []
    for lineno, line in enumerate(CASES.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{CASES}:{lineno}: {exc}") from exc
        if not item.get("query") or not item.get("skill"):
            raise SystemExit(f"{CASES}:{lineno}: query and skill are required")
        cases.append(item)
    return cases


def route(query: str, host: str | None) -> dict:
    cmd = [sys.executable, str(BIN), "route", query, "--json", "--no-body"]
    if host:
        cmd.extend(["--host", host])
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        return {"decision": "error", "selected": None, "candidates": [], "error": proc.stderr.strip()}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"decision": "error", "selected": None, "candidates": [], "error": proc.stdout.strip()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    cases = load_cases()
    rows: list[dict] = []
    hits = 0
    reciprocal = 0.0
    inject_count = 0
    inject_correct = 0
    none_expected = 0
    none_correct = 0

    for case in cases:
        expected = case["skill"]
        result = route(case["query"], args.host or None)
        selected = result.get("selected") or {}
        selected_name = selected.get("name") or ""
        selected_id = selected.get("id") or ""
        candidates = result.get("candidates") or []
        rank = 0
        for index, candidate in enumerate(candidates, 1):
            if expected in {candidate.get("name"), candidate.get("id")}:
                rank = index
                break
        hit = 1 if expected in {selected_name, selected_id} else 0
        hits += hit
        if rank:
            reciprocal += 1.0 / rank
        decision = result.get("decision", "error")
        if expected == "none":
            none_expected += 1
            if decision == "none":
                none_correct += 1
        elif decision in {"inject", "native"}:
            inject_count += 1
            inject_correct += hit
        rows.append(
            {
                "query": case["query"],
                "expected": expected,
                "selected": selected_name,
                "decision": decision,
                "hit": hit,
                "rank": rank,
                "confidence": result.get("confidence"),
                "margin": result.get("margin"),
                "error": result.get("error"),
            }
        )

    total = len(rows)
    summary = {
        "cases": total,
        "hit_at_1": round(hits / total, 3) if total else 0.0,
        "mrr": round(reciprocal / total, 3) if total else 0.0,
        "inject_precision": round(inject_correct / inject_count, 3) if inject_count else 0.0,
        "false_positive_rate": round((inject_count - inject_correct) / inject_count, 3) if inject_count else 0.0,
        "none_accuracy": round(none_correct / none_expected, 3) if none_expected else 1.0,
    }

    if args.json:
        print(json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False))
    else:
        if args.verbose:
            print(f"{'result':8} {'expected':24} {'selected':24} {'decision':9} query")
            for row in rows:
                flag = "ok" if row["hit"] else "MISS"
                print(
                    f"{flag:8} {row['expected'][:24]:24} "
                    f"{(row['selected'] or '-')[:24]:24} {row['decision']:9} {row['query']}"
                )
        print(json.dumps(summary, indent=2))
    return 0 if hits == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
