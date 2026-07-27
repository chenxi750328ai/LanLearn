# architecture Specification

## Purpose
TBD - created by archiving change arch-foundation. Update Purpose after archive.
## Requirements
### Requirement: Modular monolith boundaries
系统 SHALL 按 plans/lexicon/ingest/study/exam/progress/speech/adapters 分包；UI SHALL 只经 OpenAPI 访问。

#### Scenario: Package layout exists
- **WHEN** 检查 `src/es_app/` 包结构
- **THEN** 存在 plans、lexicon、ingest、study、exam、progress、speech、adapters 分包

#### Scenario: UI uses HTTP API
- **WHEN** Web UI 加载数据
- **THEN** 仅通过 fetch/OpenAPI 路径访问，不直连 SQLite

### Requirement: Lexicon word schema
Word SHALL 包含 word, phonetic, audio, definitions (list of string), examples (list of string)。

#### Scenario: Required word field
- **WHEN** 创建词条缺少 `word`
- **THEN** 校验失败且不得进入完整学习池

### Requirement: Adapter isolation
领域代码 SHALL 依赖 OCR/Ollama Protocol；实现位于 adapters/。

#### Scenario: Domain does not import concrete OCR
- **WHEN** 审查 study/exam/plans 领域模块 import
- **THEN** 不直接依赖 tesseract 实现类，仅依赖协议/注入端口

### Requirement: Ollama single instance
系统 SHALL 通过 OLLAMA_HOST 连接已有 WSL Ollama；SHALL NOT 默认安装第二份 Windows Ollama。

#### Scenario: Speech unavailable without Ollama path
- **WHEN** 调用 `POST /speech/evaluate` 且发音未启用
- **THEN** 返回 503 且不触发本机静默安装第二份 Ollama

