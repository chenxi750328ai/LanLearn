# TOEFL MVP（架构地基 + 垂直切片）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在空仓库落地 OpenSpec 管理下的模块化 FastAPI 单体，打通托福计划 → 词库（内置/文件/OCR）→ 背词 → 两种托福词汇题型模考 → 进度汇总，并用最小 Web UI 在本机浏览器验收。

**Architecture:** FastAPI 模块化单体（`plans` / `lexicon` / `ingest` / `study` / `exam` / `progress` / `quiz` + `adapters/`）；UI 挂 `/ui`，API 无前缀；Tesseract OCR 经 threadpool；study/exam 会话持久化在 SQLite；默认在 **WSL** 跑 API 并复用已有 Ollama；手机外网经 **Tailscale** 访问（禁止公网裸端口）；本计划只留 `/speech/evaluate` 503 桩。

**Tech Stack:** Python 3.11+、FastAPI、Uvicorn、Pydantic v2、SQLite（stdlib `sqlite3`）、httpx（测试）、pytest、Tesseract（系统依赖，测试用 Fake）、静态 Web（`static/` 无构建步）、Tailscale（外网组网，非代码依赖）

## Global Constraints

- Ollama：只连 WSL 已有实例（`OLLAMA_HOST`），禁止默认再装 Windows 原生重复实例
- **默认运行位置：** FastAPI/uvicorn 在 **WSL** 内启动；Windows 浏览器经 `localhost` 访问；Windows 原生跑 API 仅为可选附录
- **监听：** 默认 `ES_BIND=127.0.0.1`；Tailscale 联调时可设 `ES_BIND=0.0.0.0`（仍无鉴权，仅信任 Tailnet ACL）
- **外网手机：** 使用 **Tailscale**（或同类私有组网）；**禁止**路由器端口转发裸出无鉴权 API；**不做**云上托管 API（本计划）
- 单用户本机；无账号；数据根目录可配置（`ES_DATA_DIR`）
- 词库字段：`word`（必填）、`phonetic`、`audio`、`definitions: list[str]`、`examples: list[str]`
- 未确认的 `WordCandidate` 不得进入学习池 / 默认不得入 exam 组卷
- study/exam **会话状态存 SQLite**（进程重启可续）
- 无 Ollama 时背词与考试必须可用；依赖 Ollama 的接口返回 503
- 特性用 OpenSpec 管理；Git 分支与 OpenSpec change 对齐（见下节）
- 本计划 **不含** 完整发音评测实现与华为客户端（另开计划）：`docs/superpowers/plans/` 后续 `2026-07-24-pronunciation.md`、`2026-07-24-huawei-client-skeleton.md`
- 不做：SRS、爬词、云同步、多用户账号、完整托福听说套题、公网裸暴露、CI/CD 发布流水线（显式后置）

---

## Git Branch Strategy

功能全集保留；用顺序特性枝拆 PR（gstack eng review 决议 **B+A**）。

```text
master                         # 仅合并后的可运行快照；禁止长期直接堆 MVP 大 commit
  └─ feat/arch-foundation      # OpenSpec arch-foundation + 包骨架/Schema/Adapter/speech 桩
       └─ feat/toefl-core      # plans + lexicon seed + study + exam + progress + /ui
            └─ feat/ingest-ocr # 文件导入 + Tesseract OCR（仍属本计划，第二/三 PR）
  ∥ feat/pronunciation         # 后续计划；自 foundation+core 切出
  ∥ feat/huawei-client-skeleton
```

### Git 操作约定（执行本计划时必须遵守）

1. **开写前**（Task 0）：`git checkout master && git checkout -b feat/arch-foundation`
2. **每任务结束**：按任务内 `git add <显式路径>` + `git commit`（禁止 `git add -A`；禁止 `--no-verify`）
3. **分支完成**：在 WSL/本机跑 `pytest -v` 全绿后合并：
   - 有远程：`git push -u origin HEAD` → `gh pr create` → 评审通过后 merge
   - 无远程（当前）：`git checkout master && git merge --no-ff feat/arch-foundation`
4. **晋升下一枝**：`git checkout -b feat/toefl-core`（基于已合并的 master）
5. **ingest 同理** 切 `feat/ingest-ocr`
6. **禁止** 在 `master` 上直接实现 Task 2–12；**禁止** force-push `master`
7. commit message 风格：`feat:` / `fix:` / `docs:` / `test:` / `chore:` 前缀，英文或中文短句说明动机

### 任务 ↔ 分支映射

| 任务 | 分支 |
|------|------|
| Task 0–2, speech 桩骨架, OpenSpec foundation | `feat/arch-foundation` |
| Task 3–5, 8–12（含 UI；不含 ingest 文件/OCR） | `feat/toefl-core` |
| Task 6–7 | `feat/ingest-ocr` |
| Task 13 | 当前收尾枝或 master 上的 docs commit |

> 若执行时 Task 4 的 lexicon 路由需在 core 才挂载，foundation 只留 Schema/store/协议；以「每枝可独立 pytest 子集绿」为准微调，但不得把 ingest 塞进 foundation。

---

## GSTACK Tooling（执行与门禁）

本仓库已用 brainstorming + writing-plans；实现阶段强制使用下列 gstack / 相关技能（Cursor skills 路径 `~/.cursor/skills/gstack-*` 或用户配置的等价命令）。

| 时机 | 工具 | 用途 |
|------|------|------|
| 开写前（已完成） | `/plan-eng-review`（本轮） | 锁架构、测试、分支；计划末尾须有 `## GSTACK REVIEW REPORT` |
| 每特性枝实现 | `superpowers:subagent-driven-development` 或 `executing-plans` | 按 Task 复选框执行；TDD |
| 某枝准备合并前 | gstack `/review`（若可用）或人工 diff 审 | 审该枝相对 master 的 diff |
| 合并/发 PR 前 | gstack `/ship` | 检测 base、跑测试、整理 commit、开 PR（有远程时） |
| UI 可点后 | gstack `/qa` | 对本机 `http://127.0.0.1:8000/ui/` 走通计划→背词→模考 |
| 范围再膨胀时 | `/plan-eng-review` 或 `/office-hours` | 先评审再改计划，禁止无评审扩 scope |
| 并行发音/华为计划 | 各开 writing-plans → 再 `/plan-eng-review` | 不得绕过 foundation/core 直接改私有表 |

### 代理执行检查清单（每个 PR）

- [ ] 当前不在裸 `master` 上开发（除非 Task 13 docs-only 且已声明）
- [ ] `pytest -v` 全绿（或该枝约定的测试子集 + 说明）
- [ ] 未引入第二份 Ollama；未添加公网端口转发文档作为默认路径
- [ ] OpenSpec change 文件夹与分支名对应
- [ ] 准备合并时运行 `/ship` 或等价：`gh pr create` + 测试证据

### 明确不在本计划调用的 gstack

- `/land-and-deploy`（无云部署）
- 自动 `git add CLAUDE.md && commit` 类 setup 副作用（本环境禁止未经要求提交配置）

---

## File Structure

```text
openspec/
  config.yaml
  specs/                          # 主规格（archive 后合并）
  changes/
    arch-foundation/
      proposal.md
      design.md
      tasks.md
      specs/architecture/spec.md
    toefl-vertical-slice/
      proposal.md
      design.md
      tasks.md
      specs/learning/spec.md
pyproject.toml
requirements.txt
README.md
src/es_app/
  __init__.py
  main.py                         # FastAPI app 装配
  config.py                       # ES_DATA_DIR, OLLAMA_HOST, ES_BIND
  errors.py                       # ErrorBody + exception handlers
  db.py                           # SQLite 连接与 schema 迁移（含 session 表）
  schemas/
    __init__.py
    word.py                       # Word, WordCandidate
    common.py                     # ErrorBody
  quiz/
    __init__.py
    distractors.py                # pick_definition_distractors（study+exam 共用）
  adapters/
    __init__.py
    protocols.py                  # OcrPort, VisionOcrPort, OllamaPort
    tesseract_ocr.py
    fake_ocr.py                   # 测试与无 Tesseract 降级
    ollama_client.py              # 仅健康检查桩；evaluate 可 NotImplemented
  lexicon/
    __init__.py
    store.py
    service.py
    router.py
    builtin_toefl.json            # 小样例词表（≥20 词，含完整五字段优先）
  plans/
    __init__.py
    service.py
    router.py
  ingest/
    __init__.py
    parsers.py                    # CSV/TXT → WordCandidate
    service.py
    router.py
  study/
    __init__.py
    service.py
    router.py
  exam/
    __init__.py
    templates.py                  # synonym + contextual 两种题型
    service.py
    router.py
  progress/
    __init__.py
    service.py
    router.py
  speech/
    __init__.py
    router.py                     # POST /speech/evaluate → 503
static/
  index.html
  app.js
  styles.css
tests/
  conftest.py
  test_word_schema.py
  test_lexicon_store.py
  test_plans.py
  test_ingest_parsers.py
  test_ingest_ocr.py
  test_study.py
  test_exam.py
  test_progress.py
  test_api_e2e.py
  fixtures/
    words_sample.csv
    words_sample.txt
    ocr_sample.png                # 含清晰英文单词的小图
```

---

### Task 0: 建立 `feat/arch-foundation` 分支

**Files:**
- None（仅 Git）

**Interfaces:**
- Consumes: 干净 `master`
- Produces: 工作分支 `feat/arch-foundation`

- [ ] **Step 1: 确认在 master 且工作区干净**

```bash
git status -sb
git checkout master
```

Expected: 无未提交脏文件（或仅有本计划文档已提交）

- [ ] **Step 2: 创建特性枝**

```bash
git checkout -b feat/arch-foundation
```

- [ ] **Step 3: 记录 gstack 起点（可选）**

若本机有 gstack timeline：

```bash
~/.claude/skills/gstack/bin/gstack-timeline-log '{"skill":"executing-plans","event":"started","branch":"feat/arch-foundation"}' 2>/dev/null || true
```

---

### Task 1: OpenSpec 初始化与 `arch-foundation` 提案

**Files:**
- Create: `openspec/config.yaml`
- Create: `openspec/changes/arch-foundation/proposal.md`
- Create: `openspec/changes/arch-foundation/design.md`
- Create: `openspec/changes/arch-foundation/tasks.md`
- Create: `openspec/changes/arch-foundation/specs/architecture/spec.md`
- Create: `README.md`

**Interfaces:**
- Consumes: 设计文档 `docs/superpowers/specs/2026-07-24-english-learning-design.md`
- Produces: OpenSpec change 目录约定；后续任务在实现时勾选 `tasks.md`

- [ ] **Step 1: 安装 OpenSpec CLI 并初始化**

Run:

```bash
npm install -g @fission-ai/openspec
cd "D:/work/AI PROGRAME/es"
openspec init
```

Expected: 生成 `openspec/` 目录（若 CLI 交互询问工具，选 Cursor / 通用即可）。若 `openspec` 不可用，跳过 npm，**手工创建**下方文件（内容仍以本任务为准）。

- [ ] **Step 2: 写入 `openspec/config.yaml`**

```yaml
schema: spec-driven
```

- [ ] **Step 3: 写入 foundation 提案文件**

`openspec/changes/arch-foundation/proposal.md`:

```markdown
# arch-foundation

## Why
空仓库需要先锁定模块边界、共享 Schema、Adapter Protocol 与数据目录，避免并行特性冲突。

## What Changes
- 模块化 FastAPI 目录与 OpenAPI 骨架
- Word Schema（word/phonetic/audio/definitions/examples）
- OCR/Ollama Adapter Protocol
- 统一错误体；SQLite + ES_DATA_DIR
- `/speech/evaluate` 503 桩

## Non-Goals
完整发音评测、华为客户端、托福学习闭环业务（见 toefl-vertical-slice）
```

`openspec/changes/arch-foundation/design.md`: 从设计文档 §2–§3、§6 摘录进程边界与模块表（保持与设计一致，勿发明新边界）。

`openspec/changes/arch-foundation/specs/architecture/spec.md`:

```markdown
# Architecture Spec

## Requirement: Modular monolith boundaries
系统 SHALL 按 plans/lexicon/ingest/study/exam/progress/speech/adapters 分包；UI SHALL 只经 OpenAPI 访问。

## Requirement: Lexicon word schema
Word SHALL 包含 word, phonetic, audio, definitions (list of string), examples (list of string)。

## Requirement: Adapter isolation
领域代码 SHALL 依赖 OCR/Ollama Protocol；实现位于 adapters/。

## Requirement: Ollama single instance
系统 SHALL 通过 OLLAMA_HOST 连接已有 WSL Ollama；SHALL NOT 默认安装第二份 Windows Ollama。
```

`openspec/changes/arch-foundation/tasks.md`:

```markdown
## Tasks
- [ ] Python 包骨架、config、errors、db
- [ ] schemas.word + adapters.protocols
- [ ] speech 503 桩路由挂到 app
- [ ] README 说明 ES_DATA_DIR / OLLAMA_HOST
```

- [ ] **Step 4: 写 README 最小说明**

```markdown
# es — English Study

本机英语学习（托福 MVP）。API: FastAPI；UI: `static/`；数据: `ES_DATA_DIR`；Ollama: `OLLAMA_HOST`（WSL）。

规格: `docs/superpowers/specs/2026-07-24-english-learning-design.md`
OpenSpec: `openspec/changes/`
```

- [ ] **Step 5: Commit**

```bash
git add openspec README.md
git commit -m "docs: add OpenSpec arch-foundation change"
```

---

### Task 2: 工程骨架、配置、错误体、数据库

**Files:**
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `src/es_app/__init__.py`
- Create: `src/es_app/config.py`
- Create: `src/es_app/errors.py`
- Create: `src/es_app/db.py`
- Create: `src/es_app/schemas/common.py`
- Create: `tests/conftest.py`
- Create: `tests/test_config_db.py`

**Interfaces:**
- Consumes: 无
- Produces: `get_settings() -> Settings`；`get_connection(data_dir: Path) -> sqlite3.Connection`；`ErrorBody(code, message, details=None)`；`init_db(conn)`

- [ ] **Step 1: Write failing test**

```python
# tests/test_config_db.py
from pathlib import Path
from es_app.config import get_settings
from es_app.db import get_connection, init_db


def test_settings_respect_env(monkeypatch, tmp_path):
    monkeypatch.setenv("ES_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")
    s = get_settings()
    assert s.data_dir == tmp_path
    assert s.ollama_host == "http://127.0.0.1:11434"


def test_init_db_creates_words_table(tmp_path):
    conn = get_connection(tmp_path)
    init_db(conn)
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='words'"
    ).fetchall()
    assert rows == [("words",)]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pip install pytest pydantic pydantic-settings && pip install -e .`（先写好 `pyproject.toml` 的包发现后再跑）

若包尚不存在，先完成 Step 3 的 `pyproject.toml` 再跑：

`pytest tests/test_config_db.py -v`

Expected: FAIL（模块未定义）或在仅有 pyproject 时 FAIL import。

- [ ] **Step 3: Write minimal implementation**

`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "es-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",
  "uvicorn[standard]>=0.32.0",
  "pydantic>=2.0",
  "pydantic-settings>=2.0",
  "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "httpx>=0.27"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
pythonpath = ["src"]
```

`requirements.txt`:

```text
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
pydantic>=2.0
pydantic-settings>=2.0
python-multipart>=0.0.9
pytest>=8.0
httpx>=0.27
```

`src/es_app/config.py`:

```python
from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    data_dir: Path = Field(
        default_factory=lambda: Path.home() / ".es_app",
        validation_alias="ES_DATA_DIR",
    )
    ollama_host: str = Field(
        default="http://127.0.0.1:11434",
        validation_alias="OLLAMA_HOST",
    )


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.data_dir.mkdir(parents=True, exist_ok=True)
    return s
```

`src/es_app/schemas/common.py`:

```python
from pydantic import BaseModel


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict | list | str | None = None
```

`src/es_app/errors.py`:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from es_app.schemas.common import ErrorBody


class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_req: Request, exc: AppError):
        body = ErrorBody(code=exc.code, message=exc.message, details=exc.details)
        return JSONResponse(status_code=exc.status_code, content=body.model_dump())
```

`src/es_app/db.py`:

```python
import sqlite3
from pathlib import Path


def get_connection(data_dir: Path) -> sqlite3.Connection:
    data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(data_dir / "es.sqlite3")
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
```

`Settings` 增加：

```python
bind_host: str = Field(default="127.0.0.1", validation_alias="ES_BIND")
```

`tests/conftest.py`:

```python
import pytest
from es_app.db import get_connection, init_db
from es_app.config import get_settings


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("ES_DATA_DIR", str(tmp_path))
    get_settings.cache_clear()
    return tmp_path


@pytest.fixture
def conn(data_dir):
    c = get_connection(data_dir)
    init_db(c)
    yield c
    c.close()
```

- [ ] **Step 4: Run tests**

```bash
pip install -e ".[dev]"
pytest tests/test_config_db.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml requirements.txt src/es_app tests
git commit -m "feat: add app skeleton, settings, errors, and sqlite init"
```

---

### Task 3: Word Schema 与 Lexicon 存储

**Files:**
- Create: `src/es_app/schemas/word.py`
- Create: `src/es_app/lexicon/store.py`
- Create: `src/es_app/lexicon/service.py`
- Create: `src/es_app/lexicon/__init__.py`
- Create: `tests/test_word_schema.py`
- Create: `tests/test_lexicon_store.py`

**Interfaces:**
- Consumes: `db.init_db`, `sqlite3.Connection`
- Produces:
  - `Word(id: int, word: str, phonetic: str | None, audio: str | None, definitions: list[str], examples: list[str], incomplete: bool)`
  - `WordCandidate`（无 id）
  - `LexiconStore.add_word(...) -> Word`
  - `LexiconStore.list_words(*, complete_only: bool = False) -> list[Word]`
  - `LexiconStore.get_by_word(word: str) -> Word | None`
  - `is_incomplete(definitions: list[str]) -> bool`（definitions 为空则 incomplete）

- [ ] **Step 1: Write failing tests**

```python
# tests/test_word_schema.py
from es_app.schemas.word import WordCandidate


def test_word_candidate_defaults():
    c = WordCandidate(word="abandon")
    assert c.phonetic is None
    assert c.definitions == []
    assert c.examples == []


# tests/test_lexicon_store.py
from es_app.lexicon.store import LexiconStore
from es_app.schemas.word import WordCandidate


def test_add_and_list_marks_incomplete(conn):
    store = LexiconStore(conn)
    w = store.add_from_candidate(WordCandidate(word="foo", definitions=[]))
    assert w.incomplete is True
    w2 = store.add_from_candidate(
        WordCandidate(word="bar", definitions=["放弃"], examples=["He abandoned it."])
    )
    assert w2.incomplete is False
    assert len(store.list_words()) == 2
    assert len(store.list_words(complete_only=True)) == 1
```

- [ ] **Step 2: Run tests — expect FAIL**

`pytest tests/test_word_schema.py tests/test_lexicon_store.py -v`

- [ ] **Step 3: Implement**

`src/es_app/schemas/word.py`:

```python
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
```

`src/es_app/lexicon/store.py`:

```python
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
```

`src/es_app/lexicon/service.py`:

```python
from es_app.lexicon.store import LexiconStore
from es_app.schemas.word import Word, WordCandidate


class LexiconService:
    def __init__(self, store: LexiconStore):
        self._store = store

    def list_words(self, complete_only: bool = False) -> list[Word]:
        return self._store.list_words(complete_only=complete_only)

    def confirm_candidates(self, candidates: list[WordCandidate]) -> list[Word]:
        out: list[Word] = []
        for c in candidates:
            existing = self._store.get_by_word(c.word.strip())
            if existing:
                out.append(existing)
                continue
            out.append(self._store.add_from_candidate(c))
        return out
```

- [ ] **Step 4: Run tests — expect PASS**

`pytest tests/test_word_schema.py tests/test_lexicon_store.py -v`

- [ ] **Step 5: Commit**

```bash
git add src/es_app/schemas src/es_app/lexicon tests
git commit -m "feat: add word schema and lexicon store"
```

---

### Task 4: 内置托福词表种子 + Lexicon 路由

**Files:**
- Create: `src/es_app/lexicon/builtin_toefl.json`
- Create: `src/es_app/lexicon/seed.py`
- Create: `src/es_app/lexicon/router.py`
- Create: `tests/test_lexicon_seed.py`
- Modify: later wired in `main.py`（本任务可先测 service；路由测放 Task 11 亦可——此处含 router 单测用 FastAPI）

**Interfaces:**
- Consumes: `LexiconService.confirm_candidates`
- Produces: `seed_builtin_toefl(service) -> int`（插入条数）；`GET /lexicon/words`

- [ ] **Step 1: Write failing test**

```python
# tests/test_lexicon_seed.py
from es_app.lexicon.store import LexiconStore
from es_app.lexicon.service import LexiconService
from es_app.lexicon.seed import seed_builtin_toefl


def test_seed_inserts_at_least_20(conn):
    svc = LexiconService(LexiconStore(conn))
    n = seed_builtin_toefl(svc)
    assert n >= 20
    assert len(svc.list_words()) >= 20
    assert seed_builtin_toefl(svc) == 0  # idempotent
```

- [ ] **Step 2: Run — expect FAIL**

- [ ] **Step 3: Implement builtin JSON（至少 20 条；示例节选，文件中写满 20+）**

`builtin_toefl.json` 每项形如：

```json
[
  {
    "word": "abandon",
    "phonetic": "/əˈbændən/",
    "audio": null,
    "definitions": ["to leave forever", "放弃"],
    "examples": ["They had to abandon the car."]
  }
]
```

补足至 ≥20 个常见托福词（可手写简明中英释义）。

`seed.py`:

```python
import json
from importlib import resources
from es_app.lexicon.service import LexiconService
from es_app.schemas.word import WordCandidate


def seed_builtin_toefl(service: LexiconService) -> int:
    raw = resources.files("es_app.lexicon").joinpath("builtin_toefl.json").read_text(encoding="utf-8")
    items = json.loads(raw)
    added = 0
    for item in items:
        cand = WordCandidate.model_validate(item)
        before = service.list_words()
        words = {w.word for w in before}
        if cand.word in words:
            continue
        service.confirm_candidates([cand])
        added += 1
    return added
```

`router.py`:

```python
from fastapi import APIRouter, Depends
from es_app.lexicon.service import LexiconService
from es_app.schemas.word import Word

router = APIRouter(prefix="/lexicon", tags=["lexicon"])


def get_lexicon_service() -> LexiconService:
    raise NotImplementedError  # overridden in main


@router.get("/words", response_model=list[Word])
def list_words(complete_only: bool = False, svc: LexiconService = Depends(get_lexicon_service)):
    return svc.list_words(complete_only=complete_only)
```

- [ ] **Step 4: PASS + Commit**

```bash
pytest tests/test_lexicon_seed.py -v
git add src/es_app/lexicon tests/test_lexicon_seed.py
git commit -m "feat: seed builtin TOEFL lexicon and list API stub"
```

---

### Task 5: Plans 服务（托福计划）

**Files:**
- Create: `src/es_app/plans/service.py`
- Create: `src/es_app/plans/router.py`
- Create: `src/es_app/plans/__init__.py`
- Create: `tests/test_plans.py`

**Interfaces:**
- Consumes: `LexiconStore.list_words(complete_only=True)`；`plans` / `plan_words` 表
- Produces:
  - `create_toefl_plan(daily_quota: int) -> Plan`
  - `Plan(id, exam_type="toefl", daily_quota, days: list[PlanDay])`
  - `PlanDay(day_index: int, word_ids: list[int])`
  - `POST /plans` body `{ "exam_type": "toefl", "daily_quota": 10 }`
  - `GET /plans/{id}`

行为：从完整词条按 id 顺序切片，每 `daily_quota` 个词一天；词不足一天也建计划。

- [ ] **Step 1: Failing test**

```python
from es_app.lexicon.store import LexiconStore
from es_app.lexicon.service import LexiconService
from es_app.lexicon.seed import seed_builtin_toefl
from es_app.plans.service import PlanService


def test_create_toefl_plan_slices_days(conn):
    lex = LexiconService(LexiconStore(conn))
    seed_builtin_toefl(lex)
    plans = PlanService(conn, LexiconStore(conn))
    plan = plans.create_plan(exam_type="toefl", daily_quota=5)
    assert plan.exam_type == "toefl"
    assert plan.daily_quota == 5
    assert len(plan.days) >= 1
    assert sum(len(d.word_ids) for d in plan.days) == len(lex.list_words(complete_only=True))
```

- [ ] **Step 2–4: Implement `PlanService` + Pydantic models in `plans/service.py`，跑通测试并 commit**

`create_plan` 核心逻辑：

```python
words = self._lexicon.list_words(complete_only=True)
# insert plans row; chunk words into days; insert plan_words
```

若 `complete_only` 词数为 0：raise `AppError("empty_lexicon", "请先加载词库", 400)`。

**硬门禁测试（gstack D10）：**

```python
def test_create_plan_empty_lexicon_400(conn):
    plans = PlanService(conn, LexiconStore(conn))
    try:
        plans.create_plan(exam_type="toefl", daily_quota=5)
        assert False, "expected AppError"
    except AppError as e:
        assert e.status_code == 400
        assert e.code == "empty_lexicon"
```

```bash
pytest tests/test_plans.py -v
git add src/es_app/plans tests/test_plans.py
git commit -m "feat: create TOEFL study plans from lexicon"
```

**分支提醒：** 本任务起应在 `feat/toefl-core`（foundation 合并后切枝）。若仍在 foundation，先完成 foundation merge 再继续。

---

### Task 6: 文件导入（CSV/TXT）与确认入库

**Files:**
- Create: `src/es_app/ingest/parsers.py`
- Create: `src/es_app/ingest/service.py`
- Create: `src/es_app/ingest/router.py`
- Create: `tests/fixtures/words_sample.csv`
- Create: `tests/fixtures/words_sample.txt`
- Create: `tests/test_ingest_parsers.py`

**Interfaces:**
- Consumes: `LexiconService.confirm_candidates`
- Produces:
  - `parse_csv(text) -> tuple[list[WordCandidate], list[dict]]`（成功候选, 失败行）
  - `parse_txt(text) -> ...`（每行 `word|definition` 或仅 `word`）
  - `POST /ingest/file` multipart → `{ candidates, failures }`
  - `POST /ingest/confirm` body `{ candidates: WordCandidate[] }` → `Word[]`

CSV 头：`word,phonetic,audio,definitions,examples`；`definitions`/`examples` 用 `;` 分隔多值。

- [ ] **Step 1: Failing tests**

```python
from pathlib import Path
from es_app.ingest.parsers import parse_csv, parse_txt


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_csv_partial_success():
    text = (FIXTURES / "words_sample.csv").read_text(encoding="utf-8")
    ok, failures = parse_csv(text)
    assert any(c.word == "diligent" for c in ok)
    assert failures  # 含空 word 行


def test_parse_txt():
    text = (FIXTURES / "words_sample.txt").read_text(encoding="utf-8")
    ok, failures = parse_txt(text)
    assert len(ok) >= 1
```

Fixture CSV 含一行合法、一行空 word。

- [ ] **Step 2–4: 实现 parsers + service + commit**

```bash
pytest tests/test_ingest_parsers.py -v
git add src/es_app/ingest tests/fixtures tests/test_ingest_parsers.py
git commit -m "feat: parse CSV/TXT word imports with partial failure reporting"
```

---

### Task 7: OCR 导入（Tesseract 默认 + Fake）

**Files:**
- Create: `src/es_app/adapters/protocols.py`
- Create: `src/es_app/adapters/fake_ocr.py`
- Create: `src/es_app/adapters/tesseract_ocr.py`
- Create: `src/es_app/ingest/ocr_pipeline.py`
- Create: `tests/test_ingest_ocr.py`
- Create: `tests/fixtures/ocr_sample.png`（可用 PIL 在测试里生成纯文字图，避免二进制入库困难）

**Interfaces:**
- Consumes: `OcrPort.extract_text(image_bytes: bytes) -> str`
- Produces: `candidates_from_ocr_text(text) -> list[WordCandidate]`（按空白/换行抽词，definitions 空 → incomplete）
- `POST /ingest/image` → candidates（不自动入库）

- [ ] **Step 1: Failing test（不依赖真实 Tesseract）**

```python
from es_app.adapters.fake_ocr import FakeOcr
from es_app.ingest.ocr_pipeline import run_ocr_to_candidates


def test_fake_ocr_to_candidates():
    ocr = FakeOcr(text="abandon\nbenefit\n")
    cands = run_ocr_to_candidates(ocr, b"fake")
    assert {c.word for c in cands} == {"abandon", "benefit"}
    assert all(c.definitions == [] for c in cands)
```

- [ ] **Step 2–4: Implement Protocol + Fake + pipeline；Tesseract 实现尝试 `pytesseract`，导入失败时文档说明用 Fake**

`protocols.py`:

```python
from typing import Protocol


class OcrPort(Protocol):
    def extract_text(self, image_bytes: bytes) -> str: ...


class VisionOcrPort(Protocol):
    def enhance_text(self, image_bytes: bytes, base_text: str) -> str: ...
```

本任务 **不实现** Vision 增强（返回原 text 的 Noop 即可）：

```python
class NoopVisionOcr:
    def enhance_text(self, image_bytes: bytes, base_text: str) -> str:
        return base_text
```

**性能（gstack D11）：** `POST /ingest/image` 的 OCR 调用必须经 `asyncio.to_thread(...)` 或 Starlette `run_in_threadpool`，禁止在 `async def` 路由里直接阻塞跑 Tesseract。

**分支：** `feat/ingest-ocr`（core 合并之后）。

```bash
pytest tests/test_ingest_ocr.py -v
git add src/es_app/adapters src/es_app/ingest tests/test_ingest_ocr.py
git commit -m "feat: OCR ingest via OcrPort with fake adapter for tests"
```

---

### Task 8: Study 背词会话

**Files:**
- Create: `src/es_app/quiz/distractors.py`
- Create: `src/es_app/study/service.py`
- Create: `src/es_app/study/router.py`
- Create: `tests/test_study.py`
- Create: `tests/test_distractors.py`
- Create: `tests/test_study_session_persist.py`

**Interfaces:**
- Consumes: plan word_ids；lexicon words；`pick_definition_distractors(correct: str, pool: list[str], k: int = 3, *, rng) -> list[str]`
- Produces:
  - `POST /study/sessions` `{ plan_id, day_index, mode: "flashcard"|"mcq" }` → session（**写入 `study_sessions` 表**）
  - `POST /study/sessions/{id}/answer` `{ word_id, answer }` → `{ correct, correct_definition }`
  - 写 `progress_events` kind=`study`

MCQ：题干为英文 word，选项为 4 个中文释义（1 正确 + 3 干扰，**必须**调用 `quiz.distractors`）。

- [ ] **Step 1: Write failing tests**（含持久化硬门禁）

```python
def test_study_mcq_answer(conn):
    # seed, create plan, start session mode=mcq, answer correctly/incorrectly
    ...


def test_study_session_survives_new_connection(data_dir, monkeypatch):
    """同一 ES_DATA_DIR，第二次 create_app/新连接仍能 answer。"""
    ...
```

- [ ] **Step 2–4: Implement + commit**

```bash
pytest tests/test_distractors.py tests/test_study.py tests/test_study_session_persist.py -v
git add src/es_app/quiz src/es_app/study tests/test_distractors.py tests/test_study.py tests/test_study_session_persist.py
git commit -m "feat: study sessions with flashcard, mcq, and sqlite persistence"
```

---

### Task 9: Exam 两种托福词汇题型

**Files:**
- Create: `src/es_app/exam/templates.py`
- Create: `src/es_app/exam/service.py`
- Create: `src/es_app/exam/router.py`
- Create: `tests/test_exam.py`

**Interfaces:**
- Consumes: complete words only（`incomplete=0`）
- Produces:
  - 题型 `synonym_mcq`：选与题干最接近的同义释义（用 definitions 第一条作正确项；干扰项其他词）
  - 题型 `contextual_blank`：例句挖空（用 `examples[0]`，将 word 替换为 `____`；**若无例句则跳过该词**，并有单测锁定）
  - `POST /exam/sessions` `{ plan_id, question_count: int }` → 混合两种题型（各至少 1 题，若词量允许）；**写入 `exam_sessions`**
  - `POST /exam/sessions/{id}/submit` `{ answers: [{question_id, choice}] }` → report `{ score, total, wrong_word_ids }`
  - 写 `progress_events` kind=`exam`
  - synonym 干扰项 **必须** 复用 `quiz.distractors`

- [ ] **Step 1: Failing tests for both templates + submit report + skip-no-example + session persist**

```python
from es_app.exam.templates import build_synonym_mcq, build_contextual_blank


def test_build_synonym_mcq_has_four_options(conn):
    ...


def test_contextual_skips_word_without_examples(conn):
    ...


def test_exam_session_survives_new_connection(data_dir, monkeypatch):
    ...


def test_exam_report_scores(conn):
    ...
```

- [ ] **Step 2–4: Implement + commit**

```bash
pytest tests/test_exam.py -v
git add src/es_app/exam tests/test_exam.py
git commit -m "feat: TOEFL-like exam with synonym and contextual templates"
```

---

### Task 10: Progress 汇总

**Files:**
- Create: `src/es_app/progress/service.py`
- Create: `src/es_app/progress/router.py`
- Create: `tests/test_progress.py`

**Interfaces:**
- Consumes: `progress_events`
- Produces: `GET /progress/summary` → `{ study_answered, study_correct, exam_sessions, weak_word_ids: list[int] }`  
  `weak_word_ids`：study/exam 中答错次数 ≥1 的 word_id，按错次降序，最多 20。

- [ ] **Step 1–4: TDD + commit**

```bash
pytest tests/test_progress.py -v
git commit -m "feat: progress summary with weak words"
```

---

### Task 11: FastAPI `main` 装配、Speech 503 桩、E2E API 测试

**Files:**
- Create: `src/es_app/main.py`
- Create: `src/es_app/speech/router.py`
- Create: `tests/test_api_e2e.py`
- Create: `openspec/changes/toefl-vertical-slice/proposal.md`（及 design/tasks/specs 摘要）

**Interfaces:**
- Consumes: 所有 router
- Produces: 可运行应用；`POST /speech/evaluate` → 503 `ErrorBody(code="ollama_unavailable", ...)` 直至发音计划实现

- [ ] **Step 1: Failing E2E test**

```python
from fastapi.testclient import TestClient
from es_app.main import create_app


def test_toefl_loop(data_dir, monkeypatch):
    monkeypatch.setenv("ES_DATA_DIR", str(data_dir))
    from es_app.config import get_settings
    get_settings.cache_clear()
    client = TestClient(create_app())
    assert client.post("/plans", json={"exam_type": "toefl", "daily_quota": 5}).status_code == 200
    words = client.get("/lexicon/words").json()
    assert len(words) >= 20
    r = client.post("/speech/evaluate", json={"word_id": words[0]["id"]})
    assert r.status_code == 503
```

（补全：study session → exam → progress；**两次 `create_app()` 共享 data_dir 测会话持久化**；`GET /ui/` 200 且 `GET /plans` 非静态误伤。）

- [ ] **Step 2: Implement `create_app()`** — 依赖注入覆盖各 `get_*_service`；启动时 `init_db` + `seed_builtin_toefl`。**路由挂载顺序：** 先 `include_router` 全部 API，再 `mount("/ui", StaticFiles(...))`，`GET /` → RedirectResponse `/ui/`。

`speech/router.py`:

```python
from fastapi import APIRouter
from es_app.errors import AppError

router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/evaluate")
def evaluate():
    raise AppError(
        "ollama_unavailable",
        "发音评测尚未启用或 Ollama 不可用",
        status_code=503,
    )
```

- [ ] **Step 3: OpenSpec `toefl-vertical-slice` 提案文件**（What: plans/lexicon/ingest/study/exam/progress/UI；Non-goals: speech 完整、华为）

- [ ] **Step 4: PASS + commit**

```bash
pytest tests/test_api_e2e.py -v
git commit -m "feat: wire FastAPI app, speech stub, and TOEFL API e2e"
```

---

### Task 12: 最小 Web UI（本机浏览器闭环）

**Files:**
- Create: `static/index.html`
- Create: `static/app.js`
- Create: `static/styles.css`
- Modify: `src/es_app/main.py` — `app.mount("/", StaticFiles(...))` 注意 API 路由优先

**Interfaces:**
- Consumes: `/plans`, `/lexicon/words`, `/study/*`, `/exam/*`, `/progress/summary`, `/ingest/file`

UI 一页四块（不要做成仪表盘堆砌）：顶部标题「托福学习」；主操作：创建计划 → 背词 → 模考 → 看进度；侧或下部：文件上传导入。  
**入口 URL：** `http://127.0.0.1:8000/ui/`（根路径重定向到此）。

- [ ] **Step 1: 手写静态页调用 API（fetch）**
- [ ] **Step 2: 本地启动验收（默认 WSL）**

```bash
# 在 WSL 内，仓库目录下：
export ES_DATA_DIR="$HOME/.es_app"
export OLLAMA_HOST="http://127.0.0.1:11434"
export ES_BIND="127.0.0.1"
uvicorn es_app.main:app --app-dir src --reload --host "$ES_BIND" --port 8000
```

浏览器打开 `http://127.0.0.1:8000/ui/`，走通：建计划 → 背 1 题 → 考 1 次 → 看 summary。

**Tailscale（华为外网，骨架阶段）：** 手机与 WSL 节点加入同一 Tailnet；临时 `ES_BIND=0.0.0.0`，用 WSL 的 Tailscale IP:8000；**不要**做路由器端口转发。

- [ ] **Step 3: 合并前 gstack 门禁**

```bash
pytest -v
# 有远程时：
# git push -u origin HEAD && gh pr create
# 然后 /ship 或人工 merge 到 master，再切下一枝
```

- [ ] **Step 4: Commit**

```bash
git add static src/es_app/main.py
git commit -m "feat: add minimal web UI for TOEFL study loop"
```

---

### Task 13: 计划自检收尾与后续计划入口

**Files:**
- Modify: `openspec/changes/arch-foundation/tasks.md`（勾选已完成项）
- Modify: `openspec/changes/toefl-vertical-slice/tasks.md`
- Create: `docs/superpowers/plans/2026-07-24-pronunciation.md`（仅目录级 stub：目标一句 + 「待 writing-plans 展开」不可——应写清范围边界，完整步骤可极短指向设计 §5.3）
- Create: `docs/superpowers/plans/2026-07-24-huawei-client-skeleton.md`（同上）

为避免空壳 stub 违反 No Placeholders：这两个后续计划文件各写 **Goal / 依赖 foundation / 非目标 / 下一步：单独开 writing-plans 会话**，不假装已有逐步代码任务。

- [ ] **Step 1: 跑全量测试**

```bash
pytest -v
```

Expected: 全部 PASS

- [ ] **Step 2: 更新 OpenSpec change tasks 勾选**
- [ ] **Step 3: Commit**

```bash
git add openspec docs/superpowers/plans
git commit -m "docs: mark OpenSpec MVP tasks done and note follow-on plans"
```

---

## Spec Coverage Checklist（自检）

| 设计要求 | 对应任务 |
|----------|----------|
| OpenSpec 管理特性 | T1, T11, T13 |
| 模块化单体 + Adapter | T2–T7, T11 |
| Ollama 不重复 / 503 降级 | T2 config, T11 speech 桩 |
| 词库五字段 | T3 |
| 内置托福 + 文件 + OCR | T4, T6, T7 |
| 候选确认后入库 | T3 service, T6 confirm |
| 背词 flashcard/mcq | T8 |
| 两种托福词汇题型 | T9 |
| 进度汇总 | T10 |
| Web UI Windows | T12 |
| 发音完整 / 华为 | 后续计划（本计划明确排除） |
| Vision OCR 增强 | T7 Noop；完整增强归发音/后续小变更 |

## Type / 命名一致性

- `Word` / `WordCandidate` / `definitions` / `examples` 全计划统一
- 环境变量：`ES_DATA_DIR`、`OLLAMA_HOST`、`ES_BIND`
- 路由前缀与设计 §3.3 一致（API 无前缀；UI 在 `/ui`）
- `AppError` + `ErrorBody` 统一错误
- 分支：`feat/arch-foundation` → `feat/toefl-core` → `feat/ingest-ocr`

---

## Execution Handoff

实现前确认本文件末尾 `## GSTACK REVIEW REPORT` 为 CLEAR。  

**Two execution options:**

1. **Subagent-Driven（推荐）** — 每任务一个新子代理，任务间审查；遵守 Git 分支映射  
2. **Inline Execution** — 本会话 executing-plans；每枝合并点暂停  

**Which approach?**

---

## GSTACK REVIEW REPORT

| Review | Trigger | Why | Runs | Status | Findings |
|--------|---------|-----|------|--------|----------|
| CEO Review | `/plan-ceo-review` | Scope & strategy | 0 | — | not run |
| Codex Review | `/codex review` | Independent 2nd opinion | 0 | — | not run |
| Eng Review | `/plan-eng-review` | Architecture & tests (required) | 1 | CLEAR | 11 decisions accepted; 0 unresolved |
| Design Review | `/plan-design-review` | UI/UX gaps | 0 | — | not run (minimal /ui; optional before polish) |
| DX Review | `/plan-devex-review` | Developer experience gaps | 0 | — | not run |

**Outside voice:** 未跑独立第二模型；结论仅基于本轮 eng review。

**Accepted decisions (this review):**
- Scope: keep full MVP features; split PRs via three sequential branches
- Branch topology: `feat/arch-foundation` → `feat/toefl-core` → `feat/ingest-ocr`
- Sessions: SQLite persistence + hard-gate restart tests
- Runtime: default API in WSL; `ES_BIND` default 127.0.0.1
- Phone WAN: Tailscale only; no bare port-forward; no cloud API host in this plan
- DRY: shared `quiz.distractors`
- Static: mount `/ui`; `/` redirects; API unprefixed
- Tests: empty plan 400; contextual skip no-example; `/ui` must not shadow API
- OCR: `run_in_threadpool` / `asyncio.to_thread`

**VERDICT:** ENG CLEARED — ready to implement on feature branches per Git/GSTACK sections.

NO UNRESOLVED DECISIONS
