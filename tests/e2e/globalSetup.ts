import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';

// Before the preview is served: (1) regenerate placeholder PNGs so
// `assertNoBrokenImages` is green on an otherwise empty skeleton, (2) regenerate
// the synthetic example artifacts (deterministic) so the example pages + their
// csv/jsonl/xlsx links resolve, and (3) build the preview into dist/. Building
// here (rather than in the webServer command) means even a reused server serves
// freshly built output -- serve.mjs reads dist/ from disk per request, so there
// is no stale-build trap.
export default function globalSetup(): void {
  const repoRoot = path.resolve(__dirname, '..', '..');
  const venvPy = path.join(repoRoot, '.venv', 'bin', 'python');
  const py = fs.existsSync(venvPy)
    ? venvPy
    : process.platform === 'win32'
      ? 'python'
      : 'python3';
  execFileSync(py, ['tools/stubs/make_placeholders.py'], { cwd: repoRoot, stdio: 'inherit' });
  // Generate example artifacts only if they are missing, so a normal run serves
  // the committed bytes instead of overwriting the tracked tree.
  const examplesDir = path.join(repoRoot, 'examples');
  const present = fs.existsSync(examplesDir)
    ? fs.readdirSync(examplesDir, { withFileTypes: true }).filter(
        (d) => d.isDirectory() && fs.existsSync(path.join(examplesDir, d.name, 'headline.json')),
      ).length
    : 0;
  if (present < 7) {
    execFileSync(py, ['tools/data/generate_all.py'], { cwd: repoRoot, stdio: 'inherit' });
  }
  execFileSync('node', ['tools/preview/build.mjs'], { cwd: repoRoot, stdio: 'inherit' });
}
