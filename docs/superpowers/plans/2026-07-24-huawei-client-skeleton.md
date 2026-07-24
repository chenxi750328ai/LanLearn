# 华为客户端骨架（huawei-client-skeleton）— 后续计划入口

**Goal:** 交付消费同一 OpenAPI 的华为手机薄客户端壳，覆盖托福 MVP 主路径（计划 → 背词 → 模考 → 进度）；客户端仅经 HTTP 访问 FastAPI，不直连 SQLite、不直连 Ollama。外网访问经 Tailscale 私有组网，禁止公网裸端口转发。

**依赖：** `feat/arch-foundation` + `feat/toefl-core`（及 ingest-ocr）已合并；OpenAPI 契约与 `Word` / `ErrorBody` Schema 稳定；服务端默认 `ES_BIND=127.0.0.1`，联调时可临时 `0.0.0.0` + Tailnet ACL。

**非目标：**
- 华为应用市场上架、账号体系、云同步
- 在客户端内嵌 Ollama 或 Tesseract
- 重写后端业务逻辑或修改领域模块私有表
- 完整 UI  polish（骨架阶段以 API 闭环验收为主）

**下一步：** 单独开 `superpowers:writing-plans` 会话，选定 HarmonyOS / ArkUI 等技术栈并锁定屏幕与 API 映射 → `/plan-eng-review` → 自 `master` 切 `feat/huawei-client-skeleton` 执行。
