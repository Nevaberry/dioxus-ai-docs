# Agent Auth Protocol

## Identity and lifecycle

Agent Auth separates persistent hosts from runtime agents. Each agent has its own Ed25519 key and an immutable delegated/autonomous mode; only `active` agents authenticate. Sliding session TTL defaults to 3,600 seconds, activation lifetime to 86,400 seconds, and absolute lifetime runs from creation until disabled. Reactivation resets the first clocks and drops escalated grants. Revocation is permanent, and host revocation cascades.

A delegated host links to at most one user. An active linked host may auto-approve later agents only for default capabilities. Linking a formerly unlinked host marks active autonomous agents `claimed`, revokes grants, attributes history to the user, and transfers resources; continuing requires a new delegated agent.

## Discovery, registration, and approval

Servers publish `/.well-known/agent-configuration` with protocol version, issuer, modes, algorithms, approval methods, and endpoints. Stop on unsupported major versions.

Register through `POST /agent/register` with a Host JWT and agent public key. Device authorization is the mandatory approval baseline; CIBA and server extensions are discoverable. Poll `GET /agent/status` at the returned interval unless an optional SSE `notification_url` succeeds.

## JWT profiles

Host management uses Ed25519 JWTs with `typ: host+jwt`, a public-key thumbprint in `iss`, discovery issuer in `aud`, `iat`/`exp`/`jti`, and inline keys or JWKS URLs. Registration also binds the new agent key.

Execution uses `typ: agent+jwt`, host ID in `iss`, agent ID in `sub`, capability location in `aud`, and optional capability restriction. Mint a fresh token of at most 60 seconds for every request. Servers reject reused `jti`; stronger deployments may bind DPoP or mTLS through `cnf`.

## Capabilities and grants

Capabilities have stable names and optional input/output JSON Schemas. Grants independently track approval, expiry, and constraints. Trusted-host defaults may be granted during registration; runtime escalation always needs explicit consent.

Constraints accept exact values or `max`, `min`, `in`, and `not_in`. Servers may narrow but never widen. Unknown operators fail closed. A capability-specific `location` becomes JWT audience.

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

`@better-auth/agent-auth` provides discovery, registration, approval, grant enforcement, and JWT verification, plus `agentHost`, `agent`, `agentCapabilityGrant`, and `approvalRequest` tables. Run migrations after enabling it. Define JSON-Schema capabilities in `agentAuth()`, reserve `defaultHostCapabilities` for low-risk automatic grants, and execute only validated capabilities in `onExecute`.

```ts
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
    if (capability === "check_balance") {
      return db.getBalance(args.account_id);
    }
    throw new Error("Unknown capability");
  },
})
```

## Async, streaming, and OpenAPI execution

A plain `onExecute` result is synchronous. `asyncResult(statusUrl, retryAfter)` returns 202 polling; `streamResult(stream)` returns SSE. Every poll needs a fresh Agent JWT, and long streams need duration/revocation checks.

`createFromOpenAPI()` converts operations with `operationId` into capabilities and a proxy handler, maps parameters/bodies to JSON Schema, accepts method defaults and approval strength, and recognizes upstream 202, SSE, JSON, and text.

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

Auth-handler routes resolve agent, user, host, and grants through `auth.api.getAgentSession({ headers })`. Routes outside it use `verifyAgentRequest(request, auth)`. A separate resource can call protected `POST /agent/introspect`. An unauthenticated resource advertises discovery without treating a missing grant as failed authentication:

```http
WWW-Authenticate: AgentAuth discovery="https://auth.example.com/.well-known/agent-configuration"
```

## Approval and proof of presence

`deviceAuthorizationPage` receives `agent_id` and `code`. Require a fresh session; `freshSessionWindow` defaults to 300 seconds. For high-risk capabilities, enable `proofOfPresence`, the passkey plugin, and `approvalStrength: "webauthn"` to prevent silent approval by an agent controlling a browser.

## Multi-instance storage and policy

Replay and JWKS caches default to process memory. Multi-instance deployments should set `jtiCacheStorage` and `jwksCacheStorage` to configured secondary storage. `resolveCapabilities`, `blockedCapabilities`, `resolveGrantTTL`, per-path `rateLimit`, and lifecycle callbacks support visibility, non-grantable actions, expiring grants, endpoint limits, and auditing.

## Embedded SDK

`@auth/agent` `AgentAuthClient` handles discovery, keys, registration, approval polling, fresh JWTs, escalation, rotation, capability execution, and filterable AI-tool adapters. Default `MemoryStorage` is ephemeral; durable clients must implement `Storage` for host identity, connections, and providers.

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
```

## CLI and MCP client

`@auth/agent-cli` supplies `auth-agent` and a stdio MCP server for discovery, capabilities, lifecycle, execution, signing, enrollment, and rotation. It persists shared host identity, agents, and providers under `~/.agent-auth`. Set `AGENT_AUTH_ENCRYPTION_KEY` to encrypt private keys at rest with AES-256-GCM.

```sh
npx @auth/agent-cli discover https://api.example.com
npx @auth/agent-cli connect --provider https://api.example.com --capabilities read_data
npx @auth/agent-cli mcp --url https://api.example.com
```

## Hardening

Require a trusted directory, confirmation, or allowlist for discovery. Client fetches need HTTPS, bounded redirects/body sizes, and timeouts. Servers fetching client JWKS must resolve DNS and reject private, loopback, and link-local addresses.

Validate approval, notification, and async URLs returned by the server; `status_url` must share issuer origin. Sanitize approval text and use per-server host keys if cross-provider correlation is unacceptable.

## Error recovery

Re-sign and retry `invalid_jwt`; reactivate `agent_expired`; request access for `capability_not_granted`; correct inputs from `constraint_violated.violations`; honor `Retry-After` for `rate_limited`. Revoked, rejected, claimed, and absolute-expired agents require new registration. Unknown codes fall back to HTTP status semantics.
