import random


def pick_definition_distractors(
    correct: str,
    pool: list[str],
    k: int = 3,
    *,
    rng: random.Random | None = None,
) -> list[str]:
    candidates = [d for d in pool if d != correct]
    if len(candidates) < k:
        raise ValueError(f"need at least {k} distractors in pool excluding correct")
    rng = rng or random.Random()
    shuffled = candidates[:]
    rng.shuffle(shuffled)
    return shuffled[:k]
