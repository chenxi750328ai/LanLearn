from datetime import datetime, timezone
import sqlite3

from pydantic import BaseModel

from es_app.errors import AppError
from es_app.lexicon.store import LexiconStore


class PlanDay(BaseModel):
    day_index: int
    word_ids: list[int]


class Plan(BaseModel):
    id: int
    exam_type: str
    daily_quota: int
    days: list[PlanDay]


class PlanService:
    def __init__(self, conn: sqlite3.Connection, lexicon: LexiconStore):
        self._conn = conn
        self._lexicon = lexicon

    def create_plan(self, *, exam_type: str, daily_quota: int) -> Plan:
        words = self._lexicon.list_words(complete_only=True)
        if not words:
            raise AppError("empty_lexicon", "请先加载词库", 400)

        created_at = datetime.now(timezone.utc).isoformat()
        cur = self._conn.execute(
            "INSERT INTO plans (exam_type, daily_quota, created_at) VALUES (?, ?, ?)",
            (exam_type, daily_quota, created_at),
        )
        plan_id = int(cur.lastrowid)

        word_ids = [w.id for w in words]
        days: list[PlanDay] = []
        for i in range(0, len(word_ids), daily_quota):
            chunk = word_ids[i : i + daily_quota]
            day_index = i // daily_quota
            days.append(PlanDay(day_index=day_index, word_ids=chunk))
            for word_id in chunk:
                self._conn.execute(
                    "INSERT INTO plan_words (plan_id, word_id, day_index) VALUES (?, ?, ?)",
                    (plan_id, word_id, day_index),
                )
        self._conn.commit()
        return Plan(id=plan_id, exam_type=exam_type, daily_quota=daily_quota, days=days)

    def get_plan(self, plan_id: int) -> Plan:
        row = self._conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()
        if row is None:
            raise AppError("plan_not_found", "计划不存在", 404)

        rows = self._conn.execute(
            """
            SELECT word_id, day_index FROM plan_words
            WHERE plan_id = ?
            ORDER BY day_index, word_id
            """,
            (plan_id,),
        ).fetchall()

        days_map: dict[int, list[int]] = {}
        for r in rows:
            days_map.setdefault(r["day_index"], []).append(r["word_id"])

        days = [PlanDay(day_index=di, word_ids=ids) for di, ids in sorted(days_map.items())]
        return Plan(
            id=row["id"],
            exam_type=row["exam_type"],
            daily_quota=row["daily_quota"],
            days=days,
        )
