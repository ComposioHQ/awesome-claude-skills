import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { existsSync, readFileSync } from 'node:fs';

export const revision = '8084a1c8b410d625fcfd59d5cffb32f3a86a2a6f';
export const home = resolve(process.env.WHITEBOARD_HOME || join(homedir(), '.local/share/codex-whiteboard'));
export function runtime() {
  const value = process.env.WHITEBOARD_RUNTIME
    ? { path: resolve(process.env.WHITEBOARD_RUNTIME), node: process.execPath }
    : JSON.parse(readFileSync(join(home, 'runtime.json'), 'utf8'));
  if (!existsSync(join(value.path, 'dist/bin.js'))) throw new Error('Whiteboard runtime is missing. Run scripts/setup.mjs from this skill.');
  return value;
}
export function envFor(session, installed) {
  return {
    ...process.env,
    PATH: `${dirname(installed.node)}:${process.env.PATH || ''}`,
    HOST: '127.0.0.1', PORT: String(session.port),
    EXPRESS_SERVER_URL: `http://127.0.0.1:${session.port}`,
    EXCALIDRAW_DATA_DIR: join(home, 'sessions', session.id, 'data'),
    EXCALIDRAW_EXPORT_DIR: session.project,
    EXCALIDRAW_NO_AUTOSTART: '1', ENABLE_CANVAS_SYNC: 'true',
    LOG_LEVEL: 'warn', LOG_FILE_PATH: join(home, 'sessions', session.id, 'canvas.log'),
    WHITEBOARD_RUNTIME: installed.path,
    WHITEBOARD_SESSION_ID: session.id, WHITEBOARD_INSTANCE_ID: session.instance,
  };
}
