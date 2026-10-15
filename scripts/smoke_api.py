"""End-to-end HTTP check against an already running API and published local fixtures."""

import argparse
import httpx

parser = argparse.ArgumentParser()
parser.add_argument("--api", default="http://127.0.0.1:8000")
args = parser.parse_args()

with httpx.Client(base_url=args.api, timeout=30) as client:
    assert client.get("/health").raise_for_status().json()["status"] == "ok"
    assert len(client.get("/grades").raise_for_status().json()) == 12
    exams = (
        client.get("/exams", params={"grade": 1, "subject": "toan"})
        .raise_for_status()
        .json()
    )
    assert exams, "Publish local authored fixtures before smoke test"
    exam = client.get("/exams/" + exams[0]["id"]).raise_for_status().json()
    assert "correct_answer" not in str(exam) and "explanation" not in str(exam)
    attempt = (
        client.post("/exams/" + exam["id"] + "/attempts").raise_for_status().json()
    )
    headers = {"X-Attempt-Token": attempt["token"]}
    path = "/attempts/" + attempt["id"]
    assert client.get(path + "/result", headers=headers).status_code == 409
    result = (
        client.post(
            path + "/submit",
            json={"answers": {exam["questions"][0]["id"]: ["A"]}},
            headers=headers,
        )
        .raise_for_status()
        .json()
    )
    assert result["score"] == 1 and result["max_score"] == 13
    assert result["details"][0]["explanation"]
    assert (
        client.post(
            path + "/submit",
            json={"answers": {exam["questions"][0]["id"]: ["A"]}},
            headers=headers,
        )
        .raise_for_status()
        .json()
        == result
    )
    assert client.get(path + "/result").status_code == 404
    client.delete(path, headers=headers).raise_for_status()
print("PASS: live HTTP grade → subject → exam → submit → result → delete")
