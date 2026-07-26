# arch-foundation — Design

摘自 `docs/superpowers/specs/2026-07-24-english-learning-design.md` §2–§3、§6。

## 2. 系统上下文与进程边界

```text
[Web UI · 本机浏览器]
        │  HTTP (OpenAPI)
        ▼
[FastAPI 模块化单体 · 推荐部署在 WSL，与 Ollama 同机]
        │
        ├──► SQLite（计划/词库元数据/进度）+ 本地文件（词表、导入原稿、图片、音频）
        ├──► Tesseract（默认 OCR）
        └──► WSL Ollama（已有实例：发音评测 + 可选视觉 OCR）
                 ▲
[华为客户端骨架] ── HTTP（同一 OpenAPI；本机或局域网）
```

### 2.1 硬约束

1. **Ollama 唯一：** 只连接现有 WSL 端点（配置项如 `OLLAMA_HOST`），禁止再装 Windows 原生重复实例作为默认路径。
2. **UI 与领域分离：** Web / 华为只调用 API；不直连 DB、不直连 Ollama。
3. **降级可用：** 无 Ollama 时，背词与考试必须仍可用；发音与视觉 OCR 返回明确降级（如 503）。
4. **单用户本机：** MVP 无账号；数据根目录可配置。

## 3. 领域模块与稳定接口

### 3.1 模块职责

| 模块 | 职责 | 不负责 |
|------|------|--------|
| `plans` | 考试目标（首版托福）、计划生成与进度字段 | 出题、发音 |
| `lexicon` | 词条与词表 CRUD、内置托福词库 | 会话状态 |
| `ingest` | 本地文件导入、Tesseract OCR、可选 Vision OCR | 学习算法 |
| `study` | 背词会话（看英选义 / 翻卡片） | 托福题型组卷 |
| `exam` | 托福词汇模拟题型、限时、得分、报告 | SRS |
| `speech` | 录音、发音评测、纠错建议 | 词库 CRUD |
| `progress` | 背词/考试/发音事件的只读聚合 | 散落业务规则 |
| `adapters/` | `OllamaClient`、`TesseractOcr`、`VisionOcrOptional` | 领域规则 |

### 3.2 跨模块纪律

1. 模块间只经服务接口 / 共享 Schema；禁止直接 `import` 对方持久化层。
2. `ingest` 产出 `WordCandidate[]`，用户确认后才写入 `lexicon`。
3. `study` / `exam` / `speech` 只向 `progress` 写事件，不互相改对方表。
4. 领域代码依赖 OCR/LLM 的 **Protocol**，实现放在 `adapters/`。

### 3.3 对外稳定 API（OpenAPI 骨架）

- `GET/POST /plans` — 计划与进度
- `GET /lexicon/words` — 词条查询
- `POST /ingest/file` — 本地文件导入
- `POST /ingest/image` — 图片 OCR → 候选
- `POST /study/sessions` · `POST /study/sessions/{id}/answer`
- `POST /exam/sessions` · `POST /exam/sessions/{id}/submit`
- `POST /speech/evaluate` — 可 503 降级
- `GET /progress/summary`

客户端（Web / 华为）**只依赖上述契约与共享 Schema**，不依赖包内部结构。

## 6. 错误处理

- 统一错误体：`code`、`message`、`details`（面向用户可用中文）。
- 4xx：校验失败、空库开考、未确认候选误入学习等。
- 503 + 可选 `Retry-After`：依赖 Ollama 的能力不可用。
