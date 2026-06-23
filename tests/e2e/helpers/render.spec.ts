import { test, expect } from '@playwright/test';
import { assertNoBrokenImages, assertNoDeadInternalLinks } from './render';

// Self-test for the backbone helpers (Stage 0.5): each helper must correctly
// pass on a good page and fail on a deliberately broken one.

// 1x1 transparent PNG.
const GOOD_PNG =
  'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==';

test.describe('render helpers self-test', () => {
  test('assertNoBrokenImages passes when every image loads', async ({ page }) => {
    await page.setContent(`<img src="${GOOD_PNG}">`);
    await assertNoBrokenImages(page);
  });

  test('assertNoBrokenImages fails on a broken image', async ({ page }) => {
    await page.setContent('<img src="data:image/png;base64,Zm9v">'); // decodes to "foo", not a PNG
    let threw = false;
    try {
      await assertNoBrokenImages(page);
    } catch {
      threw = true;
    }
    expect(threw, 'assertNoBrokenImages should fail on a broken image').toBe(true);
  });

  test('assertNoDeadInternalLinks passes on the rendered README', async ({ page }) => {
    await page.goto('/');
    await assertNoDeadInternalLinks(page);
  });

  test('assertNoDeadInternalLinks fails on an injected dead link', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      const a = document.createElement('a');
      a.setAttribute('href', 'zzz-does-not-exist.html');
      a.textContent = 'dead';
      document.body.appendChild(a);
    });
    let threw = false;
    try {
      await assertNoDeadInternalLinks(page);
    } catch {
      threw = true;
    }
    expect(threw, 'assertNoDeadInternalLinks should fail on a dead link').toBe(true);
  });
});
