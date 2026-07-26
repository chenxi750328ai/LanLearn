from pydantic import BaseModel, Field


class WordCandidate(BaseModel):
    word: str
    phonetic: str | None = None
    audio: str | None = None
    definitions: list[str] = Field(default_factory=list)
    examples: list[str] = Field(default_factory=list)


class Word(WordCandidate):
    id: int
    incomplete: bool


def compute_incomplete(definitions: list[str]) -> bool:
    return len([d for d in definitions if d.strip()]) == 0
