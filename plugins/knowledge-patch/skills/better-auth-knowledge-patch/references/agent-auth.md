# Agent Auth Protocol

## Identity and lifecycle

The protocol distinguishes a persistent host identity from each runtime agent. Every agent receives its own Ed25519 keypair and is permanently registered as either `delegated` or `autonomous`; only `active` agents can authenticate.

The sliding session TTL defaults to 3,600 seconds, the maximum lifetime from activation is 86,400 seconds, and the absolute lifetime runs from creation until disabled. Reactivation resets the sliding and activation clocks and drops escalated grants. Revocation is permanent, and revoking a host cascades to its agents.

A delegated host can link to at most one user. An active linked host can auto-approve later agents only for its default capabilities. Linking a formerly unlinked host terminally marks its active autonomous agents as `claimed`, revokes their grants, attributes their history to the user, and transfers their resources. Continuing requires registering a new delegated agent.

## Discovery, registration, and consent

Every server publishes `/.well-known/agent-configuration` with protocol version, issuer, supported modes and algorithms, approval methods, and endpoint map. A client must stop when the server advertises an unsupported major version.

```http
GET /.well-known/agent-configuration
POST /agent/register
GET /agent/status
```

Registration sends a Host JWT and the agent public key to `POST /agent/register`. Device authorization is the mandatory approval baseline. CIBA and server extensions are discoverable alternatives. Poll `GET /agent/status` at the returned interval unless the optional SSE `notification_url` succeeds.

## Host and Agent JWT profiles

Host management JWTs use Ed25519 and must contain:

- Header `typ: host+jwt`.
- A public-key thumbprint in `iss`.
- The discovery issuer in `aud`.
- `iat`, `exp`, and unique `jti` claims.
- An inline public key or JWKS URL. Registration also binds the new agent key.

Execution JWTs use `typ: agent+jwt`, host ID in `iss`, agent ID in `sub`, and the resolved capability location in `aud`, plus an optional capability restriction. Mint a fresh token with a lifetime of at most 60 seconds for every request. Servers reject replayed `jti` values. Higher-assurance deployments can bind DPoP or mTLS through `cnf`.

## Capabilities and grants

Capabilities have stable names and optional input/output JSON Schemas. Per-agent grants separately track approval, expiry, and constraints. Trusted-host defaults may be granted during registration, but runtime escalation always requires explicit consent.

Constraints support exact values and `max`, `min`, `in`, and `not_in`. The server may narrow requested scope but may never widen it; unknown operators fail closed. A capability-specific `location` becomes the Agent JWT audience.

```json
{
  "capability": "transfer_funds",
  "constraints": {
    "to": "acc_456",
    "amount": { "max": 1000 },
    "currency": { "in": ["USD"] }
  }
}
```

## Server plugin

`@better-auth/agent-auth` adds discovery, registration, approvals, grant enforcement, JWT verification, and the `agentHost`, `agent`, `agentCapabilityGrant`, and `approvalRequest` tables. Run database migrations after enabling it.

Define capabilities with JSON Schema, reserve `defaultHostCapabilities` for low-risk automatic grants, and execute validated requests through `onExecute`:

```ts
plugins: [
  agentAuth({
    providerName: "bank",
    capabilities: [{
      name: "check_balance",
      description: "Check an account balance",
      input: {
        type: "object",
        required: ["account_id"],
        properties: { account_id: { type: "string" } },
      },
    }],
    defaultHostCapabilities: ["check_balance"],
    onExecute: async ({ capability, arguments: args }) => {
      if (capability === "check_balance") return db.getBalance(args.account_id);
      throw new Error(`Unknown capability: ${capability}`);
    },
  }),
]
```

## Execution modes and OpenAPI import

A plain `onExecute` return value produces a synchronous data response. `asyncResult(statusUrl, retryAfter)` produces `202 Accepted` polling, and `streamResult(stream)` produces SSE. Every asynchronous poll needs a new Agent JWT. Long streams need explicit duration and revocation checks.

`createFromOpenAPI()` converts operations with an `operationId` into capabilities and a proxy handler. It maps parameters and bodies to JSON Schema, supports method-specific defaults and approval strengths, and recognizes upstream 202, SSE, JSON, and text responses.

```ts
agentAuth({
  ...createFromOpenAPI(spec, {
    baseUrl: "https://api.example.com",
    defaultHostCapabilities: ["GET", "HEAD"],
    approvalStrength: { GET: "session", POST: "webauthn" },
  }),
})
```

## Request verification and resource servers

Auth routes can resolve the verified agent, user, host, and grants with `auth.api.getAgentSession({ headers })`. Routes outside the auth handler use `verifyAgentRequest(request, auth)`.

```ts
const session = await auth.api.getAgentSession({ headers: request.headers });
const customSession = await verifyAgentRequest(request, auth);
```

A separate resource server can call protected `POST /agent/introspect`. An unauthenticated resource should advertise discovery with an `AgentAuth` challenge instead of treating a missing grant as a generic authentication failure:

```http
WWW-Authenticate: AgentAuth discovery="https://auth.example.com/.well-known/agent-configuration"
```

## Approval UI and proof of presence

`deviceAuthorizationPage` receives `agent_id` and `code`. Approval should require a fresh user session rather than a long-lived cookie; `freshSessionWindow` defaults to 300 seconds.

High-risk capabilities can set `approvalStrength: "webauthn"` when `proofOfPresence` and the passkey plugin are enabled. This prevents an agent with browser access from silently approving itself.

```ts
agentAuth({
  deviceAuthorizationPage: "/approve",
  freshSessionWindow: 300,
  proofOfPresence: {
    enabled: true,
    rpId: "example.com",
    origin: "https://example.com",
  },
  capabilities: [{
    name: "delete_account",
    description: "Delete the current account",
    approvalStrength: "webauthn",
  }],
})
```

## Multi-instance state and policy hooks

Replay and JWKS caches are in memory by default. Multi-instance deployments should select configured secondary storage for both, otherwise replay protection and key caching remain instance-local.

```ts
agentAuth({
  jtiCacheStorage: "secondary-storage",
  jwksCacheStorage: "secondary-storage",
})
```

Use `resolveCapabilities`, `blockedCapabilities`, `resolveGrantTTL`, per-path `rateLimit`, and lifecycle callbacks for user-specific capability visibility, non-grantable actions, expiring grants, endpoint limits, and audit integration.

## Embedded SDK

The `@auth/agent` `AgentAuthClient` handles discovery, host and agent keys, registration, approval polling, fresh JWT signing, escalation, rotation, and capability execution. It can expose these operations through filterable AI-tool adapters.

The default `MemoryStorage` is process-local and ephemeral. Durable clients must provide a `Storage` implementation for host identity, connections, and provider configuration.

```ts
const client = new AgentAuthClient({ storage: durableStorage });
const agent = await client.connectAgent({
  provider: "https://api.example.com",
  capabilities: [
    "read_data",
    { name: "transfer_money", constraints: { amount: { max: 1000 } } },
  ],
  mode: "delegated",
});

const result = await client.executeCapability({
  agentId: agent.agentId,
  capability: "read_data",
  arguments: { id: "user-123" },
});
```

## CLI and MCP client

`@auth/agent-cli` provides `auth-agent` commands and a stdio MCP server for discovery, capabilities, lifecycle, execution, signing, enrollment, and rotation. It persists a shared host identity, agents, and providers under `~/.agent-auth`. Set `AGENT_AUTH_ENCRYPTION_KEY` to encrypt private keys at rest with AES-256-GCM.

```sh
npx @auth/agent-cli discover https://api.example.com
npx @auth/agent-cli connect --provider https://api.example.com --capabilities read_data
npx @auth/agent-cli mcp --url https://api.example.com
```

## Hardening

- Accept direct discovery only through a trusted directory, explicit confirmation, or an allowlist.
- For client URL fetches, require HTTPS, bound redirects and response sizes, and set timeouts.
- When fetching client JWKS, resolve DNS and block private, loopback, and link-local addresses.
- Validate server-returned approval, notification, and asynchronous URLs. Require `status_url` to share the issuer's origin.
- Sanitize attacker-controlled approval text.
- Use per-server host keys when cross-provider host correlation is unacceptable.

## Error recovery

Clients should re-sign and retry `invalid_jwt`, reactivate on `agent_expired`, request access after `capability_not_granted`, correct input from `constraint_violated.violations`, and respect `Retry-After` for `rate_limited`.

Revoked, rejected, claimed, or absolute-lifetime-expired agents cannot recover and require new registration. Unknown error codes fall back to their HTTP status semantics.
