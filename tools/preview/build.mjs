// Local preview render harness.
//
// Renders every Markdown file in the repo to GitHub-flavored HTML, applies a
// GitHub-like stylesheet, rewrites relative `.md` links to their rendered
// `.html`, and copies every other (non-ignored) file through so `<img src>`,
// CSV/JSONL/XLSX artifact links, etc. resolve. Output goes to
// `tools/preview/dist/` (git-ignored). This stands in for GitHub's renderer so
// the integration render-checks never need to push to GitHub to test.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import MarkdownIt from 'markdown-it';
import anchor from 'markdown-it-anchor';
import GithubSlugger from 'github-slugger';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(__dirname, '..', '..');
export const DEFAULT_DEST = path.join(__dirname, 'dist');

// Directories never copied or rendered into the preview.
const IGNORE_DIRS = new Set([
  '.git', '.venv', 'venv', 'node_modules', 'dist', 'samples',
  'test-results', 'playwright-report', '.playwright',
  '.pytest_cache', '__pycache__', '.claude', '.idea', '.vscode',
]);
// Individual files never shipped (local build-context only).
const IGNORE_FILES = new Set(['CLAUDE.md', '.DS_Store', 'Thumbs.db']);

// --- link rewriting -------------------------------------------------------

// Rewrite a relative href so a `.md` target points at its rendered `.html`.
// External URLs, mailto/tel, in-page anchors, and data URIs pass through.
export function rewriteHref(href) {
  if (!href) return href;
  if (/^([a-z][a-z0-9+.-]*:)?\/\//i.test(href)) return href; // protocol-relative or absolute
  if (/^(mailto:|tel:|data:|#)/i.test(href)) return href;

  // Split off any query string and/or anchor so `page.md?x=1#sec` rewrites the
  // path part and keeps the suffix intact.
  const m = href.match(/^([^?#]*)([?#].*)?$/);
  let pathPart = m[1];
  const suffix = m[2] || '';
  if (pathPart === '') return href;

  if (pathPart.toLowerCase().endsWith('.md')) {
    const base = path.basename(pathPart);
    if (base.toLowerCase() === 'readme.md') {
      pathPart = pathPart.slice(0, pathPart.length - base.length) + 'index.html';
    } else {
      pathPart = pathPart.slice(0, -3) + '.html';
    }
  }
  return pathPart + suffix;
}

// --- markdown rendering ---------------------------------------------------

// Build a fresh renderer with a per-render slugger so heading anchors are
// deterministic and de-duplicated exactly like GitHub.
function makeRenderer() {
  const md = new MarkdownIt({ html: true, linkify: true, typographer: false });
  const slugger = new GithubSlugger();
  md.use(anchor, {
    slugify: (s) => slugger.slug(s),
    permalink: false,
  });
  const defaultLinkOpen =
    md.renderer.rules.link_open ||
    ((tokens, idx, options, _env, self) => self.renderToken(tokens, idx, options));
  md.renderer.rules.link_open = (tokens, idx, options, _env, self) => {
    const token = tokens[idx];
    const hrefIdx = token.attrIndex('href');
    if (hrefIdx >= 0) token.attrs[hrefIdx][1] = rewriteHref(token.attrs[hrefIdx][1]);
    return defaultLinkOpen(tokens, idx, options, _env, self);
  };
  return md;
}

function extractTitle(mdText, fallback) {
  const m = mdText.match(/^#\s+(.+?)\s*$/m);
  if (!m) return fallback;
  return m[1]
    .replace(/!?\[([^\]]*)\]\([^)]*\)/g, '$1') // link/image markup -> its text
    .replace(/[*_`]/g, '')
    .trim();
}

const STYLE = `
:root { color-scheme: light; }
* { box-sizing: border-box; }
body { margin: 0; background: #ffffff; color: #1f2328;
  font: 16px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
.markdown-body { max-width: 980px; margin: 0 auto; padding: 32px 24px 96px; }
.markdown-body h1, .markdown-body h2 { border-bottom: 1px solid #d8dee4; padding-bottom: .3em; }
.markdown-body h1, .markdown-body h2, .markdown-body h3, .markdown-body h4 { font-weight: 600; line-height: 1.25; margin: 24px 0 16px; }
.markdown-body h1 { font-size: 2em; } .markdown-body h2 { font-size: 1.5em; } .markdown-body h3 { font-size: 1.25em; }
.markdown-body a { color: #0969da; text-decoration: none; } .markdown-body a:hover { text-decoration: underline; }
.markdown-body img { max-width: 100%; background: #fff; }
.markdown-body code { background: rgba(175,184,193,.2); padding: .2em .4em; border-radius: 6px; font-size: 85%;
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; }
.markdown-body pre { background: #f6f8fa; padding: 16px; border-radius: 6px; overflow: auto; }
.markdown-body pre code { background: transparent; padding: 0; }
.markdown-body blockquote { margin: 0; padding: 0 1em; color: #59636e; border-left: .25em solid #d0d7de; }
.markdown-body table { border-collapse: collapse; margin: 16px 0; display: block; overflow: auto; }
.markdown-body th, .markdown-body td { border: 1px solid #d0d7de; padding: 6px 13px; }
.markdown-body tr:nth-child(2n) { background: #f6f8fa; }
.markdown-body hr { height: 1px; background: #d8dee4; border: 0; margin: 24px 0; }
.markdown-body sub { color: #59636e; }
`;

function htmlDocument(title, bodyHtml) {
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(title)}</title>
<style>${STYLE}</style>
</head>
<body>
<article class="markdown-body">
${bodyHtml}
</article>
</body>
</html>
`;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
}

export function renderMarkdown(mdText, { fallbackTitle = 'Untitled' } = {}) {
  const md = makeRenderer();
  const body = md.render(mdText);
  return htmlDocument(extractTitle(mdText, fallbackTitle), body);
}

// Map a source markdown path (relative) to its rendered html output path.
function mdOutputRelPath(relPath) {
  const dir = path.dirname(relPath);
  const base = path.basename(relPath);
  const outBase = base.toLowerCase() === 'readme.md' ? 'index.html' : base.slice(0, -3) + '.html';
  return dir === '.' ? outBase : path.join(dir, outBase);
}

// --- filesystem walk + build ----------------------------------------------

function* walk(root) {
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    if (entry.isDirectory()) {
      if (IGNORE_DIRS.has(entry.name)) continue;
      yield* walk(path.join(root, entry.name));
    } else if (entry.isFile()) {
      if (IGNORE_FILES.has(entry.name)) continue;
      yield path.join(root, entry.name);
    }
  }
}

export function buildAll({ root = REPO_ROOT, dest = DEFAULT_DEST } = {}) {
  fs.rmSync(dest, { recursive: true, force: true });
  fs.mkdirSync(dest, { recursive: true });

  let rendered = 0;
  let copied = 0;
  for (const absPath of walk(root)) {
    const relPath = path.relative(root, absPath);
    const isMd = absPath.toLowerCase().endsWith('.md');
    if (isMd) {
      const mdText = fs.readFileSync(absPath, 'utf8');
      const outRel = mdOutputRelPath(relPath);
      const outAbs = path.join(dest, outRel);
      fs.mkdirSync(path.dirname(outAbs), { recursive: true });
      fs.writeFileSync(outAbs, renderMarkdown(mdText, { fallbackTitle: path.basename(relPath) }));
      rendered++;
    } else {
      const outAbs = path.join(dest, relPath);
      fs.mkdirSync(path.dirname(outAbs), { recursive: true });
      fs.copyFileSync(absPath, outAbs);
      copied++;
    }
  }
  return { dest, rendered, copied };
}

// CLI entry
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const result = buildAll();
  console.log(`[preview] built ${result.rendered} pages, copied ${result.copied} files -> ${result.dest}`);
}
