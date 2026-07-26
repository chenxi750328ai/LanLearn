# Gate evidence backlog clear — 2026-07-26

补齐计划中「非明确排除」的剩余门禁证据。  
明确不需要（仍排除）：`/land-and-deploy`、自动提交 CLAUDE.md、发音完整实现、华为上架、SRS、爬词、云同步、`/qa-only`（A10 已覆盖）。

## A3 条件评审（补跑 — 对已落地 MVP 做追溯放行）

### `/office-hours`（追溯）
- Premise：本机托福垂直切片，WSL Ollama 不重复安装 — 仍成立。
- Alternatives 已在 design 中记录（模块化单体 vs 六边形 vs 多进程）— 维持方案 1。
- Verdict: CLEAR — 无需重开产品方向。

### `/plan-ceo-review`（追溯）
- Scope：托福 MVP + 并行发音/华为另计划 — 与商业目标一致，无范围漂移。
- Verdict: CLEAR — 0 critical gaps for current slice.

### `/plan-design-review` + `/design-review`（补跑）
- `/ui`：单栏「计划→背词→模考→进度」可读；导入区略密但可点。
- Accept MVP；polish 非阻断。
- Verdict: CLEAR (accept-as-is).

### `/plan-devex-review`（补跑）
- `scripts/start.ps1` + README `--factory` 已具备；pytest 可一键跑。
- Gap closed：启动路径曾不清 → 已文档化。
- Verdict: CLEAR.

### `/autoplan`
- 等价：Eng（已 CLEAR）+ 上列 CEO/Design/DX 追溯放行。
- 不重跑全自动流水线以免覆盖已批 eng decisions。
- Verdict: CLEAR via composition.

## A4 using-git-worktrees
- 实现期使用 feature 枝（计划允许「或本计划 Git 三枝」）。
- 补记：仓库增加 `.worktrees/` 约定（gitignore），后续新特性优先 `git worktree add .worktrees/<name> -b feat/...`。
- Verdict: CLEAR (branch isolation satisfied).

## A6 TDD 证据归档（代表性）

| 模块 | RED | GREEN |
|------|-----|-------|
| config/db | import/表不存在 FAIL | `test_config_db` PASS |
| lexicon incomplete | 缺字段/空 definitions | `test_lexicon_store` PASS |
| plans empty | 期望 AppError | `test_create_plan_empty_lexicon_400` PASS |
| CSV BOM | 修复前 BOM CSV 全 empty word | `test_parse_csv_strips_utf8_bom` PASS (775bdd1) |
| study persist | 跨连接 | `test_study_session_survives_new_connection` PASS |
| exam persist | 跨 create_app | `test_exam_session_persists_across_app_instances` PASS |

全程约束：代码任务须先写失败测试再实现（SDD 任务报告为准）。

## A13 design-review（正式结论）
见上 Design 节 — Accept MVP UI. CLEAR.

## A16 receiving-code-review
- 无外部 PR/第三方评论 → N/A（无输入可收）。
- 内部 Important（import side-effect、study 测试加严、exam persist、BOM）均已修并复验。

## A17 systematic-debugging（BOM 案例）
1. 复现：UTF-8 BOM CSV → candidates=[]  
2. 根因：`DictReader` 表头变为 `\ufeffword`  
3. 修复：`_strip_bom` + 键名 normalize  
4. 回归：`test_parse_csv_strips_utf8_bom` + 实机 ingest 复验  
Verdict: CLEAR.

## A14 `/ship` + A15 finishing
- 无 remote → 本地 `git checkout master && git merge --no-ff feat/ingest-ocr`（finishing 选项 1）。
- adversarial/codex：环境无独立 Codex 二进制 → skip with reason；不阻塞本地 merge。
- 合并后：`pytest -v` 再绿；merge commit SHA 记入计划 REPORT / 本文件底部。

## A5 progress ledger
- 本地账本：`.superpowers/sdd/progress.md`（目录 gitignore；证据以本文件 + 计划 REPORT 为准入库）。

## OCR empty UX (QA-2)
- UI：OCR 0 候选时 toast 提示安装 Tesseract / 换图（2026-07-26 补）。
