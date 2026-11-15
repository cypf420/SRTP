"""Compare current labels with saved historical evaluations of the same episodes."""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.io_utils import write_json


def main() -> None:
    raw = ROOT / "data" / "raw_runs"
    previous = {}
    for path in sorted(raw.glob("*/episodes_eval_*.jsonl")):
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                key = row["run_id"], row["sample_id"]
                if key in previous:
                    raise ValueError(f"Duplicate historical evaluation: {key}")
                previous[key] = row["eval"]

    with (ROOT / "data" / "processed" / "labels.csv").open(encoding="utf-8", newline="") as handle:
        current = {(r["run_id"], r["sample_id"]): r for r in csv.DictReader(handle)}
    if not previous or not previous.keys() <= current.keys():
        raise ValueError("Historical evaluations are missing or lack current labels")

    paired = []
    for (run_id, sample_id), old in previous.items():
        new = current[run_id, sample_id]
        paired.append({"run_id": run_id, "sample_id": sample_id, "split": new["split"], "model": new["model_name"],
                       "old_main_label": old["main_label"], "new_main_label": new["main_label"],
                       "old_sublabels": json.dumps(old["sublabels"], ensure_ascii=False), "new_sublabels": new["sublabels"]})

    stats = {}
    for scope, rows in (("all_main", paired), ("train_dev", [r for r in paired if r["split"] in {"train", "dev"}])):
        stats[scope] = {}
        for model in sorted({r["model"] for r in rows}):
            records = [r for r in rows if r["model"] == model]
            counts = {}
            for period in ("old", "new"):
                counts[period] = {
                    "main_labels": dict(Counter(r[f"{period}_main_label"] for r in records)),
                    "sublabels": dict(Counter(label for r in records for label in json.loads(r[f"{period}_sublabels"]))),
                }
            counts["changed_main_labels"] = sum(r["old_main_label"] != r["new_main_label"] for r in records)
            counts["rows"] = len(records)
            stats[scope][model] = counts

    out = ROOT / "outputs" / "midterm"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "label_comparison.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    write_json(out / "label_comparison_summary.json", stats)
    print(f"Compared {len(paired)} historical and current labels")


if __name__ == "__main__":
    main()
