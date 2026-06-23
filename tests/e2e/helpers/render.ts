import { type Page, expect } from '@playwright/test';

// Backbone render-check helpers, reused by every stage spec.

/**
 * Assert every <img> on the page actually loaded (naturalWidth > 0). Waits for
 * each image's load/error event first so the check is not racy. Placeholders
 * count as loaded images -- that is the point of Stage 0's stub generator.
 */
export async function assertNoBrokenImages(
  page: Page,
  { perImageTimeoutMs = 8000 }: { perImageTimeoutMs?: number } = {},
): Promise<void> {
  const broken: string[] = await page.evaluate(async (timeoutMs) => {
    const imgs = Array.from(document.images);
    await Promise.all(
      imgs.map((img) =>
        img.complete
          ? Promise.resolve()
          : new Promise<void>((resolve) => {
              const done = () => resolve();
              img.addEventListener('load', done, { once: true });
              img.addEventListener('error', done, { once: true });
              // Bound the wait so a lazy / never-resolving image surfaces as a
              // clear "broken" finding instead of hanging to the test timeout.
              setTimeout(done, timeoutMs);
            }),
      ),
    );
    return imgs
      // Only assert OUR assets load; external images (e.g. shields.io badges)
      // are third-party CDNs, exempt like the external-link allowlist.
      .filter((img) => !/^(https?:)?\/\//i.test(img.getAttribute('src') || ''))
      .filter((img) => !(img.naturalWidth > 0))
      .map((img) => img.getAttribute('src') || '(no src)');
  }, perImageTimeoutMs);
  expect(broken, `broken images on ${page.url()}: ${JSON.stringify(broken)}`).toEqual([]);
}

/**
 * Crawl every relative <a href> on the page; assert each target resolves
 * (HTTP 200 in the preview server) and, when the href carries a #anchor, that
 * an element with that id/name actually exists on the target page (checked via
 * a real DOM lookup, not a regex over raw HTML). External links
 * (http/https/mailto/tel) are skipped here -- they are covered by the
 * link-checker in Stage 7.
 */
export async function assertNoDeadInternalLinks(page: Page): Promise<void> {
  const hrefs: string[] = await page
    .locator('a[href]')
    .evaluateAll((els) => els.map((e) => e.getAttribute('href') || ''));
  const current = page.url();
  const dead: string[] = [];
  let probe: Page | null = null;

  try {
    for (const href of hrefs) {
      if (!href) continue;
      if (/^([a-z][a-z0-9+.-]*:)?\/\//i.test(href)) continue; // absolute / protocol-relative
      if (/^(mailto:|tel:|data:)/i.test(href)) continue;

      const hashIdx = href.indexOf('#');
      const pathPart = hashIdx >= 0 ? href.slice(0, hashIdx) : href;
      const anchor = hashIdx >= 0 ? href.slice(hashIdx + 1) : '';

      const targetUrl = pathPart === '' ? current : new URL(pathPart, current).toString();
      const resp = await page.request.get(targetUrl);
      if (!resp.ok()) {
        dead.push(`${href} -> HTTP ${resp.status()}`);
        continue;
      }
      if (anchor) {
        if (!probe) probe = await page.context().newPage();
        await probe.goto(targetUrl);
        const found = await probe.evaluate((id) => {
          const esc = (window as unknown as { CSS: typeof CSS }).CSS.escape(id);
          return (
            !!document.getElementById(id) ||
            !!document.querySelector(`[name="${esc}"]`)
          );
        }, anchor);
        if (!found) dead.push(`${href} -> missing anchor #${anchor}`);
      }
    }
  } finally {
    if (probe) await probe.close();
  }
  expect(dead, `dead internal links on ${current}:\n${dead.join('\n')}`).toEqual([]);
}

/** Assert a table (by selector) has exactly n body rows. */
export async function assertTableRows(page: Page, selector: string, n: number): Promise<void> {
  await expect(page.locator(`${selector} tbody tr`)).toHaveCount(n);
}
