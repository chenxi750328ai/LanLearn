# es — English Study

本机英语学习（托福 MVP）。API: FastAPI；UI: `static/`；数据: `ES_DATA_DIR`；Ollama: `OLLAMA_HOST`（WSL）。

规格: `docs/superpowers/specs/2026-07-24-english-learning-design.md`
OpenSpec: `openspec/changes/`

## 启动

```bash
uvicorn es_app.main:create_app --factory --app-dir src --reload --host 127.0.0.1 --port 8000
```

E2E 测试使用 `TestClient(create_app())`，不依赖模块级 `app`。
