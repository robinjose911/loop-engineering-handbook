import { test, expect } from '@playwright/test';

// Stage 2 integration test: all diagrams + charts render as real images at their
// declared manifest dimensions, and zero diagram/chart placeholders remain.

type Slot = {
  id: string;
  kind: string;
  path: string;
  width: number;
  height: number;
  status: string;
};

async function loadImageDims(page: import('@playwright/test').Page, src: string) {
  return page.evaluate(
    (url) =>
      new Promise<{ nw: number; nh: number }>((resolve, reject) => {
        const img = new Image();
        // Bound the wait so a stalled request fails with a useful message
        // instead of hanging to the test timeout.
        const timer = setTimeout(() => reject(new Error(`timed out loading ${url}`)), 8000);
        img.onload = () => {
          clearTimeout(timer);
          resolve({ nw: img.naturalWidth, nh: img.naturalHeight });
        };
        img.onerror = () => {
          clearTimeout(timer);
          reject(new Error(`failed to load ${url}`));
        };
        img.src = url;
      }),
    src,
  );
}

test.describe('Stage 2: diagrams + charts', () => {
  test('every diagram & chart slot is real, served, and at its declared size', async ({ page }) => {
    await page.goto('/'); // establish the 127.0.0.1:4321 origin for relative srcs
    const manifest = await (await page.request.get('/assets/manifest.json')).json();
    const visuals: Slot[] = manifest.slots.filter(
      (s: Slot) => s.kind === 'diagram' || s.kind === 'chart',
    );
    expect(visuals.length).toBe(14); // 5 diagrams + 9 charts

    const placeholders = visuals.filter((s) => s.status !== 'real').map((s) => s.id);
    expect(placeholders, `placeholder visual slots remain: ${placeholders}`).toEqual([]);

    for (const slot of visuals) {
      const dims = await loadImageDims(page, `/${slot.path}`);
      expect(dims, `${slot.id} (${slot.path})`).toEqual({ nw: slot.width, nh: slot.height });
    }
  });

  test('all five diagram PNGs and nine chart PNGs return 200', async ({ page }) => {
    const manifest = await (await page.request.get('http://127.0.0.1:4321/assets/manifest.json')).json();
    const visuals: Slot[] = manifest.slots.filter(
      (s: Slot) => s.kind === 'diagram' || s.kind === 'chart',
    );
    for (const slot of visuals) {
      const resp = await page.request.get(`http://127.0.0.1:4321/${slot.path}`);
      expect(resp.ok(), `${slot.path} should be 200`).toBeTruthy();
      const body = await resp.body();
      expect(body.byteLength, `${slot.path} non-empty`).toBeGreaterThan(100);
      // PNG magic number
      expect(body[0]).toBe(0x89);
      expect(body[1]).toBe(0x50);
    }
  });
});
