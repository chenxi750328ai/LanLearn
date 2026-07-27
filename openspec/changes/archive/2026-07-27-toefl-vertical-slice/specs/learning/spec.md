# Learning Spec (delta)

## ADDED Requirements

### Requirement: TOEFL plan creation
系统 SHALL 接受 `exam_type=toefl` 与 `daily_quota`，将完整词条按日切分并持久化。

#### Scenario: Create plan with quota
- **WHEN** 客户端 POST `/plans` 且 `exam_type=toefl`、`daily_quota=5`、词库非空
- **THEN** 返回含多日切片的计划且可持久化查询

#### Scenario: Empty lexicon rejected
- **WHEN** 词库无完整词条时创建计划
- **THEN** 返回 400 且 code 表示 empty_lexicon

### Requirement: Built-in lexicon seed
应用启动 SHALL 从 `builtin_toefl.json` 种子词库（≥20 完整词条），已存在则跳过。

#### Scenario: Seed on first boot
- **WHEN** 空库首次 `create_app`
- **THEN** 完整词条数量 ≥ 20

### Requirement: Study session
系统 SHALL 支持 flashcard 与 mcq 背词模式；会话状态 SHALL 存 SQLite 并可跨进程续答。

#### Scenario: MCQ answer persists
- **WHEN** 创建 study session 并提交一题答案后新开连接
- **THEN** 仍可基于同一 session id 继续/查询

### Requirement: Exam session
系统 SHALL 生成 synonym_mcq 与 contextual_blank 题型；提交后写入 progress_events 并返回得分报告。

#### Scenario: Submit exam returns score
- **WHEN** 开始模考并提交答卷
- **THEN** 响应含 score/total 与 wrong_word_ids

### Requirement: Progress summary
`GET /progress/summary` SHALL 返回 study/exam 统计与 weak_word_ids（错次降序，最多 20）。

#### Scenario: Summary aggregates
- **WHEN** 已有 study 与 exam 事件
- **THEN** summary 含 study_answered、exam_sessions、weak_word_ids

### Requirement: Speech stub
`POST /speech/evaluate` SHALL 返回 503，code=`ollama_unavailable`，直至发音计划实现。

#### Scenario: Speech stub 503
- **WHEN** POST `/speech/evaluate`
- **THEN** HTTP 503 且业务 code 为 ollama_unavailable

### Requirement: UI mount
静态 UI SHALL 挂载于 `/ui/`；API 路由 SHALL 不被静态文件遮蔽。

#### Scenario: UI and API coexist
- **WHEN** GET `/ui/` 与 GET `/plans`（或等价 API）
- **THEN** `/ui/` 返回页面且 API 不被静态挂载遮蔽
