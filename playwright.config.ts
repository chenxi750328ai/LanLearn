import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
import os from "node:os";

const port = Number(process.env.ES_E2E_PORT || 18080);
const baseURL = `http://127.0.0.1:${port}`;
const dataDir =
  process.env.ES_E2E_DATA_DIR ||
  path.join(os.tmpdir(), `es_app_e2e_${process.pid}`);

export default defineConfig({
  testDir: "e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `python -m uvicorn es_app.main:create_app --factory --host 127.0.0.1 --port ${port}`,
    url: `${baseURL}/ui/`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      ...process.env,
      PYTHONPATH: path.resolve("src"),
      ES_DATA_DIR: dataDir,
      ES_BIND: "127.0.0.1",
    },
  },
});
