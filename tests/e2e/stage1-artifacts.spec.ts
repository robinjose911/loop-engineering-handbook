import { test, expect } from '@playwright/test';
import { assertNoBrokenImages, assertNoDeadInternalLinks } from './helpers/render';

// Stage 1 integration test: every example's generated artifacts page renders and
// every artifact link (csv / jsonl / xlsx / md / inputs) resolves in the preview.

const EXAMPLES = [
  '1-overnight-217-review',
  '2-two-loops-one-repo',
  '3-claim-ledger-security',
  '4-reproduce-before-fix',
  '5-ad-spend-reconciliation',
  '6-rfp-questionnaire-pack',
  '7-deliverability-rescue',
];

test.describe('Stage 1: synthetic artifacts', () => {
  for (const slug of EXAMPLES) {
    test(`${slug}: artifacts page renders with resolvable links`, async ({ page }) => {
      await page.goto(`/examples/${slug}/artifacts.html`);
      await expect(page.locator('h1').first()).toBeVisible();
      // the artifacts table must list at least one artifact
      const links = page.locator('table a[href]');
      expect(await links.count()).toBeGreaterThan(0);
      await assertNoBrokenImages(page);
      await assertNoDeadInternalLinks(page); // GETs every csv/jsonl/xlsx/md target, asserts 200
    });
  }

  test('headline.json is served and parses for every example', async ({ page }) => {
    for (const slug of EXAMPLES) {
      const resp = await page.request.get(`/examples/${slug}/headline.json`);
      expect(resp.ok(), `${slug}/headline.json should be 200`).toBeTruthy();
      const data = JSON.parse(await resp.text());
      expect(data.title, `${slug} headline has a title`).toBeTruthy();
    }
  });

  test('the two .xlsx workbooks are served with a non-zero body', async ({ page }) => {
    const xlsx = [
      '5-ad-spend-reconciliation/reconciliation.xlsx',
      '6-rfp-questionnaire-pack/ANSWER_PACK.xlsx',
    ];
    for (const rel of xlsx) {
      const resp = await page.request.get(`/examples/${rel}`);
      expect(resp.ok(), `${rel} should be 200`).toBeTruthy();
      const body = await resp.body();
      expect(body.byteLength, `${rel} should be non-empty`).toBeGreaterThan(1000);
      // .xlsx is a zip -> starts with PK
      expect(body[0]).toBe(0x50);
      expect(body[1]).toBe(0x4b);
    }
  });
});
