#!/usr/bin/env node
import { spawn } from 'node:child_process';
import { randomUUID } from 'node:crypto';
import { closeSync, existsSync, mkdirSync, openSync, readFileSync, readdirSync, realpathSync, renameSync, rmSync, writeFileSync } from 'node:fs';
import { createServer } from 'node:net';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { home, runtime, envFor } from './common.mjs';

const scriptDir = dirname(fileURLToPath(import.meta.url));
const sessionsDir = join(home, 'sessions');
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
const usage = `Whiteboard sessions (local only)
  start --name NAME [--project DIRECTORY]    Create a new, isolated board
  list [--project DIRECTORY]                Discover saved boards
  open SESSION_ID                           Start or reuse that exact board
  stop SESSION_ID                           Stop its process; retain all data
  run SESSION_ID COMMAND [ARGS...]          Run the canvas CLI on that board
  help                                     Show this help
Commands: add, apply, get, query, update, delete, describe, screenshot,
          render, export, import, mermaid, snapshot, arrange, clear
All commands require an explicit session ID except start/list/help.
The URL can change after restart; use open to get the current address.`;

function directory(id) {
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/.test(id || '')) {
    throw new Error('Use a session ID returned by start or list.');
  }
  return join(sessionsDir, id);
}
function read(id) {
  const session = JSON.parse(readFileSync(join(directory(id), 'session.json'), 'utf8'));
  if (session.schema !== 1 || session.id !== id || !session.project) throw new Error('Invalid session metadata.');
  return session;
}
function save(session) {
  const target = join(directory(session.id), 'session.json');
  const temp = `${target}.${process.pid}.tmp`;
  writeFileSync(temp, JSON.stringify(session, null, 2), { mode: 0o600 });
  renameSync(temp, target);
}
function alive(pid) {
  if (!Number.isSafeInteger(pid) || pid <= 0) return false;
  try { process.kill(pid, 0); return true; }
  catch (error) { return error.code !== 'ESRCH'; }
}
async function inspect(session) {
  if (!session.pid || !session.port) return 'stopped';
  let identity;
  try {
    const response = await fetch(`http://127.0.0.1:${session.port}/__whiteboard/session`, { signal: AbortSignal.timeout(700) });
    if (response.ok) identity = await response.json();
  } catch { /* A stopped server has no HTTP endpoint. */ }
  if (identity) {
    return identity.id === session.id && identity.instance === session.instance && identity.pid === session.pid
      ? 'running' : 'conflict';
  }
  return alive(session.pid) ? 'unreachable' : 'stopped';
}
function publicSession(session, status) {
  return {
    id: session.id, name: session.name, project: session.project, status,
    url: status === 'running' ? `http://127.0.0.1:${session.port}` : null,
    pid: session.pid, dataDirectory: join(directory(session.id), 'data'),
  };
}
async function locked(id, fn) {
  const lock = join(directory(id), 'operation.lock');
  const deadline = Date.now() + 30000;
  for (;;) {
    try { mkdirSync(lock); break; }
    catch (error) {
      if (error.code !== 'EEXIST') throw error;
      if (Date.now() >= deadline) throw new Error(`Session operation is busy or its lock is stale: ${lock}. Inspect owner.json before recovery; do not stop another board.`);
      await pause(100);
    }
  }
  writeFileSync(join(lock, 'owner.json'), JSON.stringify({ pid: process.pid, startedAt: new Date().toISOString() }));
  try { return await fn(read(id)); }
  finally { rmSync(lock, { recursive: true }); }
}
async function availablePort() {
  const probe = createServer();
  await new Promise((resolve, reject) => { probe.once('error', reject); probe.listen(0, '127.0.0.1', resolve); });
  const port = probe.address().port;
  await new Promise(resolve => probe.close(resolve));
  return port;
}
async function ensure(session) {
  const state = await inspect(session);
  if (state === 'running') return session;
  if (state !== 'stopped') throw new Error(`Session identity cannot be verified (${state}); refusing to attach or spawn another server. Inspect ${directory(session.id)}.`);
  const installed = runtime();
  session.port = await availablePort();
  session.instance = randomUUID();
  const log = openSync(join(directory(session.id), 'process.log'), 'a', 0o600);
  let child;
  try {
    child = spawn(installed.node, [join(scriptDir, 'serve.mjs')], {
      cwd: directory(session.id), env: envFor(session, installed),
      detached: true, stdio: ['ignore', log, log],
    });
  } finally { closeSync(log); }
  let spawnError;
  child.on('error', error => { spawnError = error; });
  session.pid = child.pid || null;
  save(session);
  child.unref();
  for (let i = 0; i < 80; i++) {
    if (spawnError || child.exitCode !== null || child.signalCode !== null) break;
    if (await inspect(session) === 'running') return session;
    await pause(100);
  }
  // This ChildProcess is the one we just launched, not a PID recovered from disk.
  child.kill('SIGTERM');
  throw new Error(`Canvas did not become ready. ${spawnError?.message || ''} Inspect ${join(directory(session.id), 'process.log')}.`);
}
async function stop(session) {
  const state = await inspect(session);
  if (state === 'running') {
    process.kill(session.pid, 'SIGTERM');
    for (let i = 0; i < 60 && alive(session.pid); i++) await pause(100);
    if (alive(session.pid)) throw new Error('Canvas did not stop; no further signal was sent.');
  } else if (state !== 'stopped') {
    throw new Error(`Session identity cannot be verified (${state}); refusing to signal this process.`);
  }
  session.pid = null; session.port = null; session.instance = null;
  save(session);
  return publicSession(session, 'stopped');
}
function options(args, allowed) {
  const result = {};
  while (args.length) {
    const key = args.shift();
    if (!allowed.includes(key) || !args.length) throw new Error(usage);
    result[key.slice(2)] = args.shift();
  }
  return result;
}
async function runCli(session, args) {
  if (args[0] === '--') args.shift();
  const allowed = new Set(['add', 'apply', 'get', 'query', 'update', 'delete', 'describe', 'screenshot', 'render', 'export', 'import', 'mermaid', 'snapshot', 'arrange', 'clear']);
  if (!allowed.has(args[0]) || args.some(arg => arg === '--url' || arg.startsWith('--url='))) {
    throw new Error('Unsupported command or URL override. Session routing is managed by this helper.');
  }
  await ensure(session);
  const installed = runtime();
  const child = spawn(installed.node, [join(installed.path, 'dist/bin.js'), ...args], {
    cwd: session.project, env: envFor(session, installed), stdio: 'inherit',
  });
  const code = await new Promise((resolve, reject) => { child.once('error', reject); child.once('exit', code => resolve(code)); });
  if (code !== 0) process.exitCode = code ?? 1;
}
async function main() {
  const [command = 'help', ...args] = process.argv.slice(2);
  if (command === 'help' || command === '--help') { console.log(usage); return; }
  if (Number(process.versions.node.split('.')[0]) < 20) throw new Error('Use Node 20 or newer (tested with Node 24).');
  mkdirSync(sessionsDir, { recursive: true, mode: 0o700 });
  if (command === 'start') {
    const opts = options(args, ['--name', '--project']);
    if (!opts.name?.trim()) throw new Error('Provide a short board name with --name.');
    const session = { schema: 1, id: randomUUID(), name: opts.name.trim(), project: realpathSync(resolve(opts.project || process.cwd())), createdAt: new Date().toISOString(), port: null, pid: null, instance: null };
    mkdirSync(directory(session.id), { mode: 0o700 });
    save(session);
    return locked(session.id, async s => publicSession(await ensure(s), 'running'));
  }
  if (command === 'list') {
    const opts = options(args, ['--project']);
    const project = opts.project ? realpathSync(resolve(opts.project)) : null;
    const sessions = readdirSync(sessionsDir).filter(id => existsSync(join(sessionsDir, id, 'session.json'))).map(read);
    return Promise.all(sessions.filter(s => !project || s.project === project).map(async s => publicSession(s, await inspect(s))));
  }
  const id = args.shift();
  if (!['open', 'stop', 'run'].includes(command) || (command !== 'run' && args.length)) throw new Error(usage);
  return locked(id, async session => {
    if (command === 'stop') return stop(session);
    if (command === 'open') return publicSession(await ensure(session), 'running');
    return runCli(session, args);
  });
}
try {
  const result = await main();
  if (result !== undefined) console.log(JSON.stringify(result, null, 2));
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
