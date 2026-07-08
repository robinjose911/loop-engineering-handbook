import { defineConfig } from '@playwright/test';
import path from 'node:path';

// The Playwright project lives in tests/e2e; the repo root is two levels up.
const repoRoot = path.resolve(__dirname, '..', '..');

export default defineConfig({
  testDir: __dirname,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: process.env.CI ? [['github'], ['list']] : 'list',
  timeout: 30_000,
  use: {
    baseURL: 'http://127.0.0.1:4321',
  },
  // globalSetup regenerates placeholders (Python) and builds the preview
  // (build.mjs) before the server boots, so the render-check is self-contained
  // and a reused server still serves freshly built output.
  globalSetup: './globalSetup.ts',
  webServer: {
    command: 'node tools/preview/serve.mjs',
    cwd: repoRoot,
    url: 'http://127.0.0.1:4321',
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
    stdout: 'pipe',
    stderr: 'pipe',
  },
});
