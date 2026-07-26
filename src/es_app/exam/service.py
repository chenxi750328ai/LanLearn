from __future__ import annotations

import json
import random
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel

from es_app.errors import AppError
from es_app.exam.templates import build_contextual_blank, build_synonym_mcq
from es_app.lexicon.store import LexiconStore
from es_app.plans.service import PlanService


class ExamQuestion(BaseModel):
    id: str
    type: Literal["synonym_mcq", "contextual_blank"]
    word_id: int
    stem: str
    options: list[str]


class ExamSession(BaseModel):
    id: str
    plan_id: int
    questions: list[ExamQuestion]


class ExamReport(BaseModel):
    score: int
    total: int
    wrong_word_ids: list[int]


class ExamService:
    def __init__(self, conn: sqlite3.Connection, lexicon: LexiconStore, plans: PlanService):
        self._conn = conn
        self._lexicon = lexicon
        self._plans = plans

    def create_session(self, *, plan_id: int, question_count: int) -> ExamSession:
        if question_count < 1:
            raise AppError("invalid_question_count", "题目数量至少为 1", 400)

        plan = self._plans.get_plan(plan_id)
        words = [self._lexicon.get_by_id(wid) for day in plan.days for wid in day.word_ids]
        words = [w for w in words if not w.incomplete]
        if not words:
            raise AppError("no_words", "计划中没有可用词条", 400)

        definition_pool = [w.definitions[0] for w in words if w.definitions]
        word_pool = [w.word for w in words]
        contextual_words = [w for w in words if w.examples and w.examples[0].strip()]

        can_synonym = len(definition_pool) >= 4
        can_contextual = len(contextual_words) >= 1 and len(word_pool) >= 4
        syn_target, ctx_target = _allocate_counts(
            question_count,
            synonym_available=can_synonym,
            contextual_available=can_contextual,
        )

        rng = random.Random()
        stored: list[dict] = []
        used_ids: set[int] = set()

        def append_question(built: dict | None) -> bool:
            if built is None:
                return False
            built["id"] = str(uuid.uuid4())
            stored.append(built)
            used_ids.add(built["word_id"])
            return True

        syn_order = words[:]
        rng.shuffle(syn_order)
        for word in syn_order:
            if sum(1 for q in stored if q["type"] == "synonym_mcq") >= syn_target:
                break
            if word.id in used_ids or not can_synonym:
                continue
            append_question(build_synonym_mcq(word, definition_pool, rng=rng))

        ctx_order = contextual_words[:]
        rng.shuffle(ctx_order)
        for word in ctx_order:
            if sum(1 for q in stored if q["type"] == "contextual_blank") >= ctx_target:
                break
            if word.id in used_ids or not can_contextual:
                continue
            append_question(build_contextual_blank(word, word_pool=word_pool, rng=rng))

        if len(stored) < question_count:
            fill_order = words[:]
            rng.shuffle(fill_order)
            for word in fill_order:
                if len(stored) >= question_count:
                    break
                if word.id in used_ids:
                    continue
                built = None
                if can_contextual and word.examples and word.examples[0].strip():
                    built = build_contextual_blank(word, word_pool=word_pool, rng=rng)
                if built is None and can_synonym and word.definitions:
                    built = build_synonym_mcq(word, definition_pool, rng=rng)
                append_question(built)

        if not stored:
            raise AppError("cannot_build_exam", "无法生成测验题目", 400)

        session_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            """
            INSERT INTO exam_sessions (id, plan_id, questions_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, plan_id, json.dumps(stored, ensure_ascii=False), created_at),
        )
        self._conn.commit()

        questions = [
            ExamQuestion(
                id=q["id"],
                type=q["type"],
                word_id=q["word_id"],
                stem=q["stem"],
                options=q["options"],
            )
            for q in stored
        ]
        return ExamSession(id=session_id, plan_id=plan_id, questions=questions)

    def submit(self, session_id: str, *, answers: list[dict]) -> ExamReport:
        row = self._conn.execute(
            "SELECT * FROM exam_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            raise AppError("session_not_found", "测验会话不存在", 404)

        questions = json.loads(row["questions_json"])
        by_id = {q["id"]: q for q in questions}
        total = len(questions)
        score = 0
        wrong_word_ids: list[int] = []
        created_at = datetime.now(timezone.utc).isoformat()

        for item in answers:
            qid = item["question_id"]
            choice = item["choice"].strip()
            q = by_id.get(qid)
            if q is None:
                raise AppError("question_not_found", "题目不存在", 400)
            is_correct = choice == q["correct_choice"]
            if is_correct:
                score += 1
            else:
                wrong_word_ids.append(q["word_id"])
            payload = {
                "session_id": session_id,
                "question_id": qid,
                "type": q["type"],
                "correct": is_correct,
                "choice": choice,
                "plan_id": row["plan_id"],
            }
            self._conn.execute(
                """
                INSERT INTO progress_events (kind, word_id, payload_json, created_at)
                VALUES ('exam', ?, ?, ?)
                """,
                (q["word_id"], json.dumps(payload, ensure_ascii=False), created_at),
            )

        self._conn.commit()
        return ExamReport(score=score, total=total, wrong_word_ids=wrong_word_ids)


def _allocate_counts(
    question_count: int,
    *,
    synonym_available: bool,
    contextual_available: bool,
) -> tuple[int, int]:
    if question_count >= 2 and synonym_available and contextual_available:
        syn = 1
        ctx = 1
        remaining = question_count - 2
        for i in range(remaining):
            if i % 2 == 0:
                syn += 1
            else:
                ctx += 1
        return syn, ctx
    if synonym_available and not contextual_available:
        return question_count, 0
    if contextual_available and not synonym_available:
        return 0, question_count
    if synonym_available:
        return question_count, 0
    return 0, question_count
