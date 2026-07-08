import { test, expect } from '@playwright/test';
import { assertNoBrokenImages, assertNoDeadInternalLinks } from './helpers/render';

// Stage 5 integration test: all 7 examples render with charts, resolvable
// artifacts, visible prompts, and the required teaching labels.

const EXAMPLES = [
  '1-overnight-217-review',
  '2-two-loops-one-repo',
  '3-claim-ledger-security',
  '4-reproduce-before-fix',
  '5-ad-spend-reconciliation',
  '6-rfp-questionnaire-pack',
  '7-deliverability-rescue',
];
const XLSX = {
  '5-ad-spend-reconciliation': 'reconciliation.xlsx',
  '6-rfp-questionnaire-pack': 'ANSWER_PACK.xlsx',
};

test.describe('Stage 5: the worked examples', () => {
  test('the index lists 7 examples with working links', async ({ page }) => {
    await page.goto('/examples/');
    await expect(page.locator('h1').first()).toContainText('worked examples');
    const rows = await page.locator('table tbody tr').count();
    expect(rows).toBe(7);
    await assertNoBrokenImages(page); // the 3 summary charts
    await assertNoDeadInternalLinks(page);
  });

  for (const slug of EXAMPLES) {
    test(`${slug} renders with chart, prompt, labels, resolvable artifacts`, async ({ page }) => {
      await page.goto(`/examples/${slug}/`);
      await expect(page.locator('h1').first()).toBeVisible();

      // at least one chart present + all images load
      expect(await page.locator('img[src*="/assets/charts/"]').count()).toBeGreaterThanOrEqual(1);
      await assertNoBrokenImages(page);

      // copy-paste prompt block visible with the contract
      const pre = page.locator('pre', { hasText: 'Goal:' }).first();
      await expect(pre).toBeVisible();
      expect(await pre.innerText()).toContain('Done-when:');

      // teaching label present (defensive frame on #3)
      const body = (await page.locator('body').innerText()).toLowerCase();
      expect(body).toContain('reconstruction');
      if (slug === '3-claim-ledger-security') expect(body).toContain('defensive');

      // every artifact link (csv/jsonl/xlsx/md) resolves
      await assertNoDeadInternalLinks(page);

      // the .xlsx link, where applicable, resolves to a real workbook
      const xlsx = (XLSX as Record<string, string>)[slug];
      if (xlsx) {
        const resp = await page.request.get(`http://127.0.0.1:4321/examples/${slug}/${xlsx}`);
        expect(resp.ok()).toBeTruthy();
        const buf = await resp.body();
        expect(buf[0]).toBe(0x50); // PK zip magic
        expect(buf[1]).toBe(0x4b);
      }
    });
  }
});
