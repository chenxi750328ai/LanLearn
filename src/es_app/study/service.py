from __future__ import annotations

import json
import random
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel

from es_app.errors import AppError
from es_app.lexicon.store import LexiconStore
from es_app.plans.service import PlanService
from es_app.quiz.distractors import pick_definition_distractors
from es_app.schemas.word import Word

_CJK = re.compile(r"[\u4e00-\u9fff]")


class StudyCard(BaseModel):
    word_id: int
    word: str
    correct_definition: str
    options: list[str] | None = None


class StudySession(BaseModel):
    id: str
    plan_id: int
    day_index: int
    mode: Literal["flashcard", "mcq"]
    cards: list[StudyCard]


class AnswerResult(BaseModel):
    correct: bool
    correct_definition: str


def _study_definition(word: Word) -> str:
    for definition in reversed(word.definitions):
        if definition.strip() and _CJK.search(definition):
            return definition.strip()
    if word.definitions:
        return word.definitions[-1].strip()
    raise AppError("word_incomplete", "词条缺少释义", 400)


def _definition_pool(words: list[Word]) -> list[str]:
    return [_study_definition(w) for w in words]


class StudyService:
    def __init__(self, conn: sqlite3.Connection, lexicon: LexiconStore, plans: PlanService):
        self._conn = conn
        self._lexicon = lexicon
        self._plans = plans

    def create_session(
        self,
        *,
        plan_id: int,
        day_index: int,
        mode: Literal["flashcard", "mcq"],
    ) -> StudySession:
        word_ids = self._plans.get_day_word_ids(plan_id, day_index)
        words = [self._lexicon.get_by_id(wid) for wid in word_ids]
        pool = _definition_pool(words)
        rng = random.Random()

        cards: list[StudyCard] = []
        for word in words:
            correct = _study_definition(word)
            options: list[str] | None = None
            if mode == "mcq":
                distractors = pick_definition_distractors(correct, pool, k=3, rng=rng)
                options = distractors + [correct]
                rng.shuffle(options)
            cards.append(
                StudyCard(
                    word_id=word.id,
                    word=word.word,
                    correct_definition=correct,
                    options=options,
                )
            )

        session_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        state = {
            "cards": [c.model_dump() for c in cards],
            "answered": {},
        }
        self._conn.execute(
            """
            INSERT INTO study_sessions (id, plan_id, day_index, mode, state_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, plan_id, day_index, mode, json.dumps(state, ensure_ascii=False), created_at),
        )
        self._conn.commit()
        return StudySession(
            id=session_id,
            plan_id=plan_id,
            day_index=day_index,
            mode=mode,
            cards=cards,
        )

    def answer(self, session_id: str, *, word_id: int, answer: str) -> AnswerResult:
        row = self._conn.execute(
            "SELECT * FROM study_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            raise AppError("session_not_found", "背词会话不存在", 404)

        state = json.loads(row["state_json"])
        cards_by_id = {c["word_id"]: c for c in state["cards"]}
        card = cards_by_id.get(word_id)
        if card is None:
            raise AppError("word_not_in_session", "该词不在本会话中", 400)

        correct_definition = card["correct_definition"]
        normalized = answer.strip()
        is_correct = normalized == correct_definition
        result = AnswerResult(correct=is_correct, correct_definition=correct_definition)

        state["answered"][str(word_id)] = {
            "correct": is_correct,
            "answer": normalized,
        }
        self._conn.execute(
            "UPDATE study_sessions SET state_json = ? WHERE id = ?",
            (json.dumps(state, ensure_ascii=False), session_id),
        )

        created_at = datetime.now(timezone.utc).isoformat()
        payload = {
            "session_id": session_id,
            "mode": row["mode"],
            "correct": is_correct,
            "answer": normalized,
            "plan_id": row["plan_id"],
            "day_index": row["day_index"],
        }
        self._conn.execute(
            """
            INSERT INTO progress_events (kind, word_id, payload_json, created_at)
            VALUES ('study', ?, ?, ?)
            """,
            (word_id, json.dumps(payload, ensure_ascii=False), created_at),
        )
        self._conn.commit()
        return result
