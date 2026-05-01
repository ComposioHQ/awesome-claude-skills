---
name: teenybase
description: Set up and manage Teenybase backends — a TypeScript-configured backend framework on Cloudflare Workers + D1. Use when the user wants to create a backend with CRUD endpoints, authentication, row-level security, auto-migrations, OpenAPI docs, or an admin panel from a single config file.
---

# Teenybase

Teenybase is a pre-alpha backend framework where the entire backend is defined in a single `teenybase.ts` config file. It runs on Cloudflare Workers + D1 and generates REST API endpoints, authentication, row-level security rules, SQL migrations, OpenAPI docs, and an admin panel automatically. No backend code, no ORM, no route files.

**Prerequisite:** Ensure the `teeny` CLI is available. Install globally with `npm install -g teenybase`, or use `npx teeny` to run commands without a global install. Requires Node.js >= 18.14.1.

## When to Use This Skill

- User wants to create a new backend or API from scratch on Cloudflare Workers
- User needs auth (email/password, JWT, OAuth) without writing auth code
- User wants CRUD endpoints generated from a schema definition
- User wants row-level security rules (e.g., "users can only see their own records")
- User is adding a backend to an existing frontend project
- User wants to deploy a serverless backend to the edge

## What This Skill Does

1. **Scaffolds projects**: Creates a new Teenybase project or adds Teenybase to an existing project with a single command.
2. **Generates typed config**: Produces a `teenybase.ts` config file defining tables, fields, auth, row-level security rules, and actions.
3. **Manages migrations**: Generates SQL migrations from config changes and applies them locally or to production.
4. **Runs local dev**: Starts a local dev server with full REST API, Swagger docs, and admin panel.
5. **Deploys to production**: Deploys to Teenybase Cloud or self-hosted Cloudflare infrastructure.

## How to Use

### Basic Usage

```
Create a Teenybase backend for a todo app with users and tasks. Users sign up with email/password. Each user can only see and edit their own tasks.
```

### Advanced Usage

```
Add Teenybase to my existing project. I need a users table with auth, a projects table owned by users, and a tasks table under projects. Row-level security: users see only their own projects and tasks. Tasks have title, description, status (todo/in-progress/done), and due_date. Add an action to mark all tasks in a project as done. Set up local dev and show me the Swagger docs.
```

## Example

**User**: "Create a Teenybase backend for a blog with users and posts. Users can sign up and log in. Posts have author, title, body, and published flag. Anyone can list published posts, but only the author can see drafts or edit their posts."

**Output**:

```bash
teeny create blog-app -t with-auth -y
cd blog-app
```

Then edit `teenybase.ts` to add a posts table:

```typescript
import { DatabaseSettings, TableAuthExtensionData,
         TableRulesExtensionData, sqlValue } from 'teenybase'
import { baseFields, authFields,
         createdTrigger, updatedTrigger } from 'teenybase/scaffolds/fields'

export default {
    appUrl: 'http://localhost:8787',
    jwtSecret: '$JWT_SECRET',
    tables: [{
        name: 'users',
        autoSetUid: true,
        fields: [...baseFields, ...authFields],
        triggers: [createdTrigger, updatedTrigger],
        extensions: [
            { name: 'auth', jwtSecret: '$JWT_SECRET_USERS',
              jwtTokenDuration: 3600, maxTokenRefresh: 5 } as TableAuthExtensionData,
            { name: 'rules',
              createRule: 'true',
              viewRule: 'auth.uid == id',
              updateRule: 'auth.uid == id',
              deleteRule: 'auth.uid == id',
            } as TableRulesExtensionData,
        ],
    }, {
        name: 'posts',
        autoSetUid: true,
        fields: [
            ...baseFields,
            { name: 'author_id', type: 'relation', sqlType: 'text', notNull: true,
              foreignKey: { table: 'users', column: 'id' } },
            { name: 'title', type: 'text', sqlType: 'text', notNull: true },
            { name: 'body', type: 'text', sqlType: 'text' },
            { name: 'published', type: 'bool', sqlType: 'boolean', default: sqlValue(false) },
        ],
        triggers: [createdTrigger, updatedTrigger],
        extensions: [
            { name: 'rules',
              listRule: 'published == true | auth.uid == author_id',
              viewRule: 'published == true | auth.uid == author_id',
              createRule: 'auth.uid != null & author_id == auth.uid',
              updateRule: 'auth.uid == author_id',
              deleteRule: 'auth.uid == author_id',
            } as TableRulesExtensionData,
        ],
    }],
} satisfies DatabaseSettings
```

```bash
teeny generate --local    # Generate migrations
teeny deploy --local      # Apply migrations to local DB
teeny dev --local         # Start dev server at http://localhost:8787
```

Swagger docs at `http://localhost:8787/api/v1/doc/ui`, admin panel at `http://localhost:8787/api/v1/pocket/`.

## Reference

### Non-Interactive Flags

Always pass these flags when running CLI commands non-interactively:

| Flag | Purpose |
|---|---|
| `-t, --template <template>` | `with-auth` (users + auth + rules) or `blank` (empty config). |
| `-y, --yes` | Skip all confirmation prompts, use defaults. |

### Creating a New Project

```bash
teeny create my-app -t with-auth -y
cd my-app
```

Scaffolds all files and runs `npm install`. The `with-auth` template includes a `users` table with email/password auth and row-level security.

### Adding to an Existing Project

```bash
npm install teenybase hono
npm install -D wrangler @cloudflare/workers-types typescript
teeny init -y
```

### Key Files

| File | Purpose |
|---|---|
| `teenybase.ts` | Backend config -- tables, fields, auth, rules, actions. |
| `src/index.ts` | Worker entry point. Usually unchanged. |
| `wrangler.jsonc` | Cloudflare Workers config, D1/R2 bindings. |
| `.dev.vars` | Local secrets (JWT_SECRET, JWT_SECRET_USERS, etc.). |
| `.prod.vars` | Production secrets. Never commit to version control. |
| `migrations/` | Auto-generated SQL. Do not edit manually. |

### Config Concepts

- `$` prefix resolves env vars from `.dev.vars` (local) or `.prod.vars` (production).
- Rules are expressions -- `auth.uid == id` becomes a SQL WHERE clause.
- Extensions add behavior: `auth` enables sign-up/login/OAuth, `rules` enforces row-level security.
- `satisfies DatabaseSettings` gives full TypeScript autocomplete and type checking.

### Row-Level Security

The `rules` extension injects SQL WHERE clauses:

```typescript
{ name: 'rules',
  listRule: 'auth.uid == owner_id',
  viewRule: 'auth.uid == owner_id',
  createRule: 'auth.uid != null',
  updateRule: 'auth.uid == owner_id',
  deleteRule: 'auth.uid == owner_id',
} as TableRulesExtensionData
```

**Variables:** `auth.uid` (authenticated user's ID, null if not logged in), any column name, `true`/`false`, `null` (deny all).

**Operators:** `==`, `!=`, `>`, `<`, `>=`, `<=`, `~` (LIKE), `!~` (NOT LIKE), `in`, `@@` (FTS), `&` (AND), `|` (OR).

### API Endpoints

Base URL: `http://localhost:8787/api/v1` (local).

**CRUD:**
```
POST   /table/{table}/insert      { "values": {...}, "returning": "*" }
GET    /table/{table}/select      ?where=...&order=...&limit=...
GET    /table/{table}/list        Returns { items, total }
GET    /table/{table}/view/{id}
POST   /table/{table}/update      { "where": "id == '...'", "setValues": {...} }
POST   /table/{table}/edit/{id}   { "field": "value" }
POST   /table/{table}/delete      { "where": "id == '...'" }
```

**Auth:**
```
POST   /table/{table}/auth/sign-up              { "username", "email", "password", "name" }
POST   /table/{table}/auth/login-password       { "identity", "password" }
POST   /table/{table}/auth/refresh-token        { "refresh_token" }
POST   /table/{table}/auth/request-password-reset   { "email" }
POST   /table/{table}/auth/confirm-password-reset   { "token", "password" }
POST   /table/{table}/auth/logout                   Authorization: Bearer <token>
```

### Deploy to Production

**WARNING:** Deploying to production applies migrations to the live database. Review generated migrations before deploying.

```bash
teeny register                # Create account (one-time, free)
teeny deploy --remote --yes   # Deploy to production
teeny status                  # See live URL
teeny secrets --remote --upload   # Upload .prod.vars to production
```

### CLI Quick Reference

```bash
teeny create <name> [-t <tpl>] [-y]  # Scaffold new project
teeny init [-t <tpl>] [-y]           # Add to existing project
teeny generate --local               # Generate migrations from config
teeny deploy --local                 # Apply migrations locally
teeny dev --local                    # Start local dev server (port 8787)
teeny deploy --remote --yes          # Deploy to production
teeny register                       # Create Teenybase Cloud account
teeny login                          # Log in
teeny status                         # Show deployed URL and status
teeny secrets --remote --upload      # Upload .prod.vars to production
teeny list                           # List deployed workers
teeny delete [name]                  # Delete a deployed worker
teeny logs                           # Stream production logs
teeny inspect [--table <n>]          # Dump resolved config as JSON
teeny --help                         # List all commands
```

## Tips

- The config file is TypeScript with full IDE autocomplete -- use `satisfies DatabaseSettings` for type checking.
- `teeny generate --local` is non-destructive; it only creates migration files. `teeny deploy` applies them.
- Use `teeny inspect --validate` to check your config for errors without deploying.
- The admin panel (PocketUI) at `/api/v1/pocket/` uses passwords from `.dev.vars`.
- Change all default secrets in `.dev.vars` and `.prod.vars` before any real usage.
- Teenybase is pre-alpha. It is suitable for side projects and MVPs, not yet proven for high-stakes production.

## Common Use Cases

- Scaffolding a backend for a new side project or MVP
- Adding auth and CRUD API to an existing frontend app
- Building a multi-table backend with foreign keys and row-level security
- Prototyping a SaaS backend with user accounts, roles, and access rules
- Deploying a serverless API to the edge with zero infrastructure setup
