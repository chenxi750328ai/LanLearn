import json
import sqlite3
from es_app.schemas.word import Word, WordCandidate, compute_incomplete


class LexiconStore:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def add_from_candidate(self, candidate: WordCandidate) -> Word:
        incomplete = compute_incomplete(candidate.definitions)
        cur = self._conn.execute(
            """
            INSERT INTO words (word, phonetic, audio, definitions_json, examples_json, incomplete)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                candidate.word.strip(),
                candidate.phonetic,
                candidate.audio,
                json.dumps(candidate.definitions, ensure_ascii=False),
                json.dumps(candidate.examples, ensure_ascii=False),
                1 if incomplete else 0,
            ),
        )
        self._conn.commit()
        return self.get_by_id(int(cur.lastrowid))

    def get_by_id(self, word_id: int) -> Word:
        row = self._conn.execute("SELECT * FROM words WHERE id = ?", (word_id,)).fetchone()
        return self._row_to_word(row)

    def get_by_word(self, word: str) -> Word | None:
        row = self._conn.execute("SELECT * FROM words WHERE word = ?", (word,)).fetchone()
        return self._row_to_word(row) if row else None

    def list_words(self, *, complete_only: bool = False) -> list[Word]:
        sql = "SELECT * FROM words"
        if complete_only:
            sql += " WHERE incomplete = 0"
        sql += " ORDER BY id"
        return [self._row_to_word(r) for r in self._conn.execute(sql).fetchall()]

    @staticmethod
    def _row_to_word(row: sqlite3.Row) -> Word:
        return Word(
            id=row["id"],
            word=row["word"],
            phonetic=row["phonetic"],
            audio=row["audio"],
            definitions=json.loads(row["definitions_json"]),
            examples=json.loads(row["examples_json"]),
            incomplete=bool(row["incomplete"]),
        )
