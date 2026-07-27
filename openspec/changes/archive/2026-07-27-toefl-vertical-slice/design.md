# toefl-vertical-slice — Design

## 应用装配

- `create_app()` 启动时 `init_db` + `seed_builtin_toefl`
- 各 router 经 `dependency_overrides` 注入真实 Service
- 挂载顺序：先 `include_router` 全部 API，再 `mount("/ui", StaticFiles)`
- `GET /` → 307 重定向 `/ui/`

## 学习闭环

```text
POST /plans → GET /lexicon/words
     ↓
POST /study/sessions → POST .../answer
     ↓
POST /exam/sessions → POST .../submit
     ↓
GET /progress/summary
```

## 持久化

- study/exam 会话与 progress_events 存 SQLite（`ES_DATA_DIR/es.sqlite3`）
- 进程重启后同一 data_dir 可续答

## 降级

- `/speech/evaluate` 固定 503 `ollama_unavailable`，背词与考试不受影响
