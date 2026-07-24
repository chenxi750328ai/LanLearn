# 英语学习软件 — 架构与 MVP 设计

**日期：** 2026-07-24  
**状态：** 待用户审阅 spec  
**仓库：** `D:\work\AI PROGRAME\es`

## 1. 目标与范围

### 1.1 产品目标

开发本机优先的英语学习软件，支持按考试制定学习计划、背单词、考试练习，以及（并行特性）发音评测；特性用 OpenSpec 管理。

### 1.2 MVP 垂直切片（托福）

打通：**选托福计划 → 词库（内置 + 导入 + OCR）→ 背词 → 托福词汇题型模考 → 进度汇总**。

### 1.3 平台策略

| 阶段 | 平台 | 说明 |
|------|------|------|
| MVP | Windows（Web UI） | 先闭环；Ollama 复用 WSL 已有实例，不重复安装 |
| 并行骨架 | 华为手机客户端 | 薄客户端，消费同一 OpenAPI；本机/局域网，不做云。具体 UI 技术栈在 `huawei-client-skeleton` 提案中选定，本设计只锁定「同一 API、无直连 DB/Ollama」 |
| 后置 | 完整华为上架、云同步 | 非本轮目标 |

### 1.4 已选技术栈与架构风格

- **后端：** Python FastAPI（模块化单体）
- **前端 MVP：** 本机浏览器 Web UI
- **持久化：** SQLite + 本地文件目录
- **OCR：** Tesseract 默认；WSL Ollama 视觉模型可选增强
- **发音：** WSL Ollama（Adapter）
- **架构：** 方案 1「模块化单体」+ 适配器纪律（发音/OCR 不渗入领域核心）

### 1.5 明确非目标（首版不做）

- 云同步、多用户账号
- 间隔复习（SRS）算法
- 网页爬取词源
- 完整托福听说读写套题
- 华为应用市场上架包
- Windows 再装一份 Ollama

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

## 4. 词库数据模型

每条词条（`Word`）至少包含：

| 字段 | 说明 | MVP 要求 |
|------|------|----------|
| `word` | 单词拼写 | 必填 |
| `phonetic` | 音标 | 可空；内置表尽量有 |
| `audio` | 发音音频（路径或 URI） | 可空；可后补 |
| `definitions` | 解释，MVP Schema 定为 `list[str]`（多义项即多条字符串） | 背词/考试前建议非空；缺失则标不完整 |
| `examples` | 例句，MVP Schema 定为 `list[str]` | 可空；模考/背词可降级展示 |

补充约定：

- 导入与 OCR 允许字段缺失；**未确认候选不进学习池**。
- 「不完整」词条可浏览与补全，默认不进入 exam 组卷（可配置例外）。
- 音标/音频与发音评测模块解耦：`speech` 可在评测时使用 `audio` 作参考，但无音频仍可评测（仅用户录音 vs 文本/模型）。

## 5. 数据流与托福学习闭环

### 5.1 主路径

```text
选目标「托福」→ plans 生成计划（每日词量/阶段）
        ↓
lexicon（内置托福表 ∪ 用户导入 ∪ OCR 确认入库）
        ↓
study：今日/计划内词 → 翻卡片或英选中义 → 记录对错
        ↓
exam：托福词汇题型模板组卷 → 限时作答 → 报告
        ↓
progress：完成度、正确率、弱词列表
```

### 5.2 导入支路

1. **文件（CSV/TXT 等）：** 解析 → `WordCandidate[]` → 用户确认 → `lexicon`
2. **图片：** Tesseract → 候选；可选 Ollama Vision 增强 → 确认入库
3. 部分成功：返回成功条数 + 失败行，禁止整批静默丢弃

### 5.3 发音支路（并行特性）

用户对某词触发 → `speech` 收录音 → WSL Ollama 评测 → 分数/纠错 → `progress`。  
Ollama 不可用时主路径不受影响。

### 5.4 考试模式

- 题型模板与词条解耦：`exam` 使用 `lexicon` + 干扰项策略组卷。
- 首版至少 **2 种** 托福词汇向题型模板（可配置）；报告含正确率与错词回链 `study`。
- 背词模式不做 SRS（后置）。

### 5.5 失败与降级

| 情况 | 行为 |
|------|------|
| OCR 失败 | 错误信息 + 保留原图路径，允许手改候选 |
| Ollama 超时/宕机 | `speech` / Vision OCR → 503；背词/考试继续 |
| 词库空 | 计划可建；study/exam 提示先加载内置表或导入 |

## 6. 错误处理

- 统一错误体：`code`、`message`、`details`（面向用户可用中文）。
- 4xx：校验失败、空库开考、未确认候选误入学习等。
- 503 + 可选 `Retry-After`：依赖 Ollama 的能力不可用。

## 7. 测试策略

| 层 | 内容 |
|----|------|
| 单元 | 解析器、组卷干扰项、计划日程、词条 Schema（含五字段） |
| 合约 | OpenAPI 与实现一致；Adapter 使用 Fake Ollama |
| 集成 | 临时 SQLite：study → exam → progress；OCR 用夹具图 |
| 手工 | Windows Web 托福闭环；WSL Ollama 发音冒烟（并行特性） |

## 8. OpenSpec 工作方式

### 8.1 提案顺序

1. **`arch-foundation`（先合并）**  
   目录结构、词库 Schema（单词/音标/发音/解释/例句）、OpenAPI 骨架、Adapter Protocol、数据目录约定、模块边界文档。

2. **并行三特性**（均依赖 foundation；互不修改对方私有表）：  
   - `toefl-vertical-slice` — plans + lexicon + ingest(文件/Tesseract) + study + exam + Web UI 最小闭环  
   - `pronunciation` — speech + Ollama 适配  
   - `huawei-client-skeleton` — 消费同一 OpenAPI 的薄客户端壳  

### 8.2 冲突规则

- 只扩展公开 API / 共享 Schema。
- 跨特性行为变更 → 补丁 `arch-foundation` 或新提案；禁止暗改他包持久化。
- 每特性写明：场景、验收标准、非目标。

## 9. 成功标准（MVP）

1. 用户可创建托福计划并看到基于内置词表的每日任务。
2. 可从本地文件与图片（Tesseract）导入词，确认后字段进入词库（五元组中缺失项显式可空/不完整）。
3. 背词（翻卡片或英选中义）与至少两种托福词汇题型模考可跑通并出报告。
4. 关闭 Ollama 时主路径仍可用；开启时发音特性可独立验收。
5. 仓库以 OpenSpec 管理上述特性，且 `arch-foundation` 先于并行特性落地。

## 10. 后续路线图（不在本 MVP 实现）

- 雅思 / 托业 / 六级计划模板（复用 `plans` 扩展）
- SRS、错题本强化、网页词源
- 华为端完善与（可选）局域网发现
- 更完整的托福题型与官方样态对齐

## 11. 决策记录摘要

| 决策 | 选择 |
|------|------|
| MVP 切片 | 托福垂直闭环 |
| 平台 | Windows 先；华为骨架并行 |
| Ollama | 复用 WSL，不重复安装 |
| 词源 | 内置 + 本地文件 + OCR（Tesseract 默认，Vision 可选） |
| 栈 | FastAPI + Web UI + SQLite |
| 背词 / 考试 | 背词基础模式；考试模拟托福词汇题型 |
| 架构 | 模块化单体 + Adapter 纪律 |
| 并行 OpenSpec | foundation → 托福切片 ∥ 发音 ∥ 华为骨架 |
| 词库字段 | 单词、音标、发音、解释（`definitions: list[str]`）、例句（`examples: list[str]`） |
