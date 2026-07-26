from __future__ import annotations

import random
import re
from typing import Any

from es_app.quiz.distractors import pick_definition_distractors
from es_app.schemas.word import Word


def build_synonym_mcq(
    word: Word,
    definition_pool: list[str],
    *,
    rng: random.Random | None = None,
) -> dict[str, Any] | None:
    if not word.definitions or not word.definitions[0].strip():
        return None
    correct = word.definitions[0].strip()
    rng = rng or random.Random()
    distractors = pick_definition_distractors(correct, definition_pool, k=3, rng=rng)
    options = distractors + [correct]
    rng.shuffle(options)
    return {
        "type": "synonym_mcq",
        "word_id": word.id,
        "stem": word.word,
        "options": options,
        "correct_choice": correct,
    }


def build_contextual_blank(
    word: Word,
    *,
    word_pool: list[str] | None = None,
    rng: random.Random | None = None,
) -> dict[str, Any] | None:
    if not word.examples or not word.examples[0].strip():
        return None
    pool = word_pool or []
    example = word.examples[0].strip()
    pattern = re.compile(r"\b" + re.escape(word.word) + r"\b", re.IGNORECASE)
    if not pattern.search(example):
        return None
    stem = pattern.sub("____", example, count=1)
    rng = rng or random.Random()
    distractors = _pick_word_distractors(word.word, pool, k=3, rng=rng)
    options = distractors + [word.word]
    rng.shuffle(options)
    return {
        "type": "contextual_blank",
        "word_id": word.id,
        "stem": stem,
        "options": options,
        "correct_choice": word.word,
    }


def _pick_word_distractors(
    correct: str,
    pool: list[str],
    k: int = 3,
    *,
    rng: random.Random,
) -> list[str]:
    candidates = [w for w in pool if w.lower() != correct.lower()]
    if len(candidates) < k:
        raise ValueError(f"need at least {k} word distractors in pool excluding correct")
    shuffled = candidates[:]
    rng.shuffle(shuffled)
    return shuffled[:k]
