# Learning Spec

## Requirement: TOEFL plan creation
系统 SHALL 接受 `exam_type=toefl` 与 `daily_quota`，将完整词条按日切分并持久化。

## Requirement: Built-in lexicon seed
应用启动 SHALL 从 `builtin_toefl.json` 种子词库（≥20 完整词条），已存在则跳过。

## Requirement: Study session
系统 SHALL 支持 flashcard 与 mcq 背词模式；会话状态 SHALL 存 SQLite 并可跨进程续答。

## Requirement: Exam session
系统 SHALL 生成 synonym_mcq 与 contextual_blank 题型；提交后写入 progress_events 并返回得分报告。

## Requirement: Progress summary
`GET /progress/summary` SHALL 返回 study/exam 统计与 weak_word_ids（错次降序，最多 20）。

## Requirement: Speech stub
`POST /speech/evaluate` SHALL 返回 503，code=`ollama_unavailable`，直至发音计划实现。

## Requirement: UI mount
静态 UI SHALL 挂载于 `/ui/`；API 路由 SHALL 不被静态文件遮蔽。
