---
title: Use Non-Blocking Operations for Side Effects
impact: MEDIUM
impactDescription: faster response times
tags: server, async, logging, analytics, side-effects
---

## Use Non-Blocking Operations for Side Effects

Schedule work that should execute after a response is sent. This prevents logging, analytics, and other side effects from blocking the response.

**Incorrect (blocks response):**

```tsx
// Express example
app.post('/api/action', async (req, res) => {
  await updateDatabase(req.body)

  // Logging blocks the response
  const userAgent = req.headers['user-agent'] || 'unknown'
  await logUserAction({ userAgent })

  res.json({ status: 'success' })
})
```

**Correct (using on-finished package - recommended):**

```tsx
import onFinished from 'on-finished'

app.post('/api/action', async (req, res) => {
  await updateDatabase(req.body)

  // Run after response is fully sent (handles errors and client disconnects)
  onFinished(res, (err) => {
    if (err) return // Client disconnected or error occurred

    const userAgent = req.headers['user-agent'] || 'unknown'
    logUserAction({ userAgent, status: res.statusCode })
  })

  res.json({ status: 'success' })
})
```

**Alternative (simple cases with res.on):**

```tsx
app.post('/api/action', async (req, res) => {
  await updateDatabase(req.body)

  // Listen to both 'finish' and 'close' events
  const afterResponse = () => {
    res.removeListener('finish', afterResponse)
    res.removeListener('close', afterResponse)
    logUserAction({ userAgent: req.headers['user-agent'] })
  }

  res.on('finish', afterResponse)
  res.on('close', afterResponse)

  res.json({ status: 'success' })
})
```

**Alternative (setImmediate for deferred work):**

```tsx
app.post('/api/action', async (req, res) => {
  await updateDatabase(req.body)

  res.json({ status: 'success' })

  // Defer to next event loop tick (runs after response starts sending)
  setImmediate(async () => {
    await logUserAction({ userAgent: req.headers['user-agent'] })
  })
})
```

The response is sent immediately while background work happens asynchronously.

**Common use cases:**

- Analytics tracking
- Audit logging
- Sending notifications
- Cache invalidation
- Cleanup tasks (closing files, releasing connections)

**Important notes:**

- Use `on-finished` package for production - handles edge cases like client disconnects
- `setImmediate()` is recommended over `process.nextTick()` (easier to reason about)
- For heavy CPU work, use Worker Threads or job queues (like Bull/BullMQ)
- Check `res.headersSent` in error handlers since response may already be committed

Reference: [on-finished](https://github.com/jshttp/on-finished), [Node.js Event Loop](https://nodejs.org/en/docs/guides/event-loop-timers-and-nexttick)
