import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

// Before the preview is served: (1) regenerate placeholder PNGs so
// `assertNoBrokenImages` is green on an otherwise empty skeleton, and (2) build
// the preview into dist/. Building here (rather than in the webServer command)
// means even a reused server serves freshly built output -- serve.mjs reads
// dist/ from disk per request, so there is no stale-build trap.
export default function globalSetup(): void {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const venvPy = path.join(repoRoot, '.venv', 'bin', 'python');
  const py = fs.existsSync(venvPy)
    ? venvPy
    : process.platform === 'win32'
      ? 'python'
      : 'python3';
  execFileSync(py, ['tools/stubs/make_placeholders.py'], { cwd: repoRoot, stdio: 'inherit' });
  execFileSync('node', ['tools/preview/build.mjs'], { cwd: repoRoot, stdio: 'inherit' });
}
