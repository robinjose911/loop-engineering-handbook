import { test, expect } from '@playwright/test';
import { assertNoBrokenImages, assertNoDeadInternalLinks } from './helpers/render';

// Stage 0 integration test: the empty-but-stubbed repo renders with zero broken
// images and zero dead internal links.

test.describe('Stage 0: scaffold + preview harness', () => {
  test('README skeleton renders with a title', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1').first()).toContainText('Loop Engineering Handbook');
  });

  test('the banner slot shows the placeholder at its declared dimensions', async ({ page }) => {
    await page.goto('/');
    const banner = page.locator('img[src="assets/banner.png"]');
    await expect(banner).toBeVisible();
    const dims = await banner.evaluate((el) => ({
      w: (el as HTMLImageElement).naturalWidth,
      h: (el as HTMLImageElement).naturalHeight,
    }));
    expect(dims).toEqual({ w: 1280, h: 320 }); // matches assets/manifest.json
  });

  test('README has no broken images', async ({ page }) => {
    await page.goto('/');
    await assertNoBrokenImages(page);
  });

  test('README has no dead internal links', async ({ page }) => {
    await page.goto('/');
    await assertNoDeadInternalLinks(page);
  });

  test('the section index pages render cleanly', async ({ page }) => {
    for (const route of ['/docs/', '/library/', '/examples/']) {
      await page.goto(route);
      await expect(page.locator('h1').first()).toBeVisible();
      await assertNoBrokenImages(page);
      await assertNoDeadInternalLinks(page);
    }
  });
});
