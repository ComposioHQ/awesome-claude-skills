#!/usr/bin/env node
import { spawnSync } from 'node:child_process';
import { cpSync, existsSync, mkdirSync, mkdtempSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { home, revision } from './common.mjs';

if (Number(process.versions.node.split('.')[0]) < 20) throw new Error('Use Node 20 or newer.');
const scriptDir = dirname(fileURLToPath(import.meta.url));
const target = join(home, 'runtimes', `${revision}-1`);
const env = { ...process.env, PATH: `${dirname(process.execPath)}:${process.env.PATH || ''}` };
function run(cmd, args, cwd) {
  const result = spawnSync(cmd, args, { cwd, env, stdio: ['ignore', 'inherit', 'inherit'] });
  if (result.error || result.status !== 0) throw result.error || new Error(`${cmd} failed with status ${result.status}`);
}
function capture(cmd, args, cwd) {
  const result = spawnSync(cmd, args, { cwd, env, encoding: 'utf8' });
  if (result.status !== 0) throw new Error(result.stderr);
  return result.stdout.trim();
}
const args = process.argv.slice(2);
if (args.length && (args.length !== 2 || args[0] !== '--source')) throw new Error('Usage: setup.mjs [--source PREPARED_CHECKOUT]');
mkdirSync(join(home, 'runtimes'), { recursive: true, mode: 0o700 });
if (!existsSync(join(target, 'ready.json'))) {
  const stage = mkdtempSync(join(home, 'runtimes', '.install-'));
  let source = args[1] && resolve(args[1]);
  if (!source) {
    source = join(stage, 'source');
    run('git', ['init', source], stage);
    run('git', ['remote', 'add', 'origin', 'https://github.com/yctimlin/mcp_excalidraw.git'], source);
    run('git', ['fetch', '--depth', '1', 'origin', revision], source);
    run('git', ['checkout', '--detach', 'FETCH_HEAD'], source);
    run('git', ['apply', join(scriptDir, 'dependency-lock.patch')], source);
    run('npm', ['ci', '--no-fund'], source);
    run('npm', ['run', 'build'], source);
  }
  if (capture('git', ['rev-parse', 'HEAD'], source) !== revision) throw new Error('Source revision does not match the pinned runtime.');
  run('git', ['apply', '--reverse', '--check', join(scriptDir, 'dependency-lock.patch')], source);
  const bundle = join(stage, 'bundle');
  mkdirSync(bundle);
  for (const path of ['dist', 'assets', 'package.json', 'package-lock.json', 'LICENSE']) {
    cpSync(join(source, path), join(bundle, path), { recursive: true });
  }
  const fonts = join(source, 'node_modules/@excalidraw/excalidraw/dist/prod/fonts');
  cpSync(fonts, join(bundle, 'dist/frontend/fonts'), { recursive: true });
  cpSync(fonts, join(bundle, 'dist/assets/fonts'), { recursive: true });
  const htmlPath = join(bundle, 'dist/frontend/index.html');
  let html = readFileSync(htmlPath, 'utf8');
  if (!html.includes('window.EXCALIDRAW_ASSET_PATH')) html = html.replace('<head>', '<head>\n<script>window.EXCALIDRAW_ASSET_PATH = "/";</script>');
  writeFileSync(htmlPath, html);
  run('npm', ['ci', '--omit=dev', '--no-fund'], bundle);
  writeFileSync(join(bundle, 'ready.json'), JSON.stringify({ revision, installedAt: new Date().toISOString() }));
  renameSync(bundle, target);
  // Retain build/log staging for diagnosis; it contains no live board data.
}
const manifest = { schema: 1, path: target, node: process.execPath, revision };
const temp = join(home, `runtime.${process.pid}.json`);
writeFileSync(temp, JSON.stringify(manifest, null, 2), { mode: 0o600 });
renameSync(temp, join(home, 'runtime.json'));
console.log(JSON.stringify(manifest, null, 2));
