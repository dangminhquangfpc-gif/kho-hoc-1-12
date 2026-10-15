import importlib.util
import json
from pathlib import Path
import pytest
from khohoc.ai import AIGrade, AIUnavailable, UnconfiguredProvider

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "pipeline", ROOT / "data/pipelines/import_cli.py"
)
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)


def test_seed_schema_and_duplicate_validation(tmp_path):
    batch = pipeline.validate(ROOT / "data/seeds/questions.json")
    assert len(batch.questions) == 60
    assert {q.grade for q in batch.questions} == {1, 5, 9, 12}
    path = tmp_path / "duplicate.json"
    record = batch.questions[0].model_dump(mode="json")
    path.write_text(json.dumps({"questions": [record, record]}))
    with pytest.raises(ValueError):
        pipeline.validate(path)


def test_csv_round_trip(tmp_path):
    import csv

    q = json.loads((ROOT / "data/seeds/questions.json").read_text())["questions"][0]
    path = tmp_path / "input.csv"
    with path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(q))
        writer.writeheader()
        writer.writerow(
            {k: json.dumps(v) if isinstance(v, list) else v for k, v in q.items()}
        )
    assert pipeline.validate(path).questions[0].id == q["id"]


def test_ai_failure_and_provisional_bounds():
    import asyncio

    with pytest.raises(AIUnavailable):
        asyncio.run(UnconfiguredProvider().grade_essay())
    with pytest.raises(ValueError):
        AIGrade(
            score=11, max_score=10, feedback="x", confidence=0.8, model_version="test"
        )
    with pytest.raises(ValueError):
        AIGrade(
            score=5,
            max_score=10,
            feedback="x",
            confidence=0.8,
            model_version="test",
            grading_status="official",
        )
