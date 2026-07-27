# toefl-vertical-slice

## Why
在 arch-foundation 骨架上打通托福学习闭环：计划 → 词库 → 背词 → 模考 → 进度，并提供最小 Web UI 入口。

## What Changes
- `plans`：创建托福计划、按日切分词表
- `lexicon`：内置托福词库种子（≥20 词）、词条查询
- `study`：背词会话（flashcard / mcq），SQLite 持久化
- `exam`：托福词汇题型（同义选择、语境填空），提交计分
- `progress`：背词/考试事件聚合与薄弱词
- `main`：FastAPI 装配、API 路由、`/ui` 静态页、`/` 重定向
- `/speech/evaluate` 503 桩（Ollama 未就绪时降级）

## Non-Goals
- 完整发音评测（见 pronunciation 计划）
- 华为客户端骨架（见 huawei-client 计划）
- ingest 文件/OCR 导入（见 ingest-ocr 枝）
- SRS、多用户、云同步、公网裸暴露
