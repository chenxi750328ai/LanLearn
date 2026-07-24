import sqlite3
from pathlib import Path


def get_connection(data_dir: Path) -> sqlite3.Connection:
    data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(data_dir / "es.sqlite3", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS words (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          word TEXT NOT NULL UNIQUE,
          phonetic TEXT,
          audio TEXT,
          definitions_json TEXT NOT NULL DEFAULT '[]',
          examples_json TEXT NOT NULL DEFAULT '[]',
          incomplete INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS plans (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          exam_type TEXT NOT NULL,
          daily_quota INTEGER NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS plan_words (
          plan_id INTEGER NOT NULL,
          word_id INTEGER NOT NULL,
          day_index INTEGER NOT NULL,
          PRIMARY KEY (plan_id, word_id),
          FOREIGN KEY (plan_id) REFERENCES plans(id),
          FOREIGN KEY (word_id) REFERENCES words(id)
        );
        CREATE TABLE IF NOT EXISTS progress_events (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          kind TEXT NOT NULL,
          word_id INTEGER,
          payload_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS study_sessions (
          id TEXT PRIMARY KEY,
          plan_id INTEGER NOT NULL,
          day_index INTEGER NOT NULL,
          mode TEXT NOT NULL,
          state_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS exam_sessions (
          id TEXT PRIMARY KEY,
          plan_id INTEGER NOT NULL,
          questions_json TEXT NOT NULL,
          created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
