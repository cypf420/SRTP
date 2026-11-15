"""Build pre-call features and train/dev baselines from saved Phase 3 episodes."""

from __future__ import annotations

import json
import re
import sys
from hashlib import sha256
from pathlib import Path

import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runner.io_utils import load_tools
from runner.schemas import ToolSchema

KEY = ["run_id", "sample_id"]
WORD = re.compile(r"[A-Za-z]+|[\u3400-\u9fff]")
CJK = re.compile(r"[\u3400-\u9fff]")
YEAR = re.compile(r"(?<![A-Za-z0-9-])(?:19|20)\d{2}(?=年|[-/]\d{1,2}[/-]|\b(?!-))")
MONTH_DAY = re.compile(
    r"\d{1,2}\s*月\s*\d{1,2}|\b(?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}\b"
    r"|\b\d{4}-\d{2}-\d{2}\b",
    re.IGNORECASE,
)
IDENTIFIER = re.compile(r"(?<![A-Za-z0-9])[A-Z]{1,8}(?:-\d+|\d+)(?:-\d+)*(?![A-Za-z0-9])")
QUOTED = re.compile(r'''"[^"\n]+"|“[^”\n]+”|‘[^’\n]+’|(?<!\w)'[^'\n]+'(?!\w)''')


def terms(text: str) -> set[str]:
    return {word.lower() for word in WORD.findall(text) if len(word) > 1 or CJK.fullmatch(word)}


def pre_call_features(
    messages: list[dict], tool_names: list[str], registry: dict[str, ToolSchema], tool_terms: dict[str, set[str]]
) -> dict:
    text = next(message["content"] for message in reversed(messages) if message["role"] == "user")
    words = terms(text)
    tools = [registry[name] for name in tool_names]
    scores = {name: len(words & tool_terms[name]) / len(words | tool_terms[name]) for name in tool_names}
    ranked = sorted(scores.values(), reverse=True)
    top = ranked[0]
    second = ranked[1] if len(ranked) > 1 else 0.0
    candidate = next(tool for tool in tools if scores[tool.name] == top) if top > second else None
    required_counts = [len(tool.required) for tool in tools]
    return {
        "utterance_chars": len(text),
        "whitespace_tokens": len(text.split()),
        "cjk_fraction": len(CJK.findall(text)) / max(1, len(text)),
        "digit_groups": len(re.findall(r"\d+", text)),
        "has_year": int(bool(YEAR.search(text))),
        "has_month_day": int(bool(MONTH_DAY.search(text))),
        "quoted_spans": len(QUOTED.findall(text)),
        "has_question_mark": int("?" in text or "？" in text),
        "identifier_mentions": len(IDENTIFIER.findall(text)),
        "tools_available": len(tools),
        "tool_groups_available": len({tool.group for tool in tools}),
        "required_params_mean": sum(required_counts) / len(tools),
        "required_params_max": max(required_counts),
        "candidate_required_params": len(candidate.required) if candidate else None,
        "candidate_optional_params": len(candidate.parameters) - len(candidate.required) if candidate else None,
        "candidate_enum_params": sum(bool(spec.enum) for spec in candidate.parameters.values()) if candidate else None,
        "tool_lexical_top": top,
        "tool_lexical_margin": top - second,
        "tools_with_lexical_overlap": sum(score > 0 for score in scores.values()),
        "exact_tool_name_mentions": sum(bool(re.search(rf"\b{re.escape(name)}\b", text, re.IGNORECASE)) for name in tool_names),
    }


def summarize_baseline(train: pd.DataFrame, dev: pd.DataFrame, columns: list[str]) -> dict:
    y_train = train["main_label"].ne("correct")
    y_dev = dev["main_label"].ne("correct")
    model = make_pipeline(SimpleImputer(strategy="constant", fill_value=-1), StandardScaler(), LogisticRegression())
    model.fit(train[columns], y_train)
    scores = model.predict_proba(dev[columns])[:, 1]
    return {
        "train_rows": len(train),
        "dev_rows": len(dev),
        "dev_errors": int(y_dev.sum()),
        "dev_error_prevalence": float(y_dev.mean()),
        "dev_average_precision": float(average_precision_score(y_dev, scores)),
    }


def main() -> None:
    data = ROOT / "data" / "processed"
    out = ROOT / "outputs" / "midterm"
    labels = pd.read_csv(data / "labels.csv", keep_default_na=False)
    metadata = pd.read_csv(data / "task_metadata.csv", keep_default_na=False)
    registry = {tool.name: tool for tool in load_tools(str(ROOT / "tools" / "tool_schemas_v1.json"))}
    tool_terms = {name: terms(f"{name.replace('_', ' ')} {tool.description}") for name, tool in registry.items()}
    rows = []
    skipped = 0
    with (data / "episodes.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            episode = json.loads(line)
            if episode.get("error") or episode["prediction"].get("parse_error"):
                skipped += 1
                continue
            observed = pre_call_features(episode["messages"], episode["tools"], registry, tool_terms)
            request = json.dumps([episode["messages"], episode["tools"]], sort_keys=True, ensure_ascii=False)
            rows.append({**{column: episode[column] for column in KEY}, **observed,
                         "request_hash": sha256(request.encode("utf-8")).hexdigest()})
    features = pd.DataFrame(rows)
    columns = [column for column in features.columns if column not in [*KEY, "request_hash"]]
    labeled = features.merge(labels, on=KEY, validate="one_to_one")
    if len(features) + skipped != len(labels) or len(labeled) != len(features):
        raise ValueError("Episode and label keys differ")
    table = labeled.merge(
        metadata[["sample_id", "template_family", "language"]], on="sample_id", validate="many_to_one"
    )
    if len(table) != len(labeled):
        raise ValueError("Some episodes lack task metadata")
    splits_per_family = table.loc[table["task_set"].eq("main")].groupby("template_family")["split"].nunique()
    if not splits_per_family.eq(1).all():
        raise ValueError("A main task family spans multiple splits")
    train = table.loc[table["split"].eq("train")]
    dev = table.loc[table["split"].eq("dev")]
    # Families are disjoint, but some templates generate identical requests.
    clean_dev = dev.loc[~dev["request_hash"].isin(train["request_hash"])]
    train_dev = pd.concat([train, dev], ignore_index=True)
    paired = train_dev.assign(correct=train_dev["main_label"].eq("correct")).pivot(
        index=["model_name", "task_id"], columns="variant_name", values="correct"
    ).dropna(subset=["clear", "ambiguous"])
    constant = [column for column in columns if train[column].nunique(dropna=False) <= 1]
    usable = [column for column in columns if column not in constant]
    metrics = {
        "feature_rows": len(table),
        "skipped_request_or_parse_errors": skipped,
        "feature_columns": columns,
        "constant_in_train": constant,
        "missing_train": {column: int(train[column].isna().sum()) for column in columns if train[column].isna().any()},
        "train_unique_candidate_by_language": {
            language: {"unique_candidate": int(group["candidate_required_params"].notna().sum()), "rows": len(group)}
            for language, group in train.groupby("language")
        },
        "dev_rows_matching_a_train_request": len(dev) - len(clean_dev),
        "auto_labels_train_dev": {
            name: group["main_label"].value_counts().to_dict()
            for name, group in train_dev.groupby("model_name")
        },
        "clear_ambiguous_pairs_train_dev": {
            name: {
                "pairs": len(group),
                "clear_only_correct": int(group["clear"].eq(True).mul(group["ambiguous"].eq(False)).sum()),
                "ambiguous_only_correct": int(group["ambiguous"].eq(True).mul(group["clear"].eq(False)).sum()),
            }
            for name, group in paired.groupby(level="model_name")
        },
        "baseline_by_model": {
            name: summarize_baseline(group, clean_dev.loc[clean_dev["model_name"].eq(name)], usable)
            for name, group in train.groupby("model_name")
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    table.to_csv(out / "features.csv", index=False)
    (out / "feature_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
