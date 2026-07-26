import { test, expect } from "@playwright/test";
import path from "node:path";
import { writeFileSync, mkdtempSync } from "node:fs";
import os from "node:os";

/**
 * System tests S-01..S-12 (plan Quality Assurance Gates §D).
 * Must not be satisfied by pytest/TestClient alone.
 */

test.describe.configure({ mode: "serial" });

test("S-02 S-03 S-04: UI title, redirect, docs", async ({ page, request }) => {
  await page.goto("/ui/");
  await expect(page).toHaveTitle("托福学习");
  await expect(page.getByRole("heading", { name: "托福学习" })).toBeVisible();

  const root = await request.get("/", { maxRedirects: 0 });
  expect([301, 302, 303, 307, 308]).toContain(root.status());
  expect(root.headers()["location"]).toContain("/ui/");

  const docs = await request.get("/docs");
  expect(docs.ok()).toBeTruthy();
});

test("S-05..S-08: plan → study → exam → progress", async ({ page }) => {
  await page.goto("/ui/");

  await page.getByRole("button", { name: "创建托福计划" }).click();
  await expect(page.locator("#plan-info")).toBeVisible();
  await expect(page.locator("#plan-info")).toContainText("toefl");
  await expect(page.locator("#btn-start-study")).toBeEnabled();
  await expect(page.locator("#btn-start-exam")).toBeEnabled();

  await page.getByRole("button", { name: "开始今日背词" }).click();
  await expect(page.locator("#study-area")).toBeVisible();
  await expect(page.locator("#study-word")).not.toBeEmpty();
  await page.locator("#study-options button").first().click();
  await expect(page.locator("#study-feedback")).toBeVisible({ timeout: 10_000 });
  await expect(page.locator("#study-feedback")).toContainText(/正确|正确答案/);

  await page.getByRole("button", { name: "开始模考（2 题）" }).click();
  await expect(page.locator("#exam-area")).toBeVisible();
  const questions = page.locator("#exam-form fieldset");
  await expect(questions).toHaveCount(2);
  const count = await questions.count();
  for (let i = 0; i < count; i++) {
    await questions.nth(i).locator('input[type="radio"]').first().check();
  }
  await page.getByRole("button", { name: "提交答卷" }).click();
  await expect(page.locator("#exam-result")).toBeVisible();
  await expect(page.locator("#exam-result")).toContainText("得分");

  await page.getByRole("button", { name: "刷新进度" }).click();
  await expect(page.locator("#progress-info")).toBeVisible();
  await expect(page.locator("#progress-info")).toContainText("背词");
  await expect(page.locator("#progress-info")).toContainText("模考");
});

test("S-09: CSV upload preview + confirm", async ({ page }) => {
  await page.goto("/ui/");
  const csv = path.resolve("tests/fixtures/words_sample.csv");
  await page.locator("#import-file").setInputFiles(csv);
  await page.getByRole("button", { name: "上传预览" }).click();
  await expect(page.locator("#import-preview")).toContainText("候选");
  await expect(page.locator("#import-preview")).toContainText("diligent");
  await expect(page.locator("#btn-import-confirm")).toBeEnabled();
  await page.getByRole("button", { name: "确认入库" }).click();
  await expect(page.locator("#toast")).toContainText("已入库", { timeout: 10_000 });
});

test("S-10: OCR empty degradation (no white screen)", async ({ page }) => {
  await page.goto("/ui/");
  const dir = mkdtempSync(path.join(os.tmpdir(), "es-ocr-"));
  // Minimal valid 1x1 PNG
  const png = Buffer.from(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
    "base64",
  );
  const imgPath = path.join(dir, "blank.png");
  writeFileSync(imgPath, png);

  await page.locator("#import-image").setInputFiles(imgPath);
  await page.getByRole("button", { name: "OCR 预览" }).click();
  await expect(page.locator("#import-preview")).toBeVisible({ timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "托福学习" })).toBeVisible();
  // Without Tesseract: empty candidates + toast; with Tesseract: may find nothing on blank PNG
  await expect(page.locator("#toast")).toBeVisible({ timeout: 10_000 });
});

test("S-11 S-12: speech 503; no unexpected 5xx on UI load", async ({
  page,
  request,
}) => {
  const speech = await request.post("/speech/evaluate", {
    failOnStatusCode: false,
  });
  expect(speech.status()).toBe(503);

  const errors: string[] = [];
  page.on("pageerror", (err) => errors.push(String(err)));
  page.on("response", (res) => {
    if (res.status() >= 500 && !res.url().includes("/speech/")) {
      errors.push(`5xx ${res.status()} ${res.url()}`);
    }
  });
  await page.goto("/ui/");
  await page.getByRole("button", { name: "创建托福计划" }).click();
  await expect(page.locator("#plan-info")).toBeVisible();
  expect(errors, errors.join("\n")).toEqual([]);
});
