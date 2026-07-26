# Architecture Spec

## Requirement: Modular monolith boundaries
系统 SHALL 按 plans/lexicon/ingest/study/exam/progress/speech/adapters 分包；UI SHALL 只经 OpenAPI 访问。

## Requirement: Lexicon word schema
Word SHALL 包含 word, phonetic, audio, definitions (list of string), examples (list of string)。

## Requirement: Adapter isolation
领域代码 SHALL 依赖 OCR/Ollama Protocol；实现位于 adapters/。

## Requirement: Ollama single instance
系统 SHALL 通过 OLLAMA_HOST 连接已有 WSL Ollama；SHALL NOT 默认安装第二份 Windows Ollama。
