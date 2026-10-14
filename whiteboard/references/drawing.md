# Drawing commands

Use the absolute path to this skill's `scripts/session.mjs` as `SESSION_CLI`. Replace `SESSION_ID` with a returned ID. Paths passed to the canvas CLI resolve relative to the session's project, even if the calling chat has another working directory. Create output directories before exporting.

```sh
node "$SESSION_CLI" run SESSION_ID snapshot save before-queue
node "$SESSION_CLI" run SESSION_ID add /absolute/path/elements.json
node "$SESSION_CLI" run SESSION_ID get api
node "$SESSION_CLI" run SESSION_ID update api --set '{"text":"API gateway"}'
node "$SESSION_CLI" run SESSION_ID query --type rectangle
node "$SESSION_CLI" run SESSION_ID export --out boards/api-design.excalidraw
node "$SESSION_CLI" run SESSION_ID screenshot --out boards/api-design.png
```

For `add`, supply a JSON array in a file or on stdin with `add -`. The CLI converts shape text to native bound labels and resolves arrow bindings:

```json
[
  {"id":"api","type":"rectangle","x":100,"y":100,"width":220,"height":100,"text":"API","backgroundColor":"#dbeafe","fillStyle":"solid"},
  {"id":"queue","type":"rectangle","x":500,"y":100,"width":220,"height":100,"text":"Job queue","backgroundColor":"#fef3c7","fillStyle":"solid"},
  {"id":"submit","type":"arrow","x":0,"y":0,"startElementId":"api","endElementId":"queue","text":"enqueue"}
]
```

Plan enough space for labels and connections. When a section label is needed to orient the viewer, use independent text; a label on a large background rectangle will appear at its center. Use `get`/`query` to obtain existing IDs instead of guessing. After browser sync, a shape's visible label can be a separate text element with `containerId`; update that text element when appropriate.

## Connector labels and spacing

An arrow's `text` or `label.text` generates a native bound text element. That element is the visible label, not a second label to add manually. After browser sync, find it through `containerId` or the arrow's `boundElements` and update its existing ID. Avoid creating a standalone caption with the same meaning. If custom placement requires standalone text, remove the prior bound label and its references and clear the arrow's label metadata first; never keep both representations.

Plan card spacing from label dimensions. For a straight horizontal connector, its visible span should accommodate the label width plus at least 24 canvas pixels of shaft on each side. Add the endpoint-to-card gaps when calculating card separation. For vertical connectors, use label height. Center the label on the available segment. Widen gaps or shorten labels before shrinking text. For example, a 145px label needs at least 193px of connector span, plus endpoint gaps between the cards. Moving a card can leave an arrow label behind: inspect and recenter it after rerouting.

Export and check the scene using `check-layout.mjs`, located beside `session.mjs`:

```sh
node "$SESSION_CLI" run SESSION_ID export --out /absolute/path/board.excalidraw
node /absolute/path/to/whiteboard/scripts/check-layout.mjs /absolute/path/board.excalidraw
```

The read-only checker reports multiple bound labels, nearby standalone copies (ignoring whitespace differences), connector labels overlapping node bounds, and insufficient shaft clearance. Exit 0 means no detected findings; 1 means findings or manual review; 2 means invalid input or invocation. Use the reported element IDs to inspect and correct agent-created problems. Do not delete user annotations merely to satisfy the checker.

Checks use stored text bounds, which can be estimates before rendering/browser sync. Bent, diagonal, rotated, or unmeasured labeled connectors require visual review. These checks cover common connector mistakes, not every possible collision or readability problem. Inspect the final rendering and live canvas when available; both labels and arrowheads should be distinct at the viewing scale.

## Other edits and file operations

`apply` accepts a patch file such as `{"create":[...],"update":[{"id":"api","set":{"x":120}}],"delete":["old-id"]}`. Do not assume a multi-operation patch is transactional. Snapshot before substantial edits.

Other supported commands include `describe`, `delete`, `arrange`, `mermaid`, `render`, and `snapshot save|list|restore NAME`. Mermaid conversion needs an open browser tab; regular screenshots render without one. `render file.excalidraw --out preview.png` renders a saved export.

To replace the active scene, export it first, then use `import path/to/board.excalidraw --replace`. `clear --yes` removes the active scene and should only follow a user request to clear/start over, with a saved recovery copy. A new empty session usually fits a new-topic request better.

Canvas JSON commands write JSON to stdout; `describe` writes text. Failures return nonzero status and diagnostics. The helper blocks `--url` overrides and upstream lifecycle commands so operations cannot silently target another board. MCP and cloud sharing are not routed through this helper.
