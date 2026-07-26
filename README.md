# es — English Study

本机英语学习（托福 MVP）。API: FastAPI；UI: `static/`；数据: `ES_DATA_DIR`；Ollama: `OLLAMA_HOST`（WSL）。

规格: `docs/superpowers/specs/2026-07-24-english-learning-design.md`  
OpenSpec: `openspec/changes/`  
计划: `docs/superpowers/plans/2026-07-24-toefl-mvp-foundation.md`

## 启动（推荐）

在仓库根目录 PowerShell：

```powershell
.\scripts\start.ps1
```

然后浏览器打开：**http://127.0.0.1:8000/ui/**  
（不要双击 `static/index.html`，必须走 HTTP；根路径 `/` 会重定向到 `/ui/`）

等价手动命令：

```powershell
$env:PYTHONPATH = "$PWD\src"
$env:ES_DATA_DIR = "$env:USERPROFILE\.es_app"
python -m uvicorn es_app.main:create_app --factory --host 127.0.0.1 --port 8000
```

API 文档: http://127.0.0.1:8000/docs

## 测试

```powershell
$env:PYTHONPATH = "$PWD\src"
pytest -v
```

E2E 使用 `TestClient(create_app())`，不依赖模块级 `app`。
