# MCP Server

## Hosted MCP Server (HTTP Transport)

Supabase provides an official hosted MCP server at `https://mcp.supabase.com/mcp` using HTTP transport (not stdio). Configure in any MCP client:

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

OAuth 2.1 login is triggered automatically on first use. The server supports URL query parameters for configuration:

- `project_ref=<id>` — scope to a single project (recommended; disables account-level tools like `list_projects`)
- `read_only=true` — execute SQL as read-only Postgres user, disable all mutating tools
- `features=database,docs` — enable only specific tool groups

Example fully configured URL:

```
https://mcp.supabase.com/mcp?project_ref=abcdefghijkl&read_only=true&features=database,docs
```

## Feature Groups

Available groups: `account`, `docs`, `database`, `debugging`, `development`, `functions`, `storage`, `branching`. Default enabled: all except `storage`.

Key tools by group:
- **database**: `list_tables`, `list_extensions`, `list_migrations`, `apply_migration`, `execute_sql`
- **development**: `get_project_url`, `get_publishable_keys`, `generate_typescript_types`
- **functions**: `list_edge_functions`, `get_edge_function`, `deploy_edge_function`
- **branching**: `create_branch`, `list_branches`, `delete_branch`, `merge_branch`, `reset_branch`, `rebase_branch`
- **debugging**: `get_logs` (by service type), `get_advisors`
- **docs**: `search_docs`

## Local CLI MCP Endpoint

When running Supabase locally via CLI, the MCP server is available at `http://localhost:54321/mcp` with a limited tool subset and no OAuth 2.1.

## AI SDK Integration with `createToolSchemas()`

The `@supabase/mcp-server-supabase` package exports `createToolSchemas()` for Vercel AI SDK's MCP client, providing typed input/output schemas:

```typescript
import { createToolSchemas } from '@supabase/mcp-server-supabase';
import { createMCPClient } from '@ai-sdk/mcp';
import { streamText } from 'ai';

const mcpClient = await createMCPClient({
  transport: { type: 'http', url: 'https://mcp.supabase.com/mcp' },
});

const tools = await mcpClient.tools({
  schemas: createToolSchemas(),
});

const result = streamText({ model, tools, prompt: '...' });

// Tool results are fully typed
for (const step of await result.steps) {
  for (const toolResult of step.staticToolResults) {
    if (toolResult.toolName === 'get_project_url') {
      toolResult.input;  // { project_id: string }
      toolResult.output; // { url: string }
    }
  }
}
```

`createToolSchemas()` options mirror the URL params:
- `features`: array of feature groups (e.g. `['database', 'docs']`)
- `projectScoped: true`: omits `project_id` from inputs, excludes account tools
- `readOnly: true`: excludes mutating tools

## PostgREST MCP Server (`@supabase/mcp-server-postgrest`)

Separate MCP server for connecting end users to your app via REST API (distinct from the main developer-facing MCP server).
