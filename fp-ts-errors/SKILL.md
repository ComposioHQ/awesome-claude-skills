---
name: fp-ts-errors
description: Handle errors as values using fp-ts Either and TaskEither for cleaner, more predictable TypeScript code. Use when implementing error handling patterns with fp-ts.
risk: safe
source: https://github.com/whatiskadudoing/fp-ts-skills
---

# Practical Error Handling with fp-ts

This skill teaches you how to handle errors without try/catch spaghetti. No academic jargon - just practical patterns for real problems.

## When to Use This Skill

- When you want type-safe error handling in TypeScript
- When replacing try/catch with Either and TaskEither patterns
- When building APIs or services that need explicit error types
- When accumulating multiple validation errors

The core idea: **Errors are just data**. Instead of throwing them into the void and hoping someone catches them, return them as values that TypeScript can track.

---

## 1. Stop Throwing Everywhere

### The Problem with Exceptions

Exceptions are invisible in your types. They break the contract between functions.

```typescript
// What this function signature promises:
function getUser(id: string): User

// What it actually does:
function getUser(id: string): User {
  if (!id) throw new Error('ID required')
  const user = db.find(id)
  if (!user) throw new Error('User not found')
  return user
}

// The caller has no idea this can fail
const user = getUser(id) // Might explode!
```

You end up with code like this:

```typescript
// MESSY: try/catch everywhere
function processOrder(orderId: string) {
  let order
  try {
    order = getOrder(orderId)
  } catch (e) {
    console.error('Failed to get order')
    return null
  }

  let user
  try {
    user = getUser(order.userId)
  } catch (e) {
    console.error('Failed to get user')
    return null
  }

  let payment
  try {
    payment = chargeCard(user.cardId, order.total)
  } catch (e) {
    console.error('Payment failed')
    return null
  }

  return { order, user, payment }
}
```

### The Solution: Return Errors as Values

```typescript
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

// Now TypeScript KNOWS this can fail
function getUser(id: string): E.Either<string, User> {
  if (!id) return E.left('ID required')
  const user = db.find(id)
  if (!user) return E.left('User not found')
  return E.right(user)
}

// The caller is forced to handle both cases
const result = getUser(id)
// result is Either<string, User> - error OR success, never both
```

---

## 2. The Result Pattern (Either)

`Either<E, A>` is simple: it holds either an error (`E`) or a value (`A`).

- `Left` = error case
- `Right` = success case (think "right" as in "correct")

```typescript
import * as E from 'fp-ts/Either'

// Creating values
const success = E.right(42)           // Right(42)
const failure = E.left('Oops')        // Left('Oops')

// Checking what you have
if (E.isRight(result)) {
  console.log(result.right) // The success value
} else {
  console.log(result.left)  // The error
}

// Better: pattern match with fold
const message = pipe(
  result,
  E.fold(
    (error) => `Failed: ${error}`,
    (value) => `Got: ${value}`
  )
)
```

### Converting Throwing Code to Either

```typescript
// Wrap any throwing function with tryCatch
const parseJSON = (json: string): E.Either<Error, unknown> =>
  E.tryCatch(
    () => JSON.parse(json),
    (e) => (e instanceof Error ? e : new Error(String(e)))
  )

parseJSON('{"valid": true}')  // Right({ valid: true })
parseJSON('not json')          // Left(SyntaxError: ...)

// For functions you'll reuse, use tryCatchK
const safeParseJSON = E.tryCatchK(
  JSON.parse,
  (e) => (e instanceof Error ? e : new Error(String(e)))
)
```

### Common Either Operations

```typescript
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

// Transform the success value
const doubled = pipe(
  E.right(21),
  E.map(n => n * 2)
) // Right(42)

// Transform the error
const betterError = pipe(
  E.left('bad'),
  E.mapLeft(e => `Error: ${e}`)
) // Left('Error: bad')

// Provide a default for errors
const value = pipe(
  E.left('failed'),
  E.getOrElse(() => 0)
) // 0

// Convert nullable to Either
const fromNullable = E.fromNullable('not found')
fromNullable(user)  // Right(user) if exists, Left('not found') if null/undefined
```

---

## 3. Chaining Operations That Might Fail

The real power comes from chaining. Each step can fail, but you write it as a clean pipeline.

### Before: Nested Try/Catch Hell

```typescript
// MESSY: Each step can fail, nested try/catch everywhere
function processUserOrder(userId: string, productId: string): Result | null {
  let user
  try {
    user = getUser(userId)
  } catch (e) {
    logError('User fetch failed', e)
    return null
  }

  if (!user.isActive) {
    logError('User not active')
    return null
  }

  let product
  try {
    product = getProduct(productId)
  } catch (e) {
    logError('Product fetch failed', e)
    return null
  }

  if (product.stock < 1) {
    logError('Out of stock')
    return null
  }

  let order
  try {
    order = createOrder(user, product)
  } catch (e) {
    logError('Order creation failed', e)
    return null
  }

  return order
}
```

### After: Clean Chain with Either

```typescript
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

// Each function returns Either<Error, T>
const getUser = (id: string): E.Either<string, User> => { ... }
const getProduct = (id: string): E.Either<string, Product> => { ... }
const createOrder = (user: User, product: Product): E.Either<string, Order> => { ... }

// Chain them together - first error stops the chain
const processUserOrder = (userId: string, productId: string): E.Either<string, Order> =>
  pipe(
    getUser(userId),
    E.filterOrElse(
      user => user.isActive,
      () => 'User not active'
    ),
    E.chain(user =>
      pipe(
        getProduct(productId),
        E.filterOrElse(
          product => product.stock >= 1,
          () => 'Out of stock'
        ),
        E.chain(product => createOrder(user, product))
      )
    )
  )

// Or use Do notation for cleaner access to intermediate values
const processUserOrder = (userId: string, productId: string): E.Either<string, Order> =>
  pipe(
    E.Do,
    E.bind('user', () => getUser(userId)),
    E.filterOrElse(
      ({ user }) => user.isActive,
      () => 'User not active'
    ),
    E.bind('product', () => getProduct(productId)),
    E.filterOrElse(
      ({ product }) => product.stock >= 1,
      () => 'Out of stock'
    ),
    E.chain(({ user, product }) => createOrder(user, product))
  )
```

### Different Error Types? Use chainW

```typescript
type ValidationError = { type: 'validation'; message: string }
type DbError = { type: 'db'; message: string }

const validateInput = (id: string): E.Either<ValidationError, string> => { ... }
const fetchFromDb = (id: string): E.Either<DbError, User> => { ... }

// chainW (W = "wider") automatically unions the error types
const process = (id: string): E.Either<ValidationError | DbError, User> =>
  pipe(
    validateInput(id),
    E.chainW(validId => fetchFromDb(validId))
  )
```

---

## 4. Collecting Multiple Errors

Sometimes you want ALL errors, not just the first one. Form validation is the classic example.

### Before: Collecting Errors Manually

```typescript
// MESSY: Manual error accumulation
function validateForm(form: FormData): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!form.email) {
    errors.push('Email required')
  } else if (!form.email.includes('@')) {
    errors.push('Invalid email')
  }

  if (!form.password) {
    errors.push('Password required')
  } else if (form.password.length < 8) {
    errors.push('Password too short')
  }

  if (!form.age) {
    errors.push('Age required')
  } else if (form.age < 18) {
    errors.push('Must be 18+')
  }

  return { valid: errors.length === 0, errors }
}
```

### After: Validation with Error Accumulation

```typescript
import * as E from 'fp-ts/Either'
import * as NEA from 'fp-ts/NonEmptyArray'
import { sequenceS } from 'fp-ts/Apply'
import { pipe } from 'fp-ts/function'

// Errors as a NonEmptyArray (always at least one)
type Errors = NEA.NonEmptyArray<string>

// Create the applicative that accumulates errors
const validation = E.getApplicativeValidation(NEA.getSemigroup<string>())

// Validators that return Either<Errors, T>
const validateEmail = (email: string): E.Either<Errors, string> =>
  !email ? E.left(NEA.of('Email required'))
  : !email.includes('@') ? E.left(NEA.of('Invalid email'))
  : E.right(email)

const validatePassword = (password: string): E.Either<Errors, string> =>
  !password ? E.left(NEA.of('Password required'))
  : password.length < 8 ? E.left(NEA.of('Password too short'))
  : E.right(password)

const validateAge = (age: number | undefined): E.Either<Errors, number> =>
  age === undefined ? E.left(NEA.of('Age required'))
  : age < 18 ? E.left(NEA.of('Must be 18+'))
  : E.right(age)

// Combine all validations - collects ALL errors
const validateForm = (form: FormData) =>
  sequenceS(validation)({
    email: validateEmail(form.email),
    password: validatePassword(form.password),
    age: validateAge(form.age)
  })

// Usage
validateForm({ email: '', password: '123', age: 15 })
// Left(['Email required', 'Password too short', 'Must be 18+'])

validateForm({ email: 'a@b.com', password: 'longpassword', age: 25 })
// Right({ email: 'a@b.com', password: 'longpassword', age: 25 })
```

### Field-Level Errors for Forms

```typescript
interface FieldError {
  field: string
  message: string
}

type FormErrors = NEA.NonEmptyArray<FieldError>

const fieldError = (field: string, message: string): FormErrors =>
  NEA.of({ field, message })

const formValidation = E.getApplicativeValidation(NEA.getSemigroup<FieldError>())

// Now errors know which field they belong to
const validateEmail = (email: string): E.Either<FormErrors, string> =>
  !email ? E.left(fieldError('email', 'Required'))
  : !email.includes('@') ? E.left(fieldError('email', 'Invalid format'))
  : E.right(email)

// Easy to display in UI
const getFieldError = (errors: FormErrors, field: string): string | undefined =>
  errors.find(e => e.field === field)?.message
```

---

## 5. Async Operations (TaskEither)

For async operations that can fail, use `TaskEither`. It's like `Either` but for promises.

- `TaskEither<E, A>` = a function that returns `Promise<Either<E, A>>`
- Lazy: nothing runs until you execute it

```typescript
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'

// Wrap any async operation
const fetchUser = (id: string): TE.TaskEither<Error, User> =>
  TE.tryCatch(
    () => fetch(`/api/users/${id}`).then(r => r.json()),
    (e) => (e instanceof Error ? e : new Error(String(e)))
  )

// Chain async operations - just like Either
const getUserPosts = (userId: string): TE.TaskEither<Error, Post[]> =>
  pipe(
    fetchUser(userId),
    TE.chain(user => fetchPosts(user.id))
  )

// Execute when ready
const result = await getUserPosts('123')() // Returns Either<Error, Post[]>
```

### Before: Promise Chain with Error Handling

```typescript
// MESSY: try/catch mixed with promise chains
async function loadDashboard(userId: string) {
  try {
    const user = await fetchUser(userId)
    if (!user) throw new Error('User not found')

    let posts, notifications, settings
    try {
      [posts, notifications, settings] = await Promise.all([
        fetchPosts(user.id),
        fetchNotifications(user.id),
        fetchSettings(user.id)
      ])
    } catch (e) {
      // Which one failed? Who knows!
      console.error('Failed to load data', e)
      return null
    }

    return { user, posts, notifications, settings }
  } catch (e) {
    console.error('Failed to load user', e)
    return null
  }
}
```

### After: Clean TaskEither Pipeline

```typescript
import * as TE from 'fp-ts/TaskEither'
import { sequenceS } from 'fp-ts/Apply'
import { pipe } from 'fp-ts/function'

const loadDashboard = (userId: string) =>
  pipe(
    fetchUser(userId),
    TE.chain(user =>
      pipe(
        // Parallel fetch with sequenceS
        sequenceS(TE.ApplyPar)({
          posts: fetchPosts(user.id),
          notifications: fetchNotifications(user.id),
          settings: fetchSettings(user.id)
        }),
        TE.map(data => ({ user, ...data }))
      )
    )
  )

// Execute and handle both cases
pipe(
  loadDashboard('123'),
  TE.fold(
    (error) => T.of(renderError(error)),
    (data) => T.of(renderDashboard(data))
  )
)()
```

### Retry Failed Operations

```typescript
import * as T from 'fp-ts/Task'
import * as TE from 'fp-ts/TaskEither'
import { pipe } from 'fp-ts/function'

const retry = <E, A>(
  task: TE.TaskEither<E, A>,
  attempts: number,
  delayMs: number
): TE.TaskEither<E, A> =>
  pipe(
    task,
    TE.orElse((error) =>
      attempts > 1
        ? pipe(
            T.delay(delayMs)(T.of(undefined)),
            T.chain(() => retry(task, attempts - 1, delayMs * 2))
          )
        : TE.left(error)
    )
  )

// Retry up to 3 times with exponential backoff
const fetchWithRetry = retry(fetchUser('123'), 3, 1000)
```

### Fallback to Alternative

```typescript
// Try cache first, fall back to API
const getUserData = (id: string) =>
  pipe(
    fetchFromCache(id),
    TE.orElse(() => fetchFromApi(id)),
    TE.orElse(() => TE.right(defaultUser)) // Last resort default
  )
```

---

## 6. Converting Between Patterns

Real codebases have throwing functions, nullable values, and promises. Here's how to work with them.

### From Nullable to Either

```typescript
import * as E from 'fp-ts/Either'
import * as O from 'fp-ts/Option'

// Direct conversion
const user = users.find(u => u.id === id) // User | undefined
const result = E.fromNullable('User not found')(user)

// From Option
const maybeUser: O.Option<User> = O.fromNullable(user)
const eitherUser = pipe(
  maybeUser,
  E.fromOption(() => 'User not found')
)
```

### From Throwing Function to Either

```typescript
// Wrap at the boundary
const safeParse = <T>(schema: ZodSchema<T>) => (data: unknown): E.Either<ZodError, T> =>
  E.tryCatch(
    () => schema.parse(data),
    (e) => e as ZodError
  )

// Use throughout your code
const parseUser = safeParse(UserSchema)
const result = parseUser(rawData) // Either<ZodError, User>
```

### From Promise to TaskEither

```typescript
import * as TE from 'fp-ts/TaskEither'

// Wrap external async functions
const fetchJson = <T>(url: string): TE.TaskEither<Error, T> =>
  TE.tryCatch(
    () => fetch(url).then(r => r.json()),
    (e) => new Error(`Fetch failed: ${e}`)
  )

// Wrap axios, prisma, any async library
const getUserFromDb = (id: string): TE.TaskEither<DbError, User> =>
  TE.tryCatch(
    () => prisma.user.findUniqueOrThrow({ where: { id } }),
    (e) => ({ code: 'DB_ERROR', cause: e })
  )
```

### Back to Promise (Escape Hatch)

Sometimes you need a plain Promise for external APIs.

```typescript
import * as TE from 'fp-ts/TaskEither'
import * as E from 'fp-ts/Either'

const myTaskEither: TE.TaskEither<Error, User> = fetchUser('123')

// Option 1: Get the Either (preserves both cases)
const either: E.Either<Error, User> = await myTaskEither()

// Option 2: Throw on error (for legacy code)
const toThrowingPromise = <E, A>(te: TE.TaskEither<E, A>): Promise<A> =>
  te().then(E.fold(
    (error) => Promise.reject(error),
    (value) => Promise.resolve(value)
  ))

const user = await toThrowingPromise(fetchUser('123')) // Throws if Left

// Option 3: Default on error
const user = await pipe(
  fetchUser('123'),
  TE.getOrElse(() => T.of(defaultUser))
)()
```

---

## Real Scenarios

### Parse User Input Safely

```typescript
interface ParsedInput {
  id: number
  name: string
  tags: string[]
}

const parseInput = (raw: unknown): E.Either<string, ParsedInput> =>
  pipe(
    E.Do,
    E.bind('obj', () =>
      typeof raw === 'object' && raw !== null
        ? E.right(raw as Record<string, unknown>)
        : E.left('Input must be an object')
    ),
    E.bind('id', ({ obj }) =>
      typeof obj.id === 'number'
        ? E.right(obj.id)
        : E.left('id must be a number')
    ),
    E.bind('name', ({ obj }) =>
      typeof obj.name === 'string' && obj.name.length > 0
        ? E.right(obj.name)
        : E.left('name must be a non-empty string')
    ),
    E.bind('tags', ({ obj }) =>
      Array.isArray(obj.tags) && obj.tags.every(t => typeof t === 'string')
        ? E.right(obj.tags as string[])
        : E.left('tags must be an array of strings')
    ),
    E.map(({ id, name, tags }) => ({ id, name, tags }))
  )

// Usage
parseInput({ id: 1, name: 'test', tags: ['a', 'b'] })
// Right({ id: 1, name: 'test', tags: ['a', 'b'] })

parseInput({ id: 'wrong', name: '', tags: null })
// Left('id must be a number')
```

### API Call with Full Error Handling

```typescript
interface ApiError {
  code: string
  message: string
  status?: number
}

const createApiError = (message: string, code = 'UNKNOWN', status?: number): ApiError =>
  ({ code, message, status })

const fetchWithErrorHandling = <T>(url: string): TE.TaskEither<ApiError, T> =>
  pipe(
    TE.tryCatch(
      () => fetch(url),
      () => createApiError('Network error', 'NETWORK')
    ),
    TE.chain(response =>
      response.ok
        ? TE.tryCatch(
            () => response.json() as Promise<T>,
            () => createApiError('Invalid JSON', 'PARSE')
          )
        : TE.left(createApiError(
            `HTTP ${response.status}`,
            response.status === 404 ? 'NOT_FOUND' : 'HTTP_ERROR',
            response.status
          ))
    )
  )

// Usage with pattern matching on error codes
const handleUserFetch = (userId: string) =>
  pipe(
    fetchWithErrorHandling<User>(`/api/users/${userId}`),
    TE.fold(
      (error) => {
        switch (error.code) {
          case 'NOT_FOUND': return T.of(showNotFoundPage())
          case 'NETWORK': return T.of(showOfflineMessage())
          default: return T.of(showGenericError(error.message))
        }
      },
      (user) => T.of(showUserProfile(user))
    )
  )
```

### Process List Where Some Items Might Fail

```typescript
import * as A from 'fp-ts/Array'
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

interface ProcessResult<T> {
  successes: T[]
  failures: Array<{ item: unknown; error: string }>
}

// Process all, collect successes and failures separately
const processAllCollectErrors = <T, R>(
  items: T[],
  process: (item: T) => E.Either<string, R>
): ProcessResult<R> => {
  const results = items.map((item, index) =>
    pipe(
      process(item),
      E.mapLeft(error => ({ item, error, index }))
    )
  )

  return {
    successes: pipe(results, A.filterMap(E.toOption)),
    failures: pipe(
      results,
      A.filterMap(r => E.isLeft(r) ? O.some(r.left) : O.none)
    )
  }
}

// Usage
const parseNumbers = (inputs: string[]) =>
  processAllCollectErrors(inputs, input => {
    const n = parseInt(input, 10)
    return isNaN(n) ? E.left(`Invalid number: ${input}`) : E.right(n)
  })

parseNumbers(['1', 'abc', '3', 'def'])
// {
//   successes: [1, 3],
//   failures: [
//     { item: 'abc', error: 'Invalid number: abc', index: 1 },
//     { item: 'def', error: 'Invalid number: def', index: 3 }
//   ]
// }
```

### Bulk Operations with Partial Success

```typescript
import * as TE from 'fp-ts/TaskEither'
import * as T from 'fp-ts/Task'
import { pipe } from 'fp-ts/function'

interface BulkResult<T> {
  succeeded: T[]
  failed: Array<{ id: string; error: string }>
}

const bulkProcess = <T>(
  ids: string[],
  process: (id: string) => TE.TaskEither<string, T>
): T.Task<BulkResult<T>> =>
  pipe(
    ids,
    A.map(id =>
      pipe(
        process(id),
        TE.fold(
          (error) => T.of({ type: 'failed' as const, id, error }),
          (result) => T.of({ type: 'succeeded' as const, result })
        )
      )
    ),
    T.sequenceArray,
    T.map(results => ({
      succeeded: results
        .filter((r): r is { type: 'succeeded'; result: T } => r.type === 'succeeded')
        .map(r => r.result),
      failed: results
        .filter((r): r is { type: 'failed'; id: string; error: string } => r.type === 'failed')
        .map(({ id, error }) => ({ id, error }))
    }))
  )

// Usage
const deleteUsers = (userIds: string[]) =>
  bulkProcess(userIds, id =>
    pipe(
      deleteUser(id),
      TE.mapLeft(e => e.message)
    )
  )

// All operations run, you get a report of what worked and what didn't
```

---

## Quick Reference

| Pattern | Use When | Example |
|---------|----------|---------|
| `E.right(value)` | Creating a success | `E.right(42)` |
| `E.left(error)` | Creating a failure | `E.left('not found')` |
| `E.tryCatch(fn, onError)` | Wrapping throwing code | `E.tryCatch(() => JSON.parse(s), toError)` |
| `E.fromNullable(error)` | Converting nullable | `E.fromNullable('missing')(maybeValue)` |
| `E.map(fn)` | Transform success | `pipe(result, E.map(x => x * 2))` |
| `E.mapLeft(fn)` | Transform error | `pipe(result, E.mapLeft(addContext))` |
| `E.chain(fn)` | Chain operations | `pipe(getA(), E.chain(a => getB(a.id)))` |
| `E.chainW(fn)` | Chain with different error type | `pipe(validate(), E.chainW(save))` |
| `E.fold(onError, onSuccess)` | Handle both cases | `E.fold(showError, showData)` |
| `E.getOrElse(onError)` | Extract with default | `E.getOrElse(() => 0)` |
| `E.filterOrElse(pred, onFalse)` | Validate with error | `E.filterOrElse(x => x > 0, () => 'must be positive')` |
| `sequenceS(validation)({...})` | Collect all errors | Form validation |

### TaskEither Equivalents

All Either operations have TaskEither equivalents:
- `TE.right`, `TE.left`, `TE.tryCatch`
- `TE.map`, `TE.mapLeft`, `TE.chain`, `TE.chainW`
- `TE.fold`, `TE.getOrElse`, `TE.filterOrElse`
- `TE.orElse` for fallbacks

---

## Summary

1. **Return errors as values** - Use Either/TaskEither instead of throwing
2. **Chain with confidence** - `chain` stops at first error automatically
3. **Collect all errors when needed** - Use validation applicative for forms
4. **Wrap at boundaries** - Convert throwing/Promise code at the edges
5. **Match at the end** - Use `fold` to handle both cases when you're ready to act

The payoff: TypeScript tracks your errors, no more forgotten try/catch, clear control flow, and composable error handling.
