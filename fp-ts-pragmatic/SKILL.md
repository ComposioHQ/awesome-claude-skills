---
name: fp-ts-pragmatic
description: A practical, jargon-free guide to fp-ts functional programming - the 80/20 approach that gets results without the academic overhead. Use when writing TypeScript with fp-ts library.
risk: safe
source: https://github.com/whatiskadudoing/fp-ts-skills
---

# Pragmatic Functional Programming

**Read this first.** This guide cuts through the academic jargon and shows you what actually matters. No category theory. No abstract nonsense. Just patterns that make your code better.

## When to Use This Skill

- When starting with fp-ts and need practical guidance
- When writing TypeScript code that handles nullable values, errors, or async operations
- When you want cleaner, more maintainable functional code without the academic overhead
- When refactoring imperative code to functional style

## The Golden Rule

> **If functional programming makes your code harder to read, don't use it.**

FP is a tool, not a religion. Use it when it helps. Skip it when it doesn't.

---

## The 80/20 of FP

These five patterns give you most of the benefits. Master these before exploring anything else.

### 1. Pipe: Chain Operations Clearly

Instead of nesting function calls or creating intermediate variables, chain operations in reading order.

```typescript
import { pipe } from 'fp-ts/function'

// Before: Hard to read (inside-out)
const result = format(validate(parse(input)))

// Before: Too many variables
const parsed = parse(input)
const validated = validate(parsed)
const result = format(validated)

// After: Clear, linear flow
const result = pipe(
  input,
  parse,
  validate,
  format
)
```

**When to use pipe:**
- 3+ transformations on the same data
- You find yourself naming throwaway variables
- Logic reads better top-to-bottom

**When to skip pipe:**
- Just 1-2 operations (direct call is fine)
- The operations don't naturally chain

### 2. Option: Handle Missing Values Without null Checks

Stop writing `if (x !== null && x !== undefined)` everywhere.

```typescript
import * as O from 'fp-ts/Option'
import { pipe } from 'fp-ts/function'

// Before: Defensive null checking
function getUserCity(user: User | null): string {
  if (user === null) return 'Unknown'
  if (user.address === null) return 'Unknown'
  if (user.address.city === null) return 'Unknown'
  return user.address.city
}

// After: Chain through potential missing values
const getUserCity = (user: User | null): string =>
  pipe(
    O.fromNullable(user),
    O.flatMap(u => O.fromNullable(u.address)),
    O.flatMap(a => O.fromNullable(a.city)),
    O.getOrElse(() => 'Unknown')
  )
```

**Plain language translation:**
- `O.fromNullable(x)` = "wrap this value, treating null/undefined as 'nothing'"
- `O.flatMap(fn)` = "if we have something, apply this function"
- `O.getOrElse(() => default)` = "unwrap, or use this default if nothing"

### 3. Either: Make Errors Explicit

Stop throwing exceptions for expected failures. Return errors as values.

```typescript
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

// Before: Hidden failure mode
function parseAge(input: string): number {
  const age = parseInt(input, 10)
  if (isNaN(age)) throw new Error('Invalid age')
  if (age < 0) throw new Error('Age cannot be negative')
  return age
}

// After: Errors are visible in the type
function parseAge(input: string): E.Either<string, number> {
  const age = parseInt(input, 10)
  if (isNaN(age)) return E.left('Invalid age')
  if (age < 0) return E.left('Age cannot be negative')
  return E.right(age)
}

// Using it
const result = parseAge(userInput)
if (E.isRight(result)) {
  console.log(`Age is ${result.right}`)
} else {
  console.log(`Error: ${result.left}`)
}
```

**Plain language translation:**
- `E.right(value)` = "success with this value"
- `E.left(error)` = "failure with this error"
- `E.isRight(x)` = "did it succeed?"

### 4. Map: Transform Without Unpacking

Transform values inside containers without extracting them first.

```typescript
import * as O from 'fp-ts/Option'
import * as E from 'fp-ts/Either'
import * as A from 'fp-ts/Array'
import { pipe } from 'fp-ts/function'

// Transform inside Option
const maybeUser: O.Option<User> = O.some({ name: 'Alice', age: 30 })
const maybeName: O.Option<string> = pipe(
  maybeUser,
  O.map(user => user.name)
)

// Transform inside Either
const result: E.Either<Error, number> = E.right(5)
const doubled: E.Either<Error, number> = pipe(
  result,
  E.map(n => n * 2)
)

// Transform arrays (same concept!)
const numbers = [1, 2, 3]
const doubled = pipe(
  numbers,
  A.map(n => n * 2)
)
```

### 5. FlatMap: Chain Operations That Might Fail

When each step might fail, chain them together.

```typescript
import * as E from 'fp-ts/Either'
import { pipe } from 'fp-ts/function'

const parseJSON = (s: string): E.Either<string, unknown> =>
  E.tryCatch(() => JSON.parse(s), () => 'Invalid JSON')

const extractEmail = (data: unknown): E.Either<string, string> => {
  if (typeof data === 'object' && data !== null && 'email' in data) {
    return E.right((data as { email: string }).email)
  }
  return E.left('No email field')
}

const validateEmail = (email: string): E.Either<string, string> =>
  email.includes('@') ? E.right(email) : E.left('Invalid email format')

// Chain all steps - if any fails, the whole thing fails
const getValidEmail = (input: string): E.Either<string, string> =>
  pipe(
    parseJSON(input),
    E.flatMap(extractEmail),
    E.flatMap(validateEmail)
  )

// Success path: Right('user@example.com')
// Any failure: Left('specific error message')
```

**Plain language:** `flatMap` means "if this succeeded, try the next thing"

---

## When NOT to Use FP

Functional programming is not always the answer. Here's when to keep it simple.

### Simple Null Checks

```typescript
// Just use optional chaining - it's built into the language
const city = user?.address?.city ?? 'Unknown'

// DON'T overcomplicate it
const city = pipe(
  O.fromNullable(user),
  O.flatMap(u => O.fromNullable(u.address)),
  O.flatMap(a => O.fromNullable(a.city)),
  O.getOrElse(() => 'Unknown')
)
```

### Simple Loops

```typescript
// A for loop is fine when you need early exit or complex logic
function findFirst(items: Item[], predicate: (i: Item) => boolean): Item | null {
  for (const item of items) {
    if (predicate(item)) return item
  }
  return null
}

// DON'T force FP when it doesn't help
const result = pipe(
  items,
  A.findFirst(predicate),
  O.toNullable
)
```

### Performance-Critical Code

```typescript
// For hot paths, imperative is faster (no intermediate arrays)
function sumLarge(numbers: number[]): number {
  let sum = 0
  for (let i = 0; i < numbers.length; i++) {
    sum += numbers[i]
  }
  return sum
}

// fp-ts creates intermediate structures
const sum = pipe(numbers, A.reduce(0, (acc, n) => acc + n))
```

### When Your Team Doesn't Know FP

If you're the only one who can read the code, it's not good code.

```typescript
// If your team knows this pattern
async function getUser(id: string): Promise<User | null> {
  try {
    const response = await fetch(`/api/users/${id}`)
    if (!response.ok) return null
    return await response.json()
  } catch {
    return null
  }
}

// Don't force this on them
const getUser = (id: string): TE.TaskEither<Error, User> =>
  pipe(
    TE.tryCatch(() => fetch(`/api/users/${id}`), E.toError),
    TE.flatMap(r => r.ok ? TE.right(r) : TE.left(new Error('Not found'))),
    TE.flatMap(r => TE.tryCatch(() => r.json(), E.toError))
  )
```

---

## Quick Wins: Easy Changes That Improve Code Today

### 1. Replace Nested Ternaries with pipe + fold

```typescript
// Before: Nested ternary nightmare
const message = user === null
  ? 'No user'
  : user.isAdmin
    ? `Admin: ${user.name}`
    : `User: ${user.name}`

// After: Clear case handling
const message = pipe(
  O.fromNullable(user),
  O.fold(
    () => 'No user',
    (u) => u.isAdmin ? `Admin: ${u.name}` : `User: ${u.name}`
  )
)
```

### 2. Replace try-catch with tryCatch

```typescript
// Before: try-catch everywhere
let config
try {
  config = JSON.parse(rawConfig)
} catch {
  config = defaultConfig
}

// After: One-liner
const config = pipe(
  E.tryCatch(() => JSON.parse(rawConfig), () => 'parse error'),
  E.getOrElse(() => defaultConfig)
)
```

### 3. Replace undefined Returns with Option

```typescript
// Before: Caller might forget to check
function findUser(id: string): User | undefined {
  return users.find(u => u.id === id)
}

// After: Type forces caller to handle missing case
function findUser(id: string): O.Option<User> {
  return O.fromNullable(users.find(u => u.id === id))
}
```

### 4. Replace Error Strings with Typed Errors

```typescript
// Before: Just strings
function validate(data: unknown): E.Either<string, User> {
  // ...
  return E.left('validation failed')
}

// After: Structured errors
type ValidationError = {
  field: string
  message: string
}

function validate(data: unknown): E.Either<ValidationError, User> {
  // ...
  return E.left({ field: 'email', message: 'Invalid format' })
}
```

### 5. Use const Assertions for Error Types

```typescript
// Create specific error types without classes
const NotFound = (id: string) => ({ _tag: 'NotFound' as const, id })
const Unauthorized = { _tag: 'Unauthorized' as const }
const ValidationFailed = (errors: string[]) =>
  ({ _tag: 'ValidationFailed' as const, errors })

type AppError =
  | ReturnType<typeof NotFound>
  | typeof Unauthorized
  | ReturnType<typeof ValidationFailed>

// Now you can pattern match
const handleError = (error: AppError): string => {
  switch (error._tag) {
    case 'NotFound': return `Item ${error.id} not found`
    case 'Unauthorized': return 'Please log in'
    case 'ValidationFailed': return error.errors.join(', ')
  }
}
```

---

## Common Refactors: Before and After

### Callback Hell to Pipe

```typescript
// Before
fetchUser(id, (user) => {
  if (!user) return handleNoUser()
  fetchPosts(user.id, (posts) => {
    if (!posts) return handleNoPosts()
    fetchComments(posts[0].id, (comments) => {
      render(user, posts, comments)
    })
  })
})

// After (with TaskEither for async)
import * as TE from 'fp-ts/TaskEither'

const loadData = (id: string) =>
  pipe(
    fetchUser(id),
    TE.flatMap(user => pipe(
      fetchPosts(user.id),
      TE.map(posts => ({ user, posts }))
    )),
    TE.flatMap(({ user, posts }) => pipe(
      fetchComments(posts[0].id),
      TE.map(comments => ({ user, posts, comments }))
    ))
  )

// Execute
const result = await loadData('123')()
pipe(
  result,
  E.fold(handleError, ({ user, posts, comments }) => render(user, posts, comments))
)
```

### Multiple null Checks to Option Chain

```typescript
// Before
function getManagerEmail(employee: Employee): string | null {
  if (!employee.department) return null
  if (!employee.department.manager) return null
  if (!employee.department.manager.email) return null
  return employee.department.manager.email
}

// After
const getManagerEmail = (employee: Employee): O.Option<string> =>
  pipe(
    O.fromNullable(employee.department),
    O.flatMap(d => O.fromNullable(d.manager)),
    O.flatMap(m => O.fromNullable(m.email))
  )

// Use it
pipe(
  getManagerEmail(employee),
  O.fold(
    () => sendToDefault(),
    (email) => sendTo(email)
  )
)
```

### Validation with Multiple Checks

```typescript
// Before: Throws on first error
function validateUser(data: unknown): User {
  if (!data || typeof data !== 'object') throw new Error('Must be object')
  const obj = data as Record<string, unknown>
  if (typeof obj.email !== 'string') throw new Error('Email required')
  if (!obj.email.includes('@')) throw new Error('Invalid email')
  if (typeof obj.age !== 'number') throw new Error('Age required')
  if (obj.age < 0) throw new Error('Age must be positive')
  return obj as User
}

// After: Returns first error, type-safe
const validateUser = (data: unknown): E.Either<string, User> =>
  pipe(
    E.Do,
    E.bind('obj', () =>
      typeof data === 'object' && data !== null
        ? E.right(data as Record<string, unknown>)
        : E.left('Must be object')
    ),
    E.bind('email', ({ obj }) =>
      typeof obj.email === 'string' && obj.email.includes('@')
        ? E.right(obj.email)
        : E.left('Valid email required')
    ),
    E.bind('age', ({ obj }) =>
      typeof obj.age === 'number' && obj.age >= 0
        ? E.right(obj.age)
        : E.left('Valid age required')
    ),
    E.map(({ email, age }) => ({ email, age }))
  )
```

### Promise Chain to TaskEither

```typescript
// Before
async function processOrder(orderId: string): Promise<Receipt> {
  const order = await fetchOrder(orderId)
  if (!order) throw new Error('Order not found')

  const validated = await validateOrder(order)
  if (!validated.success) throw new Error(validated.error)

  const payment = await processPayment(validated.order)
  if (!payment.success) throw new Error('Payment failed')

  return generateReceipt(payment)
}

// After
const processOrder = (orderId: string): TE.TaskEither<string, Receipt> =>
  pipe(
    fetchOrderTE(orderId),
    TE.flatMap(order =>
      order ? TE.right(order) : TE.left('Order not found')
    ),
    TE.flatMap(validateOrderTE),
    TE.flatMap(processPaymentTE),
    TE.map(generateReceipt)
  )
```

---

## The Readability Rule

Before using any FP pattern, ask: **"Would a junior developer understand this?"**

### Too Clever (Avoid)

```typescript
const result = pipe(
  data,
  A.filter(flow(prop('status'), equals('active'))),
  A.map(flow(prop('value'), multiply(2))),
  A.reduce(monoid.concat, monoid.empty),
  O.fromPredicate(gt(threshold))
)
```

### Just Right (Prefer)

```typescript
const activeItems = data.filter(item => item.status === 'active')
const doubledValues = activeItems.map(item => item.value * 2)
const total = doubledValues.reduce((sum, val) => sum + val, 0)
const result = total > threshold ? O.some(total) : O.none
```

### The Middle Ground (Often Best)

```typescript
const result = pipe(
  data,
  A.filter(item => item.status === 'active'),
  A.map(item => item.value * 2),
  A.reduce(0, (sum, val) => sum + val),
  total => total > threshold ? O.some(total) : O.none
)
```

---

## Cheat Sheet

| What you want | Plain language | fp-ts |
|--------------|----------------|-------|
| Handle null/undefined | "Wrap this nullable" | `O.fromNullable(x)` |
| Default for missing | "Use this if nothing" | `O.getOrElse(() => default)` |
| Transform if present | "If something, change it" | `O.map(fn)` |
| Chain nullable operations | "If something, try this" | `O.flatMap(fn)` |
| Return success | "Worked, here's the value" | `E.right(value)` |
| Return failure | "Failed, here's why" | `E.left(error)` |
| Wrap throwing function | "Try this, catch errors" | `E.tryCatch(fn, onError)` |
| Handle both cases | "Do this for error, that for success" | `E.fold(onLeft, onRight)` |
| Chain operations | "Then do this, then that" | `pipe(x, fn1, fn2, fn3)` |

---

## When to Level Up

Once comfortable with these patterns, explore:

1. **TaskEither** - Async operations that can fail (replaces Promise + try/catch)
2. **Validation** - Collect ALL errors instead of stopping at first
3. **Reader** - Dependency injection without classes
4. **Do notation** - Cleaner syntax for multiple bindings

But don't rush. The basics here will handle 80% of real-world scenarios. Get comfortable with these before adding more tools to your belt.

---

## Summary

1. **Use pipe** for 3+ operations
2. **Use Option** for nullable chains
3. **Use Either** for operations that can fail
4. **Use map** to transform wrapped values
5. **Use flatMap** to chain operations that might fail
6. **Skip FP** when it hurts readability
7. **Keep it simple** - if your team can't read it, it's not good code
