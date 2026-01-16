---
title: Defer Non-Critical Third-Party Libraries
impact: MEDIUM
impactDescription: loads after hydration
tags: bundle, third-party, analytics, defer
---

## Defer Non-Critical Third-Party Libraries

Analytics, logging, and error tracking don't block user interaction. Load them after hydration.

**Incorrect (blocks initial bundle):**

```tsx
import { Analytics } from '@vercel/analytics/react'

export default function App({ children }) {
  return (
    <div>
      {children}
      <Analytics />
    </div>
  )
}
```

**Correct (loads after hydration with useEffect):**

```tsx
import { useEffect, useState, lazy, Suspense } from 'react'

const Analytics = lazy(() =>
  import('@vercel/analytics/react').then(m => ({ default: m.Analytics }))
)

export default function App({ children }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div>
      {children}
      {mounted && (
        <Suspense fallback={null}>
          <Analytics />
        </Suspense>
      )}
    </div>
  )
}
```

**Alternative (simple deferred loading):**

```tsx
import { useEffect } from 'react'

export default function App({ children }) {
  useEffect(() => {
    // Load analytics after initial render
    import('@vercel/analytics/react').then(({ Analytics }) => {
      // Initialize analytics
    })
  }, [])

  return <div>{children}</div>
}
```

This ensures the main bundle stays small and analytics loads without blocking the initial render.
