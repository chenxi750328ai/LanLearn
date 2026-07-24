# 发音评测（pronunciation）— 后续计划入口

**Goal:** 实现完整发音评测闭环：用户对某词录音 → `speech` 收音频 → WSL Ollama 评测 → 返回分数/纠错 → 写入 `progress`；Ollama 不可用时主路径（背词/模考）不受影响。详见设计文档 §5.3。

**依赖：** `feat/arch-foundation` + `feat/toefl-core`（及已合并的 ingest-ocr）已落地；复用现有 `POST /speech/evaluate` 路由、`OllamaPort` 协议、`ES_DATA_DIR` / `OLLAMA_HOST` 配置与 `ErrorBody` 503 降级约定。

**非目标：**
- 替换或重复安装 Windows 原生 Ollama
- Vision OCR 增强（归独立小变更或本计划可选附录）
- 华为客户端 UI、云托管 API、多用户账号
- 完整托福听说读写套题

**下一步：** 单独开 `superpowers:writing-plans` 会话，产出带 Task 复选框的实现计划 → `/plan-eng-review` → 自 `master` 切 `feat/pronunciation` 执行。
