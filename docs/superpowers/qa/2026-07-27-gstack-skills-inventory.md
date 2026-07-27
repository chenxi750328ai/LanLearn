# gstack skills inventory — 2026-07-27

## Install

- Source: `garrytan/gstack` @ `main` (tarball)
- Targets（双侧一致，各 **53**）:
  - Windows: `C:\Users\chenx\.cursor\skills\gstack-*`
  - WSL: `/home/cx/.cursor/skills/gstack-*`
- Helpers: `~/.claude/skills/gstack/bin/`（Win + WSL）
- 每份 `SKILL.md` 已注入 VC 注记（禁止自动 commit CLAUDE.md）

## Catalog (gstack-*)

autoplan, benchmark, benchmark-models, browse, canary, careful, codex, context-restore, context-save, cso, design-consultation, design-html, design-review, design-shotgun, devex-review, diagram, document-generate, document-release, freeze, gstack-upgrade, guard, health, investigate, ios-clean, ios-design-review, ios-fix, ios-qa, ios-sync, land-and-deploy, landing-report, learn, make-pdf, office-hours, open-gstack-browser, pair-agent, plan-ceo-review, plan-design-review, plan-devex-review, plan-eng-review, plan-tune, qa, qa-only, retro, review, scrape, setup-browser-cookies, setup-deploy, setup-gbrain, ship, skillify, spec, sync-gbrain, unfreeze

## LanLearn 执行策略

| Skill | 装入 | 本产品是否执行 |
|-------|------|----------------|
| `/qa` `/qa-only` `/ship` `/review` `/investigate` | 是 | **必做**（按计划 A 节） |
| `/plan-*` `/office-hours` `/spec` `/autoplan` `/design-review` | 是 | 范围变更时必做；MVP 追溯已记 |
| `/land-and-deploy` `/setup-deploy` `/canary` | 是（技能齐） | **禁止对 LanLearn 执行上云** — 无生产云主机/无托管部署管线（见计划） |
| iOS* | 是 | 本产品非 iOS — 可选忽略 |

## 复装

见仓库 `scripts/install-gstack-from-upstream.sh`（需先有 `/tmp/gstack-src`）。
