# RCA：浏览器 / Playwright 系统测为何在落地时遗漏

日期：2026-07-26  
范围：计划已要求「禁止仅 pytest 宣称网页可用」，但仓库长期无 Playwright，系统验收曾被稀释。

## 结论（根因链）

遗漏不在「完全没写要求」，而在 **计划把浏览器验收写成技能步骤（`/qa`），没有写成可提交的工程交付物（Playwright 套件）**，再叠加 **实现代理把 Task 完成定义收窄为 pytest**，以及 **Task 14 用「路径勾选表 + 人工/MCP 点一点」顶替可重复系统测**。

## 时间线（仓库证据）

| 时间 | 事件 | 问题 |
|------|------|------|
| 2026-07-24 `05feb1c` | 初版 plan：Goal 写「本机浏览器验收」；Task 12 写「浏览器打开走通」；Tech Stack **只有 pytest**，无 Playwright 任务 | 验收依赖人工打开，无自动化资产 |
| 2026-07-24 `a404195` | eng-review：写入 `/qa` 时机；硬门多为 **API/pytest**（empty plan、persist 等） | `/qa` 是流程名，不是 `e2e/*.spec.ts` |
| Tasks 0–13（SDD） | 子代理 brief 以 pytest RED→GREEN + commit 收尾；Task 12 无「安装 Playwright」步骤 | **第一次遗漏点：实现环只认 pytest** |
| 用户指出打不开网页 | 代理承认「主要靠 pytest，没起服务、没跑 `/qa`」 | **第二次遗漏点：宣称完成早于 A9/A10** |
| 2026-07-25 `4adf011` | 补写 Quality Assurance Gates A0–A17 + Task 14；明确禁止 TestClient 代替 `/qa` | 仍未规定「必须提交 Playwright 工程」 |
| Task 14 `9653211` | `mvp-verification.md` 勾选 12 路径；工具为起服 + HTTP +（文档称）browser | **第三次遗漏点：A10 CLEAR 无 `playwright test` 产物、无 `e2e/` 入库** |
| 2026-07-26 | 本地 merge + 门禁 CLEAR 文档 | 第四次：把「有 QA 报告」当成「有系统测试套件」 |

## 遗漏落点（精确到流程节点）

1. **writing-plans / 计划结构（源头缺口）**  
   - 有：A10 = gstack `/qa`；§D 十二条路径；「禁止 pytest 代替 `/qa`」。  
   - 无：Task「Create `e2e/` + `npx playwright test`」；通过判据未要求仓库内可重复跑的系统测命令。  
   - Tech Stack 未列入 Playwright → 实现代理不会主动加依赖。

2. **subagent-driven-development（执行漂移）**  
   - 每个业务 Task 的 Done = pytest 绿 + commit。  
   - Task 12「浏览器闭环」被做成静态页 + 口头/事后人工打开，**没有系统测任务卡**。

3. **verification-before-completion（被误用为终点）**  
   - A9 要求 pytest + 起服 + HTTP 探活。  
   - 代理易在 A9 后停住；计划虽写「然后再跑 `/qa`」，但早期会话未执行。

4. **Task 14 / A10 `/qa`（验收降级）**  
   - `/qa` 技能允许 Cursor browser / CDP；本机 gstack 注记甚至写「不需要浏览器二进制」。  
   - 产出是 markdown 勾选，**不是** CI 可跑的 Playwright。  
   - Medium OCR toast 曾 defer，说明系统测未工程化强制回归。

5. **`/ship` / finishing（假绿放行）**  
   - F 节勾选依赖「A10 报告存在」，未检查 `npm run test:e2e`。  
   - 本地 merge 时 REPORT 将 Browser QA 标 CLEAR → **流程文件认可了降级证据**。

## 与「计划里早就有要求」的对齐说明

| 计划原意 | 实际落地 | 差距 |
|----------|----------|------|
| 禁止仅 pytest 宣称可用 | 曾发生（用户打断前） | 执行违纪 |
| 必须浏览器 `/qa` §D | 有 verification 勾选表 | 无自动化、难回归 |
| （隐含）系统测 | 无 Playwright | **计划未点名工具 → 代理选最省事路径** |

用户今日明确：**必须集成/系统测 + Playwright 类工具最终验证** → 属于把原 A10 从「技能仪式」升级为「工程硬门」。

## 纠正措施（本分支）

- 新增 `e2e/` + Playwright；`npm run test:e2e` 覆盖 §D 主路径。  
- 计划 A9/A10/A14/F 节改为：**pytest（L1/L2）+ Playwright（L3）+ `/qa` 报告** 三证齐全才可 CLEAR。  
- 禁止仅用 MCP 点一次或 HTTP 探活勾掉 A10。
