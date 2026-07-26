# Playwright system tests — 2026-07-26

Branch: merged to `master` via `0850bf7` (`feat/playwright-system-tests`)

## Command

```powershell
npm ci
npx playwright install chromium
$env:CI='1'; npm run test:e2e
```

## Result

```text
5 passed (e2e/system.spec.ts)
- S-02 S-03 S-04: UI title, redirect, docs
- S-05..S-08: plan → study → exam → progress
- S-09: CSV upload preview + confirm
- S-10: OCR empty degradation (no white screen)
- S-11 S-12: speech 503; no unexpected 5xx on UI load
```

S-01（start.ps1）由 Playwright `webServer` 等价起服覆盖（uvicorn factory）。

## Gate impact

A9/A10 现要求本命令与 `/qa` 报告双证；此前仅 markdown 勾选不算 CLEAR（见 omission RCA）。
