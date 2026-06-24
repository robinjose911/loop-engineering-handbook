import { test, expect } from '@playwright/test';
import { assertNoBrokenImages, assertNoDeadInternalLinks } from './helpers/render';

// Stage 6 integration test: the README hero renders fully, the buttons navigate,
// and every quote-card slot is present + attributed.

test.describe('Stage 6: the README hero', () => {
  test('banner is real and the hero renders with no broken local images or dead links', async ({ page }) => {
    await page.goto('/');
    const banner = page.locator('img[src="assets/banner.png"]');
    await expect(banner).toBeVisible();
    const dims = await banner.evaluate((el) => ({
      w: (el as HTMLImageElement).naturalWidth,
      h: (el as HTMLImageElement).naturalHeight,
    }));
    expect(dims).toEqual({ w: 1280, h: 320 }); // real asset at manifest size
    await assertNoBrokenImages(page); // local imgs only; shields.io badges skipped
    await assertNoDeadInternalLinks(page);
  });

  test('the "Loop in 30 seconds" block is visible with the contract', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'Loop in 30 seconds' })).toBeVisible();
    const pre = page.locator('pre', { hasText: 'Goal:' }).first();
    await expect(pre).toBeVisible();
    expect(await pre.innerText()).toContain('If-blocked:');
  });

  test('the three buttons navigate to docs / library / examples', async ({ page }) => {
    const nav = [
      ['Learn loop engineering', '/docs/'],
      ['Copy a loop', '/library/'],
      ['See one run', '/examples/'],
    ];
    for (const [label, expectedPath] of nav) {
      await page.goto('/');
      await page.getByRole('link', { name: new RegExp(label) }).first().click();
      await expect(page).toHaveURL(new RegExp(`${expectedPath.replace('/', '\\/')}(index\\.html)?$`));
      await expect(page.locator('h1').first()).toBeVisible();
    }
  });

  test('all five quote-cards render and link to their source posts', async ({ page }) => {
    await page.goto('/');
    const cards = page.locator('img[src^="assets/quote-cards/"]');
    await expect(cards).toHaveCount(5);
    for (let i = 0; i < 5; i++) {
      const img = cards.nth(i);
      await expect(img).toBeVisible();
      // attribution lives in the alt text; the image links to its source post
      expect((await img.getAttribute('alt'))?.length || 0).toBeGreaterThan(3);
      const href = await img.locator('xpath=ancestor::a').first().getAttribute('href');
      expect(href).toMatch(/^https?:\/\//);
    }
  });
});
