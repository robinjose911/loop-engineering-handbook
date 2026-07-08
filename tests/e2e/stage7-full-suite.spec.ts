import { test, expect } from '@playwright/test';
import { assertNoBrokenImages } from './helpers/render';

// Stage 7 integration test: a whole-repo crawl from the README. Follow every
// internal link transitively; every reachable HTML page renders with no broken
// images, and every followed internal link resolves (no 404s). The per-stage
// specs (re-run alongside this one) cover anchors + page-specific assertions.

test.describe('Stage 7: whole-repo integrity', () => {
  test('crawl from README: no broken images, no dead internal links anywhere', async ({ page }) => {
    test.setTimeout(120_000);
    const origin = 'http://127.0.0.1:4321';
    const seen = new Set<string>();
    const dead: string[] = [];
    const queue = ['/'];

    while (queue.length) {
      const path = queue.shift()!;
      const key = new URL(path, origin).toString().split('#')[0];
      if (seen.has(key)) continue;
      seen.add(key);

      const resp = await page.request.get(key);
      if (!resp.ok()) {
        dead.push(`${key} -> HTTP ${resp.status()}`);
        continue;
      }
      const ctype = resp.headers()['content-type'] || '';
      if (!ctype.includes('text/html')) continue; // assets (css/json/png/...) just need 200

      await page.goto(key);
      await assertNoBrokenImages(page);

      const hrefs = await page
        .locator('a[href]')
        .evaluateAll((els) => els.map((e) => e.getAttribute('href') || ''));
      for (const href of hrefs) {
        if (!href || /^(https?:)?\/\//i.test(href) || /^(mailto:|tel:|data:)/i.test(href)) continue;
        const targetPath = href.split('#')[0];
        if (!targetPath) continue;
        const target = new URL(targetPath, key).toString();
        if (target.startsWith(origin) && !seen.has(target)) {
          queue.push(target.replace(origin, ''));
        }
      }
    }

    expect(dead, `dead internal links across the crawl:\n${dead.join('\n')}`).toEqual([]);
    // README + 8 docs + library index + 17 cards + examples index + 7 example READMEs + ...
    expect(seen.size, 'crawl should reach the whole repo').toBeGreaterThan(30);
  });
});
