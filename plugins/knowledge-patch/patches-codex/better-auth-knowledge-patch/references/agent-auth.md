# Agent Auth Protocol

## Identity and lifecycle

Agent Auth separates a persistent host identity from runtime agents. Each agent owns an Ed25519 keypair and has an immutable delegated or autonomous mode. Only `active` agents authenticate.

Sliding session TTL defaults to 3,600 seconds, maximum lifetime from activation to 86,400 seconds, and absolute lifetime runs from creation until disabled. Reactivation resets the first two clocks and removes escalated grants. Revocation is permanent, and host revocation cascades to its agents.

A delegated host links to at most one user. An active linked host may auto-approve later agents only for default capabilities. Linking a previously unlinked host terminally marks active autonomous agents `claimed`, revokes their grants, attributes history to the user, and transfers resources. Continued execution requires a new delegated agent.

## Discovery, registration, and consent

Publish `/.well-known/agent-configuration` with protocol version, issuer, supported modes and algorithms, approval methods, and endpoint map. A client must stop on an unsupported major version.

Registration sends a Host JWT and agent public key to `POST /agent/register`. Device authorization is the mandatory approval baseline; CIBA and server extensions are discoverable alternatives. Poll `GET /agent/status` at the returned interval unless an optional SSE `notification_url` succeeds.

```http
GET /.well-known/agent-configuration
POST /agent/register
GET /agent/status
```

## JWT profiles

Host-management JWTs use Ed25519 with:

- `typ: host+jwt`;
- a public-key thumbprint in `iss`;
- the discovery issuer in `aud`;
- `iat`, `exp`, and `jti`;
- inline keys or a JWKS URL.

Registration also binds the new agent key.

Execution JWTs use `typ: agent+jwt`, host ID in `iss`, agent ID in `sub`, resolved capability location in `aud`, and an optional capability restriction. Mint a new token of at most 60 seconds for every request. Servers reject repeated `jti` values. Higher-assurance deployments may additionally bind DPoP or mTLS with `cnf`.

## Capabilities, grants, and constraints

Capabilities have stable names and optional input/output JSON Schemas. Per-agent grants independently record approval, expiration, and constraints. Trusted-host defaults may be granted during registration; runtime escalation always requires explicit consent.

Constraints accept exact values and `max`, `min`, `in`, and `not_in`. A server may narrow but never widen requested scope, and unknown operators fail closed. A capability-specific `location` becomes the Agent JWT audience.

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

`@better-auth/agent-auth` supplies discovery, registration, approvals, grant enforcement, JWT validation, and four tables: `agentHost`, `agent`, `agentCapabilityGrant`, and `approvalRequest`. Run a migration after enabling it.

Define capabilities with JSON Schema in `agentAuth()`. Reserve `defaultHostCapabilities` for low-risk automatic grants, and execute already-validated requests in `onExecute`.

```ts
plugins: [agentAuth({
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
    if (capability === "check_balance") {
      return db.getBalance(args.account_id);
    }
    throw new Error(`Unknown capability: ${capability}`);
  },
})]
```

## Synchronous, asynchronous, and streaming execution

A normal `onExecute` value becomes a synchronous data response. `asyncResult(statusUrl, retryAfter)` returns `202 Accepted` with polling. `streamResult(stream)` produces SSE. Every async poll requires a fresh Agent JWT; long streams require duration and revocation checks.

`createFromOpenAPI()` maps operations with an `operationId` into capabilities and a proxy handler. It maps parameters and request bodies to JSON Schema, supports HTTP-method defaults and approval strengths, and recognizes upstream 202, SSE, JSON, and text responses.

```ts
agentAuth({
  ...createFromOpenAPI(spec, {
    baseUrl: "https://api.example.com",
    defaultHostCapabilities: ["GET", "HEAD"],
    approvalStrength: { GET: "session", POST: "webauthn" },
  }),
})
```

## Verification and resource servers

Within auth routes, resolve the verified agent, user, host, and grants through `auth.api.getAgentSession({ headers })`. Outside the auth handler call `verifyAgentRequest(request, auth)`.

```ts
const session = await auth.api.getAgentSession({
  headers: request.headers,
});
const customSession = await verifyAgentRequest(request, auth);
```

Separate resource servers can call protected `POST /agent/introspect`. An unauthenticated resource can advertise discovery through an `AgentAuth` challenge; a missing grant is authorization failure, not necessarily authentication failure.

```http
WWW-Authenticate: AgentAuth discovery="https://auth.example.com/.well-known/agent-configuration"
```

## Approval and proof of presence

`deviceAuthorizationPage` receives `agent_id` and `code`. Approval should require a fresh session, not merely a long-lived cookie; `freshSessionWindow` defaults to 300 seconds.

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

## Multi-instance deployment and policy

Replay and JWKS caches are process-local by default. Use configured secondary storage for both in multi-instance systems or replay protection and key caching remain instance-local.

```ts
agentAuth({
  jtiCacheStorage: "secondary-storage",
  jwksCacheStorage: "secondary-storage",
})
```

Use `resolveCapabilities`, `blockedCapabilities`, `resolveGrantTTL`, per-path `rateLimit`, and lifecycle callbacks for user-specific visibility, non-grantable actions, grant expiration, endpoint limits, and audit integration.

## Embedded client SDK

`@auth/agent` provides `AgentAuthClient` for discovery, key management, registration, approval polling, fresh JWT signing, escalation, rotation, execution, and filterable tool adapters. Default `MemoryStorage` is ephemeral; durable clients must supply storage for host identity, connections, and provider configurations.

```ts
const client = new AgentAuthClient({ storage: durableStorage });

const agent = await client.connectAgent({
  provider: "https://api.example.com",
  capabilities: [
    "read_data",
    {
      name: "transfer_money",
      constraints: { amount: { max: 1000 } },
    },
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

`@auth/agent-cli` provides `auth-agent` commands and a stdio MCP server for discovery, capability, lifecycle, execution, signing, enrollment, and rotation. It stores a shared host identity, agents, and providers under `~/.agent-auth`. Set `AGENT_AUTH_ENCRYPTION_KEY` to encrypt private keys at rest using AES-256-GCM.

```sh
npx @auth/agent-cli discover https://api.example.com
npx @auth/agent-cli connect \
  --provider https://api.example.com \
  --capabilities read_data
npx @auth/agent-cli mcp --url https://api.example.com
```

## Protocol hardening

- Require a trusted directory, user confirmation, or allowlist before direct discovery.
- For client URL fetches, require HTTPS, bound redirects and response sizes, and enforce timeouts.
- For server-side JWKS fetches, resolve DNS and block private, loopback, and link-local addresses.
- Validate server-returned approval, notification, and asynchronous URLs.
- Require `status_url` to use the issuer's origin.
- Sanitize attacker-controlled approval text.
- Use per-server host keys if cross-provider host correlation is unacceptable.

## Error recovery

Clients re-sign and retry `invalid_jwt`, reactivate `agent_expired`, request access after `capability_not_granted`, correct inputs from `constraint_violated.violations`, and honor `Retry-After` for `rate_limited`.

Revoked, rejected, claimed, and absolute-lifetime-expired agents cannot recover; register a new agent. Unknown error codes fall back to their HTTP status semantics.
