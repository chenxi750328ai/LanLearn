import random

import pytest

from es_app.quiz.distractors import pick_definition_distractors


def test_pick_excludes_correct_and_returns_k():
    pool = ["放弃", "能力", "缺席", "绝对的", "吸收"]
    correct = "放弃"
    result = pick_definition_distractors(correct, pool, k=3, rng=random.Random(0))
    assert len(result) == 3
    assert correct not in result
    assert all(d in pool for d in result)
    assert len(set(result)) == 3


def test_pick_respects_rng_for_reproducibility():
    pool = ["a", "b", "c", "d", "e"]
    rng = random.Random(42)
    first = pick_definition_distractors("a", pool, k=3, rng=rng)
    rng2 = random.Random(42)
    second = pick_definition_distractors("a", pool, k=3, rng=rng2)
    assert first == second


def test_pick_raises_when_pool_too_small():
    with pytest.raises(ValueError):
        pick_definition_distractors("only", ["only", "other"], k=3)
