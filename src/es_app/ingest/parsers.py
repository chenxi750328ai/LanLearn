import csv
import io

from es_app.schemas.word import WordCandidate


def _split_semicolon(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(";") if part.strip()]


def _optional_field(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def parse_csv(text: str) -> tuple[list[WordCandidate], list[dict]]:
    reader = csv.DictReader(io.StringIO(text))
    candidates: list[WordCandidate] = []
    failures: list[dict] = []

    for line_no, row in enumerate(reader, start=2):
        word = (row.get("word") or "").strip()
        if not word:
            failures.append({"line": line_no, "reason": "empty word", "row": dict(row)})
            continue

        candidates.append(
            WordCandidate(
                word=word,
                phonetic=_optional_field(row.get("phonetic")),
                audio=_optional_field(row.get("audio")),
                definitions=_split_semicolon(row.get("definitions")),
                examples=_split_semicolon(row.get("examples")),
            )
        )

    return candidates, failures


def parse_txt(text: str) -> tuple[list[WordCandidate], list[dict]]:
    candidates: list[WordCandidate] = []
    failures: list[dict] = []

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        if "|" in line:
            word_part, definition_part = line.split("|", 1)
            word = word_part.strip()
            definitions = [definition_part.strip()] if definition_part.strip() else []
        else:
            word = line
            definitions = []

        if not word:
            failures.append({"line": line_no, "reason": "empty word", "row": raw})
            continue

        candidates.append(WordCandidate(word=word, definitions=definitions))

    return candidates, failures
