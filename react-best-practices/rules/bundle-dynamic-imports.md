---
title: Dynamic Imports for Heavy Components
impact: CRITICAL
impactDescription: directly affects TTI and LCP
tags: bundle, dynamic-import, code-splitting, lazy-loading
---

## Dynamic Imports for Heavy Components

Use `React.lazy()` to lazy-load large components not needed on initial render.

**Incorrect (Monaco bundles with main chunk ~300KB):**

```tsx
import { MonacoEditor } from './monaco-editor'

function CodePanel({ code }: { code: string }) {
  return <MonacoEditor value={code} />
}
```

**Correct (Monaco loads on demand):**

```tsx
import { lazy, Suspense } from 'react'

const MonacoEditor = lazy(() =>
  import('./monaco-editor').then(m => ({ default: m.MonacoEditor }))
)

function CodePanel({ code }: { code: string }) {
  return (
    <Suspense fallback={<div>Loading editor...</div>}>
      <MonacoEditor value={code} />
    </Suspense>
  )
}
```

**Alternative (with loading state):**

```tsx
import { lazy, Suspense } from 'react'

const MonacoEditor = lazy(() => import('./monaco-editor'))

function CodePanel({ code }: { code: string }) {
  return (
    <Suspense fallback={<EditorSkeleton />}>
      <MonacoEditor value={code} />
    </Suspense>
  )
}
```

React.lazy() enables code-splitting, loading the component only when it's rendered for the first time.
