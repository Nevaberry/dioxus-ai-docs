# Agent Auth Protocol

The Agent Auth Protocol (`agentauthprotocol.com`) is a standalone open protocol from Better Auth for AI agent identity.

## Server Plugin (`@better-auth/agent-auth`)

```ts
import { agentAuth } from "@better-auth/agent-auth";

export const auth = betterAuth({
  plugins: [
    agentAuth({
      providerName: "Acme",
      modes: ["delegated", "autonomous"],
      capabilities: [
        { name: "deploy_project", description: "Deploy to production.",
          input: { type: "object", properties: { projectId: { type: "string" } }, required: ["projectId"] } },
        { name: "list_projects", description: "List user projects." },
      ],
      async onExecute({ capability, arguments: args, agentSession }) {
        // agentSession.user, agentSession.agent, agentSession.host
        return { ok: true, projectId: args?.projectId };
      },
    }),
  ],
});
```

Must expose discovery document at `/.well-known/agent-configuration`:

```ts
export async function GET() {
  return NextResponse.json(await auth.api.getAgentConfiguration());
}
```

### OpenAPI Adapter

Turn any OpenAPI spec into agent-auth capabilities:

```ts
import { createFromOpenAPI } from "@better-auth/agent-auth/openapi";
const spec = await fetch("https://api.example.com/openapi.json").then(r => r.json());
export const auth = betterAuth({
  plugins: [agentAuth({ ...createFromOpenAPI(spec, { baseUrl: "https://api.example.com" }) })],
});
```

### Per-Capability Location URLs

Let agents call REST endpoints directly. Resolve agent sessions in custom handlers:

```ts
const agentSession = await auth.api.getAgentSession({ headers: request.headers });
// Or: const agentSession = await verifyAgentRequest(request, auth);
```

### Async & Streaming Execution

```ts
import { asyncResult, streamResult } from "@better-auth/agent-auth";

agentAuth({
  onExecute: async ({ capability, arguments: args }) => {
    if (capability === "generate_report") {
      const job = await startJob(args);
      return asyncResult(`https://api.example.com/jobs/${job.id}/status`, 5); // retryAfter=5s
    }
    if (capability === "stream_analysis") {
      return streamResult(createReadableStream(args)); // SSE stream
    }
    return { balance: 1250 }; // plain sync response
  },
});
```

### Capability Constraints

Constraint operators: exact value (`"field": value`), `max`, `min`, `in` (array), `not_in` (array). Server enforces at execution — returns `403 constraint_violated` with `violations` array.

### Approval Strength & WebAuthn

```ts
agentAuth({
  capabilities: [
    { name: "read_data", approvalStrength: "none" },
    { name: "update_data", approvalStrength: "session" },  // default
    { name: "delete_account", approvalStrength: "webauthn" },
  ],
  proofOfPresence: { enabled: true, rpId: "example.com" },
  freshSessionWindow: 300, // 5 min
});
```

### Resolve Capabilities Per User

```ts
agentAuth({
  resolveCapabilities: ({ capabilities, agentSession }) => {
    return capabilities.filter(cap => {
      if (cap.name === "admin_action") return agentSession?.user?.role === "admin";
      return true;
    });
  },
});
```

### Cache Storage for Multi-Instance

```ts
agentAuth({
  jtiCacheStorage: "secondary-storage",  // Redis
  jwksCacheStorage: "secondary-storage",
});
```

## Protocol Details

### Agent States & Lifetime Clocks

States: `pending` → `active` → `expired`/`revoked`. Also `rejected`, `claimed`.

Three independent clocks:
- **Session TTL**: from last request
- **Max lifetime**: from last activation
- **Absolute lifetime**: from creation, hard limit, cannot reset

On reactivation: capabilities reset to host defaults, session/max clocks reset, absolute clock does NOT reset.

### Host vs Agent

**Host** = persistent identity of the client environment (e.g., a Claude Code installation). **Agent** = runtime actor within that host (e.g., one conversation). Two chats in the same app = two agents, one host.

### Discovery

Servers publish `/.well-known/agent-configuration`:

```json
{
  "version": "1.0-draft",
  "provider_name": "bank",
  "issuer": "https://auth.bank.com",
  "algorithms": [
    "Ed25519"
  ],
  "modes": [
    "delegated",
    "autonomous"
  ],
  "approval_methods": [
    "device_authorization",
    "ciba"
  ],
  "endpoints": {
    "register": "/agent/register",
    "capabilities": "/capability/list",
    "execute": "/capability/execute",
    "status": "/agent/status"
  }
}
```

## Client SDK (`@auth/agent`)

```ts
import { AgentAuthClient } from "@auth/agent";

const client = new AgentAuthClient({
  directoryUrl: "https://directory.example.com",
  storage: myStorage,         // default: MemoryStorage (lost on exit)
  onApprovalRequired: (info) => console.log(`Approve at: ${info.verificationUri}`),
  approvalTimeoutMs: 300000,
});

const config = await client.discoverProvider("https://api.example.com");
const agent = await client.connectAgent({
  provider: "https://api.example.com",
  capabilities: [
    "check_balance",
    { name: "transfer_funds", constraints: { amount: { max: 1000 } } },
  ],
  mode: "delegated",
  name: "finance-bot",
  reason: "User wants to check balance",
});

const result = await client.executeCapability({
  agentId: agent.agentId,
  capability: "check_balance",
  arguments: { account_id: "acc_123" },
});

// Runtime escalation
await client.requestCapability({
  agentId: agent.agentId,
  capabilities: ["transfer_funds"],
  reason: "User asked to transfer money",
});

// Lifecycle
await client.reactivateAgent(agent.agentId);
await client.disconnectAgent(agent.agentId);
await client.rotateAgentKey(agent.agentId);
```

### Custom Storage Interface

```ts
interface Storage {
  getHostIdentity(): Promise<HostIdentity | null>;
  setHostIdentity(host: HostIdentity): Promise<void>;
  deleteHostIdentity(): Promise<void>;
  getAgentConnection(agentId: string): Promise<AgentConnection | null>;
  setAgentConnection(agentId: string, conn: AgentConnection): Promise<void>;
  deleteAgentConnection(agentId: string): Promise<void>;
  listAgentConnections(issuer: string): Promise<AgentConnection[]>;
  getProviderConfig(issuer: string): Promise<ProviderConfig | null>;
  setProviderConfig(issuer: string, config: ProviderConfig): Promise<void>;
  listProviderConfigs(): Promise<ProviderConfig[]>;
}
```

## AI Framework Tool Adapters

```ts
import { getAgentAuthTools, filterTools } from "@auth/agent";
import { toAISDKTools } from "@auth/agent";      // Vercel AI SDK
import { toOpenAITools } from "@auth/agent";      // OpenAI
import { toAnthropicTools } from "@auth/agent";   // Anthropic

const client = new AgentAuthClient();
const tools = getAgentAuthTools(client);

// Vercel AI SDK
const { text } = await generateText({
  model: openai("gpt-4o"),
  tools: await toAISDKTools(tools),
  prompt: "Transfer $50 to Alice",
});

// OpenAI
const { definitions, execute } = toOpenAITools(tools, { strict: true });

// Anthropic
const { definitions, processToolUse } = toAnthropicTools(tools);

// Filter tools exposed to agents
const safe = filterTools(tools, { exclude: ["sign_jwt", "rotate_host_key"] });
const minimal = filterTools(tools, { only: ["execute_capability", "agent_status"] });
```

Available tools: `list_providers`, `search_providers`, `discover_provider`, `list_capabilities`, `describe_capability`, `connect_agent`, `execute_capability`, `request_capability`, `agent_status`, `sign_jwt`, `disconnect_agent`, `reactivate_agent`, `rotate_agent_key`, `rotate_host_key`, `enroll_host`.

## CLI (`@auth/agent-cli`)

```bash
npm install -g @auth/agent-cli

auth-agent discover https://api.example.com
auth-agent connect --provider https://api.example.com \
  --capabilities check_balance transfer_funds \
  --constraints '{"transfer_funds": {"amount": {"max": 500}}}' \
  --mode delegated --name "my-bot"
auth-agent execute agt_abc123 check_balance --args '{"account_id": "acc_456"}'
auth-agent status agt_abc123
auth-agent mcp --url https://api.example.com # Start as MCP server (stdio)
```

Storage in `~/.agent-auth/` (host.json, agents/, providers/). Encrypt keys at rest with `AGENT_AUTH_ENCRYPTION_KEY`.
