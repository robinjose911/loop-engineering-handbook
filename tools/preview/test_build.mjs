// Unit test for the preview render harness (Stage 0.3).
//
// Builds a tiny fixture (`# Hi ![x](a.png) [l](b.md)`) through the same render +
// build path the real preview uses, and asserts: the rendered HTML has a
// resolvable `<img src="a.png">` (the asset is copied through) and a rewritten
// `<a href="b.html">` (the `.md` link points at its rendered page).

import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { buildAll, renderMarkdown, rewriteHref } from './build.mjs';

let failures = 0;
function check(name, fn) {
  try {
    fn();
    console.log(`  ok - ${name}`);
  } catch (err) {
    failures++;
    console.error(`  FAIL - ${name}\n    ${err.message}`);
  }
}

// 1. renderMarkdown: img passes through, .md link is rewritten to .html
check('renderMarkdown rewrites .md links and keeps img src', () => {
  const html = renderMarkdown('# Hi\n\n![x](a.png) [l](b.md)\n');
  assert.match(html, /<img[^>]+src="a\.png"/, 'img src should be preserved');
  assert.match(html, /<a href="b\.html">/, '.md link should be rewritten to .html');
  assert.doesNotMatch(html, /href="b\.md"/, 'no raw .md link should remain');
});

// 2. rewriteHref edge cases
check('rewriteHref maps README.md -> index.html and leaves externals/anchors', () => {
  assert.equal(rewriteHref('docs/README.md'), 'docs/index.html');
  assert.equal(rewriteHref('../README.md'), '../index.html');
  assert.equal(rewriteHref('docs/01-x.md'), 'docs/01-x.html');
  assert.equal(rewriteHref('docs/01-x.md#origin'), 'docs/01-x.html#origin');
  assert.equal(rewriteHref('page.md?v=1'), 'page.html?v=1');
  assert.equal(rewriteHref('page.md?v=1#sec'), 'page.html?v=1#sec');
  assert.equal(rewriteHref('https://example.com/a.md'), 'https://example.com/a.md');
  assert.equal(rewriteHref('#anchor'), '#anchor');
  assert.equal(rewriteHref('LICENSE'), 'LICENSE');
});

// 3. buildAll on a fixture root: html produced, asset copied, README -> index
check('buildAll renders pages and copies assets', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'preview-fixture-'));
  const dest = fs.mkdtempSync(path.join(os.tmpdir(), 'preview-dist-'));
  try {
    fs.writeFileSync(path.join(root, 'README.md'), '# Hi\n\n![x](a.png) [l](b.md)\n');
    fs.writeFileSync(path.join(root, 'b.md'), '# B page\n');
    fs.writeFileSync(path.join(root, 'a.png'), Buffer.from([0x89, 0x50, 0x4e, 0x47])); // PNG magic bytes

    const result = buildAll({ root, dest });
    assert.equal(result.rendered, 2, 'two markdown files rendered');
    assert.ok(result.copied >= 1, 'at least the png copied');

    assert.ok(fs.existsSync(path.join(dest, 'index.html')), 'README.md -> index.html');
    assert.ok(fs.existsSync(path.join(dest, 'b.html')), 'b.md -> b.html');
    assert.ok(fs.existsSync(path.join(dest, 'a.png')), 'a.png copied through');

    const indexHtml = fs.readFileSync(path.join(dest, 'index.html'), 'utf8');
    assert.match(indexHtml, /<img[^>]+src="a\.png"/);
    assert.match(indexHtml, /<a href="b\.html">/);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
    fs.rmSync(dest, { recursive: true, force: true });
  }
});

if (failures > 0) {
  console.error(`\n[preview] test_build.mjs: ${failures} failure(s)`);
  process.exit(1);
}
console.log('\n[preview] test_build.mjs: all checks passed');
