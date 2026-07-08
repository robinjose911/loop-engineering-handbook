import { test, expect } from '@playwright/test';
import { assertNoBrokenImages, assertNoDeadInternalLinks } from './helpers/render';

// Stage 4 integration test: the library index, every card link, and the
// agent-readable files all resolve and parse.

test.describe('Stage 4: the prompt library', () => {
  test('the index lists every card and has no dead links', async ({ page }) => {
    await page.goto('/library/');
    await expect(page.locator('h1').first()).toContainText('prompt library');
    await assertNoBrokenImages(page);
    // resolves every card link, example link, and catalog/schema/llms link
    await assertNoDeadInternalLinks(page);

    // row count == catalog card count
    const catalog = await (await page.request.get('/library/catalog.json')).json();
    const cardRows = await page.locator('table a[href^="loops/"]').count();
    expect(cardRows).toBe(catalog.count);
    expect(catalog.count).toBeGreaterThanOrEqual(15);
  });

  test('catalog.json and llms.txt are served and catalog parses in-browser', async ({ page }) => {
    await page.goto('/'); // establish the localhost origin for the in-browser fetch
    const catResp = await page.request.get('http://127.0.0.1:4321/library/catalog.json');
    expect(catResp.ok()).toBeTruthy();
    const parsed = await page.evaluate(async () => {
      const r = await fetch('/library/catalog.json');
      return JSON.parse(await r.text());
    });
    expect(Array.isArray(parsed.cards)).toBeTruthy();
    expect(parsed.cards.length).toBe(parsed.count);

    const llmsResp = await page.request.get('http://127.0.0.1:4321/library/llms.txt');
    expect(llmsResp.ok()).toBeTruthy();
    expect((await llmsResp.text()).length).toBeGreaterThan(100);
  });

  test('three cards render their copy-paste prompt block with contract fields', async ({ page }) => {
    const cards = [
      '/library/loops/engineering/overnight-217-review.html',
      '/library/loops/operations/ad-spend-reconciliation.html',
      '/library/loops/data/csv-normalizer.html',
    ];
    for (const route of cards) {
      await page.goto(route);
      const pre = page.locator('pre').first();
      await expect(pre).toBeVisible();
      const text = await pre.innerText();
      for (const field of ['Goal:', 'Done-when:', 'Evidence:', 'If-blocked:']) {
        expect(text, `${route} prompt block should contain ${field}`).toContain(field);
      }
      await assertNoDeadInternalLinks(page);
    }
  });
});
