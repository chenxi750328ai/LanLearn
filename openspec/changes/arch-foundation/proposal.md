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
