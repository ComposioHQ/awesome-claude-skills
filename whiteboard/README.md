# Excalidraw Whiteboard

Draw, discuss, and refine the same local Excalidraw board with Claude Code or Codex. The agent draws a design, the human edits the canvas, and the agent reads the revised scene and an image before continuing the discussion.

Created by [Jim Jeffers](https://github.com/jimjeffers) for iterative software design discussions. The [upstream repository](https://github.com/jimjeffers/excalidraw-whiteboard-skill) contains installation instructions, rendered examples, editable boards, and verification notes. This copy is MIT licensed; see [LICENSE](LICENSE).

## Install

Requires Node.js 22.20+ for this installer, npm, Git, and a local browser:

```sh
npx skills@1.7.2 add jimjeffers/excalidraw-whiteboard-skill --skill whiteboard --global --agent claude-code
```

The bundled scripts themselves require Node 20+. First use builds a pinned open-source Excalidraw runtime. Each board has its own loopback server, available port, and durable session data. No Excalidraw account, API key, Docker, or MCP server is needed. This requires an agent and browser on the same computer; it is not a cloud-only Claude.ai workflow. Validated on macOS with Node 24.

## Example

Ask: “Use the whiteboard skill to sketch our upload-processing flow.” Edit the board to add “Invalid file?” beside the worker, wait for sync, then ask: “Read the board and help me decide how to handle the case I added.”

The agent reads the current scene and image, discusses the change, saves a snapshot, and refines the diagram. Take turns editing: human and agent writes are not conflict-safe, and drawing does not automatically wake the agent.

![Example of a sketch, a human concern, and a revised flow](https://raw.githubusercontent.com/jimjeffers/excalidraw-whiteboard-skill/main/examples/collaborative-iteration.png)

[Editable example](https://github.com/jimjeffers/excalidraw-whiteboard-skill/blob/main/examples/collaborative-iteration.excalidraw) · [Runtime architecture](https://github.com/jimjeffers/excalidraw-whiteboard-skill#architecture-one-server-per-board-session)
