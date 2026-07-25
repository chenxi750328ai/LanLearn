# MVP Verification + QA Evidence — 2026-07-25

Branch: `feat/ingest-ocr`  
Gates: Task 14 / Quality Assurance Gates A9–A12

## A9 verification-before-completion

### pytest

```text
Command: PYTHONPATH=src pytest -v
Result: 34 passed, 1 warning (Starlette TestClient deprecation), ~3.0s
Date: 2026-07-25 (after BOM fix commit 775bdd1)
```

### Server start

```text
Command: python -m uvicorn es_app.main:create_app --factory --host 127.0.0.1 --port 8000
(equivalent to scripts/start.ps1 without --reload for this session)
ES_DATA_DIR=%USERPROFILE%\.es_app_qa
Log: Uvicorn running on http://127.0.0.1:8000 — no traceback
```

### HTTP probe

| URL | Result |
|-----|--------|
| `GET /ui/` | 200, title 托福学习 |
| `GET /docs` | 200 |
| `GET /` | 307 Location `/ui/` |
| `POST /speech/evaluate` | 503 |

## A10 gstack `/qa` Standard — path checklist

| # | Path | Result |
|---|------|--------|
| 1 | start.ps1 / uvicorn start | PASS |
| 2 | open `/ui/` | PASS (browser) |
| 3 | `/` → `/ui/` | PASS |
| 4 | `/docs` | PASS |
| 5 | create TOEFL plan | PASS — 计划 #1 · 每日 5 · 5 天；背词/模考按钮启用 |
| 6 | study ≥1 answer | PASS — abandon → 「✓ 正确」 |
| 7 | exam submit score | PASS — 「得分 0 / 2」+ wrong_word_ids |
| 8 | progress refresh | PASS — 背词 1/1 100%；模考次数；薄弱词列出 |
| 9 | CSV upload preview | FAIL→FIXED — UTF-8 BOM made `word` column `\ufeffword` |
| 10 | OCR preview | PASS (degraded) — no Tesseract → FakeOcr empty candidates, HTTP 200, no white screen |
| 11 | speech 503 | PASS |
| 12 | console / 5xx | PASS on critical path (503 only speech) |

### Findings

| Sev | ID | Issue | Resolution |
|-----|-----|-------|------------|
| High | QA-1 | CSV with UTF-8 BOM: all rows `empty word` | Fixed in `parsers.py` (`_strip_bom` + key normalize); test `test_parse_csv_strips_utf8_bom`; commit `775bdd1`; re-probed ingest → candidate `qa_word_one` ok |
| Medium | QA-2 | Without Tesseract, OCR returns `candidates: []` silently | Deferred: acceptable degradation per plan; recommend UI toast 「未识别到词 / 请安装 Tesseract」 in follow-up |
| Low | QA-3 | Exam radio options not exposed as buttons in a11y tree | Note only; form submit works |

### Re-verify after QA-1

- `pytest tests/test_ingest_parsers.py` — 3 passed  
- Live `POST /ingest/file` with BOM CSV — 1 candidate + 1 failure (empty word row) — PASS  

## A12 `/review` notes (`master...HEAD`)

Reviewed via `git log` / `git diff --stat` (78 files, +3481/-38).

**Strengths:** modular packages; OpenSpec changes; SQLite sessions; `/ui` mount; speech 503; E2E + persist tests; start.ps1.

**ASK / follow-ups (non-blocking for merge after Task 14):**

1. Merge strategy: prefer `--no-ff` of `feat/ingest-ocr` into `master` (contains full lineage) or merge three branches in order.  
2. OCR empty-state UX toast (QA-2).  
3. Optional commit of `.cursor/` OpenSpec skills.

**No Critical open.**

## A13 design-review (MVP)

Verdict: **Accept MVP UI as-is** — single-column flow readable; import panel slightly dense but usable; no ship blocker. Polish deferred.

## Product acceptance

| Gate | Status |
|------|--------|
| Eng plan review | CLEAR (prior) |
| A9 verification | CLEAR (this doc) |
| A10 `/qa` Standard | CLEAR after QA-1 fix |
| A12 `/review` | CLEAR (notes above) |
| A14 `/ship` / finishing | **PENDING user choice** |

**PRODUCT ACCEPTANCE:** READY for user finishing option (merge / PR / keep branch).
