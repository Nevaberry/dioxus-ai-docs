# MCP Server

## Remote Hosted MCP Server

Supabase provides a hosted MCP server at `https://mcp.supabase.com/mcp` using HTTP transport (not stdio). Configure any MCP client:

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp"
    }
  }
}
```

Authentication uses OAuth 2.1 — the client prompts you to log in via browser during setup.

## URL Query Parameter Configuration

Configure the server via URL query parameters:

- `project_ref=<id>` — scope to a single project (recommended). Disables account-level tools like `list_projects`
- `read_only=true` — restrict to read-only queries. Executes SQL as read-only Postgres user. Disables all mutating tools (`apply_migration`, `create_project`, `deploy_edge_function`, etc.)
- `features=database,docs` — enable only specific tool groups

Example fully configured URL:

```
https://mcp.supabase.com/mcp?project_ref=abcdefghijklmnop&read_only=true&features=database,docs
```

## Feature Groups

Available groups: `account`, `docs`, `database`, `debugging`, `development`, `functions`, `storage`, `branching`.

Default enabled: all except `storage`. Storage is disabled by default to reduce tool count — enable explicitly with `features` parameter.

## Local CLI MCP

When running Supabase locally via CLI, the MCP server is available at `http://localhost:54321/mcp`. Offers a limited subset of tools and no OAuth 2.1.

## AI SDK Integration with createToolSchemas()

The `@supabase/mcp-server-supabase` package exports `createToolSchemas()` for typed tool integration with Vercel AI SDK's MCP client:

```typescript
import { createToolSchemas } from '@supabase/mcp-server-supabase'
import { createMCPClient } from '@ai-sdk/mcp'
import { streamText } from 'ai'

const mcpClient = await createMCPClient({
  transport: { type: 'http', url: 'https://mcp.supabase.com/mcp' },
})

const tools = await mcpClient.tools({
  schemas: createToolSchemas(),
})

const result = streamText({ model, tools, prompt: '...' })
```

Options mirror the URL parameters: `features` (array), `projectScoped` (boolean), `readOnly` (boolean).

```typescript
const tools = await mcpClient.tools({
  schemas: createToolSchemas({
    features: ['database', 'docs'],
    projectScoped: true,
    readOnly: true,
  }),
});
```

## PostgREST MCP Server

Separate package `@supabase/mcp-server-postgrest` allows connecting end users to your app via REST API through MCP. Distinct from the main MCP server which uses developer-level permissions.
