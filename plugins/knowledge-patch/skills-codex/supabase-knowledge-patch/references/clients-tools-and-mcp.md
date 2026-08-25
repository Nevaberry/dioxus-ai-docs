# Clients, developer tools, and MCP

## Node.js 20 runtime floor (supabase-js-2.101.0)

Starting with 2.79.0, all Supabase JavaScript libraries require Node.js 20 or later and rely on native `fetch`. Version 2.78.0 is the last release that supports Node.js 18.

## PostgREST filters and request coverage (supabase-js-2.101.0)

PostgREST adds `notin`, `isdistinct`, and regex pattern-matching operators, along with URL-length validation, timeout protection, and PostgREST 14 compatibility. `maybeSingle()` now works across all request methods.

## Stricter generated-query types (supabase-js-2.101.0)

Table and view names passed to `from()` and column names passed to `eq()` or `neq()` are now type-checked; embedded functions and cross-schema set-returning RPCs also receive improved inference. Supabase JS additionally exports the `DatabaseWithoutInternals` utility type.

## Generated Python database types

CLI 2.66.0 or later can generate Python database types: selected rows become Pydantic `BaseModel` classes, while insert and update payloads become `TypedDict` classes with requiredness derived from the schema.

```sh
npx supabase gen types --lang=python --project-id "$PROJECT_REF" \
  --schema public > database_types.py
npx supabase gen types --lang=python --local > database_types.py
```

## Typed JSON selectors in supabase-js

Since 2.48.0, overriding a generated JSON/JSONB column with a custom type through `MergeDeep` enables nested selector inference. `->` retains the custom JSON type, while `->>` produces text.

```ts
type Payload = { bar: { baz: number }; en: 'ONE' | 'TWO' }
type Database = MergeDeep<DatabaseGenerated, {
  public: { Tables: { events: { Row: { data: Payload | null } } } }
}>

const result = await client
  .from('events')
  .select('data->bar->baz, data->en, data->>en')
```

## Installable Supabase agent skills

Supabase publishes portable agent skills that can be installed all at once or selected by name; the same CLI can search the community directory.

```sh
npx skills add supabase/agent-skills
npx skills add supabase/agent-skills --skill SKILL_NAME
npx skills find QUERY
```

## Hosted MCP scope controls

The hosted MCP endpoint accepts `read_only=true`, `project_ref=<id>`, and comma-separated `features=<groups>` controls. Project scoping removes account-management tools, Storage is the only group disabled by default, and the local stack exposes MCP at `http://localhost:54321/mcp`.

```text
https://mcp.supabase.com/mcp?project_ref=abc123&read_only=true&features=database,docs
```

## Hosted MCP authentication outside browser flows

Hosted MCP normally authenticates through browser OAuth with dynamic client registration. CI can instead send a personal access token as `Authorization: Bearer <token>`; clients that require a fixed client ID and secret need an organization OAuth app, currently with write access to every available scope.

## Hosted MCP trust boundary

The hosted MCP server is intended for development and testing, runs with developer permissions, and must not be exposed to customers. Keep tool-call approval enabled and reduce prompt-injection impact with a development project or branch, project scope, read-only mode, and the smallest necessary feature set.

## Edge Function MCP transport and authentication boundary

The Edge Functions MCP guide currently supports unauthenticated servers only: use `WebStandardStreamableHTTPServerTransport`, disable function-layer JWT verification when serving and deploying, and send `Accept: application/json, text/event-stream`. Function routes are prefixed with the function name, so a differently named Hono function needs the corresponding `basePath`.

```sh
supabase functions serve --no-verify-jwt mcp
supabase functions deploy --no-verify-jwt mcp
```

## Hono project bootstrap

The CLI can bootstrap a Hono starter already configured with `@supabase/supabase-js` and `@supabase/ssr`; the sample also requires anonymous sign-ins to be enabled.

```sh
npx supabase@latest bootstrap hono
```

## Static AI SDK tool schemas

`@supabase/mcp-server-supabase` exports `createToolSchemas()` so its MCP tools can be used as statically typed AI SDK tools with client-side input and output validation. Match its `features`, `projectScoped`, and `readOnly` options to the server URL; the server does not send `structuredContent`, so the AI SDK falls back to parsing JSON from text content.

```ts
import { createMCPClient } from '@ai-sdk/mcp'
import { createToolSchemas } from '@supabase/mcp-server-supabase'

const client = await createMCPClient({
  transport: {
    type: 'http',
    url: 'https://mcp.supabase.com/mcp?project_ref=<ref>&read_only=true&features=database,docs',
  },
})
const tools = await client.tools({
  schemas: createToolSchemas({
    features: ['database', 'docs'],
    projectScoped: true,
    readOnly: true,
  }),
})
```

## Mutation workflow guardrails

`apply_migration` records supplied SQL as a database migration and is intended for DDL, while `execute_sql` is for ordinary queries. Read-only mode runs the latter as a read-only Postgres user and removes every other mutating tool; project or branch creation also requires cost confirmation through the account tools.

## Local CLI capability limit

The MCP server bundled with the local Supabase CLI exposes only a limited subset of tools and has no OAuth 2.1 support.

## End-user PostgREST server

`@supabase/mcp-server-postgrest` is a separate MCP server for connecting an application's own users to that application through its REST API.

## Multi-runtime server SDK

`@supabase/server` centralizes Auth, client creation, CORS, and context injection across Edge Functions, Vercel Functions, Deno, Bun, and Cloudflare Workers.
