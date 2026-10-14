// Add launch identity without modifying the upstream editor or server source.
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';

const { default: app, startServer } = await import(pathToFileURL(join(process.env.WHITEBOARD_RUNTIME, 'dist/server.js')));
app.get('/__whiteboard/session', (_req, res) => {
  res.json({ id: process.env.WHITEBOARD_SESSION_ID, instance: process.env.WHITEBOARD_INSTANCE_ID, pid: process.pid });
});
await startServer();
