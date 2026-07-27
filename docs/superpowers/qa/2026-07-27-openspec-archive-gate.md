# OpenSpec archive readiness — 2026-07-27

**规则：** 未满足计划 §J 全勾前，**禁止** `openspec archive` / 归档 `arch-foundation`、`toefl-vertical-slice`。

## §J 勾选（归档前）

- [x] 技能齐套：Win+WSL `gstack-*` = 53（inventory 文档）
- [x] 计划齐套：A–J 已写 land-and-deploy 理由、Playwright、远程 ship、归档门禁
- [x] 质量三证：pytest 34 + Playwright 5 + `/qa`（见 `2026-07-27-full-quality-gates.md`）
- [x] A12 review：Playwright 合入差分已审（同文件）
- [x] A14：local merge + `origin/master` push（`7eac021` 起）
- [x] 无未修 Critical/High（OCR toast 已补）
- [ ] **用户书面确认「允许归档」** ← 最后一闸；未确认不得 archive

## `/land-and-deploy` 摘要

装了技能，但不对本产品执行：无云生产、无 `/setup-deploy` 目标；本机+Tailscale ≠ land-and-deploy。

## 归档命令（仅用户确认后）

```powershell
openspec archive arch-foundation
openspec archive toefl-vertical-slice
```

（以本机 OpenSpec CLI 实际子命令为准。）
