import { test, expect } from '@playwright/test';
import { assertNoBrokenImages, assertNoDeadInternalLinks } from './helpers/render';

// Stage 3 integration test: every guide page renders with working images, links,
// and in-doc anchors; the canonical loop contract shows its six fields.

const PAGES = [
  '/docs/',
  '/docs/01-what-is-loop-engineering.html',
  '/docs/02-goal-and-loop-basics.html',
  '/docs/03-benefits.html',
  '/docs/04-risks-and-cost.html',
  '/docs/05-recommendations-and-tips.html',
  '/docs/the-loop-contract.html',
  '/docs/glossary.html',
];

test.describe('Stage 3: the guide', () => {
  for (const route of PAGES) {
    test(`${route} renders with no broken images or dead links/anchors`, async ({ page }) => {
      await page.goto(route);
      await expect(page.locator('h1').first()).toBeVisible();
      await assertNoBrokenImages(page);
      // Exercises the DOM-based anchor checker against the cross-doc #anchor
      // links (e.g. SOURCES.md#origin-and-lineage, 02...#the-durability-ladder).
      await assertNoDeadInternalLinks(page);
    });
  }

  test('the canonical loop contract shows all six fields', async ({ page }) => {
    await page.goto('/docs/the-loop-contract.html');
    const body = await page.locator('body').innerText();
    for (const field of ['Goal:', 'Context:', 'Constraints:', 'Done-when:', 'Evidence:', 'If-blocked:']) {
      expect(body, `contract should show ${field}`).toContain(field);
    }
  });

  test('docs embed real diagram images at their manifest sizes', async ({ page }) => {
    const checks: Array<[string, string, number, number]> = [
      ['/docs/01-what-is-loop-engineering.html', 'lineage.png', 1200, 600],
      ['/docs/02-goal-and-loop-basics.html', 'goal-vs-loop-flowchart.png', 1200, 800],
      ['/docs/the-loop-contract.html', 'anatomy-5-blocks.png', 1200, 700],
    ];
    for (const [route, file, w, h] of checks) {
      await page.goto(route);
      const img = page.locator(`img[src*="${file}"]`);
      await expect(img).toBeVisible();
      const dims = await img.evaluate((el) => ({
        w: (el as HTMLImageElement).naturalWidth,
        h: (el as HTMLImageElement).naturalHeight,
      }));
      expect(dims, `${file}`).toEqual({ w, h });
    }
  });
});
