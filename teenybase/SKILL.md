---
name: teenybase
description: Set up and manage Teenybase backends — a TypeScript-configured backend framework on Cloudflare Workers + D1. Use when the user wants to create a backend with CRUD endpoints, authentication, row-level security, auto-migrations, OpenAPI docs, or an admin panel from a single config file.
---

# Teenybase Backend Development

Teenybase is a pre-alpha backend framework where the entire backend is defined in a single `teenybase.ts` config file. It runs on Cloudflare Workers + D1 and generates REST API endpoints, authentication, row-level security rules, SQL migrations, OpenAPI docs, and an admin panel automatically.

**Prerequisite:** Ensure the `teeny` CLI is available. Install globally with `npm install -g teenybase`, or use `npx teeny` to run commands without a global install.

## When to Use This Skill

- User wants to create a new backend or API from scratch
- User needs auth (email/password, JWT, OAuth) without writing auth code
- User wants CRUD endpoints generated from a schema definition
- User wants row-level security rules (e.g., "users can only see their own records")
- User is adding a backend to an existing frontend project
- User wants to deploy a serverless backend to the edge

## Before You Start

Before modifying `teenybase.ts`, understand what the user is building. If the user has not provided clear instructions, ask them to describe what their backend needs to do.

Users typically describe intentions, not schemas: "I need login", "I need a database for recipes", "I need to process payments and track subscribers." Infer tables, auth setup, and access rules from their description.

Determine whether this is a **new project** or **adding teenybase to an existing project**. If unclear, ask.

## Non-Interactive Flags

Always pass these flags when running CLI commands non-interactively. Without them, commands launch arrow-key prompts that hang when stdin is not a TTY.

| Flag | Purpose |
|---|---|
| `-t, --template <template>` | `with-auth` (users + auth + rules) or `blank` (empty config). |
| `-y, --yes` | Skip all confirmation prompts, use defaults. |

## Creating a New Project

```bash
teeny create my-app -t with-auth -y
cd my-app
```

This scaffolds all files and runs `npm install`. The `with-auth` template includes a `users` table with email/password auth and row-level security. Use `-t blank` for an empty project.

## Adding to an Existing Project

```bash
npm install teenybase hono
npm install -D wrangler @cloudflare/workers-types typescript
teeny init -y
```

`teeny init` detects existing files and only creates what is missing. It will not overwrite `package.json` or `tsconfig.json`. Install dependencies yourself with the `npm install` lines above since `teeny init` does not modify `package.json`.

## Key Files

| File | Purpose |
|---|---|
| `teenybase.ts` | Backend config -- tables, fields, auth, rules, actions. The main file you edit. |
| `src/index.ts` | Worker entry point. Usually unchanged unless adding custom routes or R2 storage. |
| `wrangler.jsonc` | Cloudflare Workers config, D1/R2 bindings. |
| `.dev.vars` | Local secrets (JWT_SECRET, JWT_SECRET_USERS, ADMIN_JWT_SECRET, etc.). |
| `.prod.vars` | Production secrets (same keys, strong values). Not auto-created -- copy from `.dev.vars`. |
| `migrations/` | Auto-generated SQL. Do not edit manually. |

## Understanding the Config

`teenybase.ts` is the entire backend definition:

```typescript
import { DatabaseSettings, TableAuthExtensionData,
         TableRulesExtensionData } from 'teenybase'
import { baseFields, authFields,
         createdTrigger, updatedTrigger } from 'teenybase/scaffolds/fields'

export default {
    appUrl: 'http://localhost:8787',
    jwtSecret: '$JWT_SECRET',               // $-prefixed = resolved from .dev.vars / .prod.vars
    tables: [{
        name: 'users',
        autoSetUid: true,
        fields: [
            ...baseFields,                  // id + created + updated
            ...authFields,                  // username, email, password, name, avatar, role, etc.
        ],
        triggers: [createdTrigger, updatedTrigger],
        extensions: [
            { name: 'auth',
              jwtSecret: '$JWT_SECRET_USERS',
              jwtTokenDuration: 3600,
              maxTokenRefresh: 5,
            } as TableAuthExtensionData,
            { name: 'rules',
              listRule: 'auth.uid == id',
              viewRule: 'auth.uid == id',
              createRule: 'true',
              updateRule: 'auth.uid == id',
              deleteRule: 'auth.uid == id',
            } as TableRulesExtensionData,
        ],
    }],
} satisfies DatabaseSettings
```

**Key concepts:**
- `$` prefix resolves env vars from `.dev.vars` (local) or `.prod.vars` (production).
- Rules are expressions -- `auth.uid == id` becomes a SQL WHERE clause.
- Extensions add behavior: `auth` enables sign-up/login/OAuth, `rules` enforces row-level security, `crud` is implicit.
- Everything else is auto-generated: REST API, Swagger docs, admin panel.

## Local Development Workflow

After setup (new project or init):

```bash
teeny generate --local    # Generate migrations from config changes
teeny deploy --local      # Apply migrations to local SQLite database
teeny dev --local         # Start dev server at http://localhost:8787
```

Available endpoints after starting the dev server:
- Health check: `/api/v1/health`
- Swagger UI: `/api/v1/doc/ui`
- Admin panel: `/api/v1/pocket/`

### Development Loop

1. Edit `teenybase.ts`
2. Run `teeny generate --local` and `teeny deploy --local`
3. Run `teeny dev --local`
4. Test with curl, Swagger UI, or the admin panel
5. Repeat from step 1, or deploy to production

## Adding a Table

Add a new entry to the `tables` array in `teenybase.ts`. Example -- a `posts` table linked to `users`:

```typescript
{
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
},
```

Add `sqlValue` to your teenybase import, then run:

```bash
teeny generate --local && teeny deploy --local && teeny dev --local
```

## Row-Level Security (Rules)

The `rules` extension injects SQL WHERE clauses. Rules are expressions:

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

## API Endpoint Reference

Base URL: `http://localhost:8787/api/v1` (local). For deployed apps, run `teeny status` to get the URL, then append `/api/v1`.

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
POST   /table/{table}/auth/request-verification     Authorization: Bearer <token>
POST   /table/{table}/auth/confirm-verification     { "token" }
POST   /table/{table}/auth/logout                   Authorization: Bearer <token>
```

**Auth header:** `Authorization: Bearer <token>`

**Other:** `GET /health`, `GET /doc/ui` (Swagger), `GET /doc` (OpenAPI JSON)

## Deploy to Production (Teenybase Cloud)

**WARNING:** Deploying to production applies migrations to the live database. Review generated migrations before deploying. Back up production data if the deployment includes destructive schema changes (dropping columns or tables).

```bash
teeny register                # Create account (one-time, free)
teeny deploy --remote --yes   # Deploy to production
teeny status                  # See live URL
```

On first deploy, secrets are auto-generated and saved to `.prod.vars`. Never commit `.prod.vars` to version control.

To upload custom production secrets:

```bash
teeny secrets --remote --upload    # Uploads .prod.vars to production
```

## CLI Quick Reference

```bash
teeny create <name> [-t <tpl>] [-y]  # Scaffold new project
teeny init [-t <tpl>] [-y]           # Add teenybase to existing project
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

## Testing the API with curl

```bash
# Sign up
curl -X POST http://localhost:8787/api/v1/table/users/auth/sign-up \
  -H 'Content-Type: application/json' \
  -d '{ "username": "testuser", "email": "test@example.com", "password": "mypassword", "name": "Test User" }'

# Login (response includes JWT token and refresh_token)
curl -X POST http://localhost:8787/api/v1/table/users/auth/login-password \
  -H 'Content-Type: application/json' \
  -d '{ "identity": "test@example.com", "password": "mypassword" }'

# Query data (authenticated)
curl http://localhost:8787/api/v1/table/users/select \
  -H 'Authorization: Bearer <token-from-login>'
```

## Tips

- The config file is TypeScript with full IDE autocomplete -- use `satisfies DatabaseSettings` for type checking.
- `teeny generate --local` is non-destructive; it only creates migration files. `teeny deploy` applies them.
- Use `teeny inspect --validate` to check your config for errors without deploying.
- The admin panel (PocketUI) at `/api/v1/pocket/` uses passwords from `.dev.vars` (POCKET_UI_VIEWER_PASSWORD for read-only, POCKET_UI_EDITOR_PASSWORD for read+write).
- Change all default secrets in `.dev.vars` and `.prod.vars` before any real usage.
- Teenybase is pre-alpha. It is suitable for side projects and MVPs, not yet proven for high-stakes production.
