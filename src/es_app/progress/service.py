import json
import sqlite3

from pydantic import BaseModel


class ProgressSummary(BaseModel):
    study_answered: int
    study_correct: int
    exam_sessions: int
    weak_word_ids: list[int]


class ProgressService:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get_summary(self) -> ProgressSummary:
        study_rows = self._conn.execute(
            "SELECT word_id, payload_json FROM progress_events WHERE kind = 'study'"
        ).fetchall()

        study_answered = len(study_rows)
        study_correct = 0
        wrong_counts: dict[int, int] = {}

        for row in study_rows:
            payload = json.loads(row["payload_json"])
            if payload.get("correct"):
                study_correct += 1
            else:
                word_id = row["word_id"]
                if word_id is not None:
                    wrong_counts[word_id] = wrong_counts.get(word_id, 0) + 1

        exam_rows = self._conn.execute(
            "SELECT word_id, payload_json FROM progress_events WHERE kind = 'exam'"
        ).fetchall()

        for row in exam_rows:
            payload = json.loads(row["payload_json"])
            if not payload.get("correct"):
                word_id = row["word_id"]
                if word_id is not None:
                    wrong_counts[word_id] = wrong_counts.get(word_id, 0) + 1

        exam_sessions = self._conn.execute(
            "SELECT COUNT(*) AS n FROM exam_sessions"
        ).fetchone()["n"]

        weak_word_ids = sorted(
            wrong_counts,
            key=lambda word_id: (-wrong_counts[word_id], word_id),
        )[:20]

        return ProgressSummary(
            study_answered=study_answered,
            study_correct=study_correct,
            exam_sessions=exam_sessions,
            weak_word_ids=weak_word_ids,
        )
