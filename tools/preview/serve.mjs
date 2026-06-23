// Static server for the rendered preview. Serves tools/preview/dist/ on
// http://localhost:4321. Directory requests resolve to index.html. Used by the
// Playwright webServer and for eyeballing the preview locally.

import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.join(__dirname, 'dist');
const PORT = Number(process.env.PREVIEW_PORT) || 4321;

const CONTENT_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.md': 'text/plain; charset=utf-8',
  '.csv': 'text/csv; charset=utf-8',
  '.jsonl': 'application/x-ndjson; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.gif': 'image/gif',
  '.webp': 'image/webp',
  '.ico': 'image/x-icon',
  '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  '.xls': 'application/vnd.ms-excel',
  '.pdf': 'application/pdf',
  '.mmd': 'text/plain; charset=utf-8',
};

function send(res, status, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(status, { 'Content-Type': type });
  res.end(body);
}

// Resolve a URL path to a file inside DIST, guarding against traversal.
function resolveTarget(urlPath) {
  let decoded;
  try {
    decoded = decodeURIComponent(urlPath.split('?')[0].split('#')[0]);
  } catch {
    return null;
  }
  const rel = decoded.replace(/^\/+/, '');
  const abs = path.normalize(path.join(DIST, rel));
  if (abs !== DIST && !abs.startsWith(DIST + path.sep)) return null; // traversal guard
  return abs;
}

const server = http.createServer((req, res) => {
  const reqUrl = req.url || '/';
  const target = resolveTarget(reqUrl);
  if (target === null) return send(res, 400, 'Bad request');

  let filePath = target;
  try {
    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
      const pathOnly = reqUrl.split('?')[0].split('#')[0];
      // Redirect a bare directory to its trailing-slash form (like GitHub
      // Pages) so relative links/images inside the index resolve correctly.
      if (!pathOnly.endsWith('/')) {
        const query = reqUrl.slice(pathOnly.length);
        res.writeHead(301, { Location: `${pathOnly}/${query}` });
        return res.end();
      }
      filePath = path.join(filePath, 'index.html');
    }
    if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
      return send(res, 404, `Not found: ${reqUrl}`);
    }
    const ext = path.extname(filePath).toLowerCase();
    const type = CONTENT_TYPES[ext] || 'application/octet-stream';
    const stream = fs.createReadStream(filePath);
    // A file deleted/unreadable between stat and read emits an async 'error'
    // event; without this listener the process would crash.
    stream.on('error', (err) => {
      if (!res.headersSent) send(res, 500, `Server error: ${err.message}`);
      else res.destroy();
    });
    res.writeHead(200, { 'Content-Type': type });
    stream.pipe(res);
  } catch (err) {
    if (!res.headersSent) send(res, 500, `Server error: ${err.message}`);
  }
});

server.listen(PORT, () => {
  console.log(`[preview] serving ${DIST} on http://localhost:${PORT}`);
});
