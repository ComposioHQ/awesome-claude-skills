# Session operations

`scripts/session.mjs` uses `~/.local/share/codex-whiteboard/` by default. `runtime.json` identifies the installed runtime and Node executable. Each `sessions/<id>/` directory holds `session.json`, durable `data/`, logs, and a temporary operation lock. Keep these files when a chat or checkout is removed. `WHITEBOARD_HOME` and `WHITEBOARD_RUNTIME` can select isolated locations for verification; ordinary sessions should use the defaults.

`start --name NAME --project DIRECTORY` creates a distinct board. `list` shows all saved boards; `list --project DIRECTORY` filters by the canonical directory path. Git worktrees therefore count as separate project directories. To deliberately share across worktrees, chats, or agent apps, pass the same session ID to `open`/`run`. Local Codex and Claude Code installations use the same runtime and session directory. No automatic chat-to-board binding exists.

`open ID` returns the current URL. `run ID COMMAND...` also starts a stopped session when necessary. `stop ID` checks the server's session ID, launch instance, and PID before signaling it, and keeps all saved data. The helper uses a different available loopback port after restart; bookmarks may need the refreshed URL.

## Runtime setup

Run `node /absolute/path/to/this/skill/scripts/setup.mjs`. It fetches community source commit `8084a1c8b410d625fcfd59d5cffb32f3a86a2a6f`, applies the bundled lockfile patch, builds the editor/server, and installs runtime artifacts in the user data directory. It also serves packaged fonts locally. Repeating setup reuses the installed version.

For development, `setup.mjs --source /absolute/path/to/prepared/upstream` can copy a built checkout at that commit with the expected lockfile patch. It installs runtime dependencies in the destination and does not retain a dependency on the source checkout. The installer never changes global Codex/MCP settings.

Runtime code comes from [yctimlin/mcp_excalidraw](https://github.com/yctimlin/mcp_excalidraw), a community project embedding the official Excalidraw editor. This is an experimental local workflow. The original audit fixes are bundled; frontend dependency findings remain. The server has no authentication, and board edits are not conflict-safe. Do not expose it beyond loopback.

## Diagnosing a failed operation

Inspect the specific session's `process.log`, `canvas.log`, and `session.json`. A running listener with a mismatched identity must not be adopted or terminated. If a saved PID is alive but its endpoint is unreachable, investigate that process before changing the registry or starting another server for its data directory. The helper deliberately refuses ambiguous ownership.

A concurrent helper operation waits on `operation.lock`. If it times out, read the lock's `owner.json` and check that PID. An interrupted helper can leave a stale lock; remove only that exact lock directory after verifying its owner has exited and no session command is active. Do not remove the upstream `data/canvas-state.lock` while its server is running.

If the helper reports Node is too old, use Node 20+; the original install used Node 24. The runtime manifest records its executable path. If that executable has been removed, rerun setup with an available supported Node version. Keep project export destinations available; moving a project does not automatically update its saved session metadata.
