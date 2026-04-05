# Actions V2 (Targets, Executions, Payloads)

Actions V2 replaces V1's inline JavaScript with HTTP webhook targets. V1 APIs planned for removal in V5.

## Target Types

| Type | API Field | Behavior |
|------|-----------|----------|
| **Webhook** | `restWebhook` | Fire-and-forget — status code checked but response body ignored |
| **Call** | `restCall` | Status code AND response body processed — enables request/response manipulation |
| **Async** | `restAsync` | Neither status code nor response checked — runs in parallel |

All types support `interruptOnError: true` — if target returns status >= 400, execution chain stops.

```json
// Create a webhook target
POST /v2/actions/targets
{
  "name": "my-webhook",
  "restWebhook": { "interruptOnError": true },
  "endpoint": "https://my-api.example.com/hook",
  "timeout": "10s"
}

// Create a call target (for request/response manipulation)
POST /v2/actions/targets
{
  "name": "my-call",
  "restCall": { "interruptOnError": true },
  "endpoint": "https://my-api.example.com/call",
  "timeout": "10s"
}
```

Response returns `{ "id": "...", "signingKey": "..." }`. Save both — the ID for executions, the signing key for HMAC verification.

## Execution Conditions

Four condition types with granularity levels:

**Request/Response conditions** (3 levels, best-match priority):
1. **Method** (most specific): `/zitadel.user.v2.UserService/CreateUser`
2. **Service**: `zitadel.user.v2.UserService`
3. **All**: catches everything

```json
PUT /v2/actions/executions
{
  "condition": {
    "request": { "method": "/zitadel.user.v2.UserService/CreateUser" }
  },
  "targets": ["<targetID>"]
}
```

**Function conditions** — trigger during OIDC/SAML flows:
- `preaccesstoken` — before access token generation
- `preuserinfo` — before userinfo response
- `presamlresponse` — before SAML response

**Event conditions** (3 levels): specific event (`user.human.added`), group, or all.

## Payload Structures

**Request/Response payloads:**
```json
{
  "fullMethod": "/zitadel.user.v2.UserService/CreateUser",
  "instanceID": "...", "orgID": "...", "projectID": "...", "userID": "...",
  "request": { /* full protobuf request as JSON */ },
  "response": { /* only for response conditions */ },
  "headers": { "Content-Type": ["application/grpc"], "Host": ["..."] }
}
```

**Event payloads:**
```json
{
  "aggregateID": "...", "aggregateType": "user",
  "resourceOwner": "...", "instanceID": "...",
  "version": "v2", "sequence": 1,
  "event_type": "user.human.added", "created_at": "...",
  "userID": "...", "event_payload": { /* event-specific JSON */ }
}
```

**Function payloads** (preuserinfo/preaccesstoken): Zitadel sends `function`, `userinfo`, `user`, `user_metadata`, `org`, and `user_grants`. Target must return:
```json
{
  "set_user_metadata": [
    {
      "key": "k",
      "value": "base64value"
    }
  ],
  "append_claims": [
    {
      "key": "custom_claim",
      "value": "any_value"
    }
  ],
  "append_log_claims": [
    "log entry"
  ]
}
```

**PreSAMLResponse** return format uses `append_attribute` instead of `append_claims`:
```json
{
  "set_user_metadata": [
    {
      "key": "k",
      "value": "base64value"
    }
  ],
  "append_attribute": [
    {
      "name": "department",
      "name_format": "urn:oasis:names:tc:SAML:2.0:attrname-format:basic",
      "value": "Engineering"
    }
  ]
}
```

## Request/Response Manipulation (Call Targets)

Call targets (`restCall`) can **modify** the request before Zitadel processes it or the response before it's returned. **Important**: Use `protojson` (not standard JSON marshal) for Go targets, since payloads are protobuf messages.

## Payload Signing and Encryption

Three payload types via `payloadType` on target creation:

| Type | Header/Format | Verification |
|------|---------------|-------------|
| `PAYLOAD_TYPE_JSON` (default) | JSON body + `ZITADEL-Signature` HMAC header | Verify HMAC using `signingKey` from target creation |
| `PAYLOAD_TYPE_JWT` | Signed JWT body | Verify via instance's webkeys JWKS endpoint |
| `PAYLOAD_TYPE_JWE` | Encrypted JWE body | Decrypt with your private key, verify inner JWT via webkeys |

**JWE setup** — upload RSA public key to target:
```bash
# Upload public key
POST /v2/actions/targets/<targetID>/publickeys
{ "publicKey": "<base64 encoded PEM>" }

# Activate the key
PUT /v2/actions/targets/<targetID>/publickeys/<keyID>/activate
```

## Error Forwarding

Targets can return structured errors forwarded to the API caller. Return status 200 with:
```json
{
  "forwardedStatusCode": 403,
  "forwardedErrorMessage": "Access denied by custom policy"
}
```
Only status codes 400–499 are forwarded. Other values → PreconditionFailed error. Requires `interruptOnError: true`.

## Feature Flag Behavior

To **manage** Actions V2 resources, the "Actions" feature flag must be activated via `FeatureService.SetInstanceFeatures`. However, **executions always run** even if the flag is off. The only way to stop an execution is to delete it.
