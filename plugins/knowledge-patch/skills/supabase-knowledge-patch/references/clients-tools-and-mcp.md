# Clients, developer tools, and MCP

## JavaScript and application clients

### TypeScript response overrides

Query-builder `.returns()` is deprecated; `.overrideTypes<T>()` merges with generated result by default. Second generic `{ merge: false }` replaces fully.

```ts
const merged = supabase.from('users').select()
  .overrideTypes<{ custom_field: string }>()
const replaced = supabase.from('users').select()
  .overrideTypes<{ id: number; name: string }, { merge: false }>()
```

### Expo SQLite-backed Auth persistence

Expo React Native can install `expo-sqlite`'s localStorage polyfill as Auth storage plus URL polyfill. Keep refresh/persistence on and URL-session detection off.

```ts
import 'react-native-url-polyfill/auto'
import 'expo-sqlite/localStorage/install'
import { createClient } from '@supabase/supabase-js'

export const supabase = createClient(url, publishableKey, {
  auth: {
    storage: localStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
})
```

### Next.js Proxy-based Auth refresh

With `@supabase/ssr`, Server Components cannot write refreshed cookies. Root `proxy.ts` calls `supabase.auth.getClaims()` and copies refreshed cookies into both request for Server Components and response to browser. Never authorize server pages from cookie `getSession()` because it is not guaranteed revalidated.

### Supabase UI Library

The official UI library offers ready components built on `shadcn/ui` and integrated with Auth, Storage, and Realtime.

## Developer packages and tools

### Installable Supabase Agent Skills

Install all portable skills or one named skill:

```sh
npx skills add supabase/agent-skills
npx skills add supabase/agent-skills --skill postgres-best-practices
```

### Official MCP server

The official server lets compatible AI tools create projects, fetch project configuration, and query SQL.

## Hosted MCP

### Hosted MCP scope controls

Hosted endpoint query controls: `read_only=true`, `project_ref=<id>`, comma-separated `features=<groups>`. Project scope removes account-management tools. Storage is the only group off by default; groups include Database, Debugging, Development, Functions, Account, Docs, experimental Branching.

```text
https://mcp.supabase.com/mcp?project_ref=abc123&read_only=true&features=database,docs
```

Local stack endpoint is `http://localhost:54321/mcp`.

### Noninteractive hosted MCP authentication

Hosted normally uses browser OAuth with dynamic client registration. CI may send personal access token in `Authorization: Bearer`. If client requires OAuth ID/secret, manually create organization OAuth app; currently it needs write access to all available scopes.

### Hosted MCP safety boundary

Use for development/testing, not production data; it acts with developer permissions and must not be customer-facing. Keep per-tool approvals, project scope, read-only, limited features, and disposable branches to reduce prompt-injection impact.

### Typed tools for the AI SDK MCP client

`@supabase/mcp-server-supabase` exports `createToolSchemas()` for client-side input/output validation and static result types. Filters must match URL: `projectScoped` removes account tools/`project_id`, `readOnly` removes mutation, `features` selects groups.

```ts
import { createMCPClient } from '@ai-sdk/mcp'
import { createToolSchemas } from '@supabase/mcp-server-supabase'

const client = await createMCPClient({
  transport: {
    type: 'http',
    url: 'https://mcp.supabase.com/mcp?project_ref=<project-ref>&read_only=true&features=database,docs',
  },
})
const tools = await client.tools({
  schemas: createToolSchemas({
    features: ['database', 'docs'], projectScoped: true, readOnly: true,
  }),
})
```

Results are not in MCP `structuredContent`; AI SDK parses JSON from textual `content`.

## Embedded and local MCP behavior

### Local CLI server limitations

CLI MCP exposes a limited tool subset and has no OAuth 2.1; hosted-auth/full-inventory configurations do not transfer unchanged.

### Tracked schema changes versus ad hoc SQL

Use `apply_migration` for DDL because it records migration history. `execute_sql` is for ordinary non-schema queries; DDL there escapes migration tracking.

### Cost confirmation gate

Creating project/branch needs `confirm_cost`; first use `get_cost` for amount.

### Compact table discovery

`list_tables` defaults compact and combines `schema.name`; use `verbose` for full metadata.

### SQL-result prompt-injection guard

Server wraps SQL results with a warning against commands embedded in data, but it is not foolproof. Keep approvals and inspect follow-on calls when rows contain untrusted text.
