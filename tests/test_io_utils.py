from pathlib import Path

from runner.io_utils import append_jsonl, load_jsonl_sample_ids


def test_load_jsonl_sample_ids_reads_valid_rows(tmp_path: Path) -> None:
    target = tmp_path / "episodes.jsonl"
    append_jsonl(target, {"sample_id": "task_001__clear"})
    append_jsonl(target, {"sample_id": "task_002__clear"})

    sample_ids = load_jsonl_sample_ids(target)

    assert sample_ids == {"task_001__clear", "task_002__clear"}


def test_load_jsonl_sample_ids_ignores_truncated_line(tmp_path: Path) -> None:
    target = tmp_path / "episodes.jsonl"
    target.write_text('{"sample_id":"task_001__clear"}\n{"sample_id":"broken"\n', encoding="utf-8")

    sample_ids = load_jsonl_sample_ids(target)

    assert sample_ids == {"task_001__clear"}
