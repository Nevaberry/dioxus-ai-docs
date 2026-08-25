# Actions

## Migrate from Actions V1

Actions V1 is frozen and planned for removal in version 5; use Actions V2 for new work. Migration replaces embedded goja JavaScript and supplied `ctx`/`api` objects with externally hosted HTTP handlers:

- API pre/post hooks become request/response executions.
- Token and SAML hooks become function executions.
- Reactions to stored changes become event executions.

V2 executions run in addition to V1, so staged migrations must prevent duplicate side effects. Legacy embedded Actions cannot access server files through `require` on hardened releases.

## Configure Actions V2

### Create and wire a target

Create an endpoint with `POST /v2/actions/targets`, retain the returned target ID and signing key, then attach it to a condition with `PUT /v2/actions/executions`.

```json
{"name":"enrich create-user","restCall":{"interruptOnError":true},"endpoint":"https://actions.example.com/create-user","timeout":"10s"}
```

```json
{"condition":{"request":{"method":"/zitadel.user.v2.UserService/CreateUser"}},"targets":["target-id"]}
```

Target URL restrictions can deny unsafe destinations, and outgoing connections use the protected HTTP client on hardened releases.

### Select a target mode and failure behavior

A Webhook handles target status but ignores its response, a Call handles status and response, and Async handles neither and can run in parallel. Targets run in listed order. Any non-2xx response fails the execution and is logged as `PreconditionFailed`; with `interruptOnError: true`, HTTP 400 or higher stops remaining targets.

To pass a chosen client error through ZITADEL, an interrupting target must itself return HTTP 200 with a forwarding body. Only 400–499 are forwarded; other requested codes become `PreconditionFailed`.

```json
{"forwardedStatusCode":403,"forwardedErrorMessage":"Blocked by policy"}
```

### Understand best-match condition selection

Request and response conditions choose a fully qualified gRPC method, a service, or all calls. Function conditions choose a function name. Event conditions choose one event, an event group, or all events. Only the best match runs: `method > service > all` for calls and `event > group > all` for events. Maintained releases correct request/response `all` conditions so they execute.

### Return protobuf messages, not envelopes

A request target receives `fullMethod`, `instanceID`, `orgID`, `projectID`, `userID`, and the complete protobuf request represented as JSON. A response target gets the same context plus the original request and response. Decode with protobuf-aware JSON such as `protojson`; for a Call, return only the modified request or response, not the context envelope.

Request headers are available in executions on current releases. Metadata-setting contexts contain user information, and Actions can set or delete user and organization metadata. Userinfo Actions receive actor information and can append raw values through `appendMetadataRaw`.

## Implement function executions

### Mutate OIDC results

`preuserinfo` and `preaccesstoken` receive userinfo, user and Base64-valued metadata, organization data, and user grants. A Call can return `set_user_metadata`, `append_claims`, and `append_log_claims`. Bare claim keys are namespaced as `urn:zitadel:iam:<key>`, and logs appear under the function-specific action-log claim.

```json
{"set_user_metadata":[{"key":"tier","value":"cHJv"}],"append_claims":[{"key":"tier","value":"pro"}],"append_log_claims":["mapped tier"]}
```

### Mutate SAML results

`presamlresponse` receives userinfo, user, and grant context. A Call may persist Base64-valued metadata or append SAML attributes. The response field is singular `append_attribute`; each entry contains `name`, `name_format`, and `value`.

```json
{"append_attribute":[{"name":"department","name_format":"urn:oasis:names:tc:SAML:2.0:attrname-format:basic","value":"support"}]}
```

## React to events

Event executions run only after a matching event is stored, so they are reactions rather than pre-operation guards. The envelope identifies aggregate and type, resource owner, instance, aggregate version and sequence, event type and creation time, and creator user ID. The execution input includes `event_payload` on corrected releases.

## Verify and decrypt target payloads

`PAYLOAD_TYPE_JSON` is the default. It carries `ZITADEL-Signature`, an HMAC over content and a timestamp; verify it with the generated signing key and an age limit. Patching a target can generate a replacement key.

`PAYLOAD_TYPE_JWT` is signed with the instance key published through Web Keys. `PAYLOAD_TYPE_JWE` encrypts that signed JWT to the target's key: Base64-encode the public-key PEM, post it to `/v2/actions/targets/{targetID}/publickeys`, then activate the returned key at `/v2/actions/targets/{targetID}/publickeys/{keyID}/activate`.

## Remap nonstandard identity-provider claims

A response execution on `/zitadel.user.v2.UserService/RetrieveIdentityProviderIntent` can inspect `idpInformation.rawInformation` and return a modified response that fills `idpInformation.userName` and required `addHumanUser` profile, email, username, and link fields. Use this when upstream claim names leave required auto-creation fields such as `givenName` empty. Actions V2 can also update metadata through this intent retrieval API.

## Enforce concurrent-session limits

Actions V2 can implement a maximum concurrent-session policy per user through Actions-based session management. Treat it as policy automation rather than a built-in static Login setting.

## Maintain legacy V1 Actions during transition

### Map flow and trigger identifiers

```text
external authentication  flow 1: post-authentication 1, pre-creation 2, post-creation 3
complement token         flow 2: pre-userinfo 4, pre-access-token 5
internal authentication  flow 3: post-authentication 1, pre-creation 2, post-creation 3
complement SAMLResponse  flow 4: pre-SAMLResponse 6
```

### Apply legacy token and SAML mutation rules

Pre-userinfo runs before ID-token, userinfo, and introspection claims; pre-access-token runs only before a JWT access token. `api.v1.claims.setClaim()` adds only absent, non-`urn:zitadel:iam` keys, `api.v1.user.setMetadata()` persists metadata, and pre-access-token also exposes `appendLogIntoClaims()`. Before a SAML response, `api.v1.attributes.setCustomAttribute(key, nameFormat, ...values)` adds a non-conflicting attribute.

### Use legacy authentication hooks correctly

External post-authentication exposes the upstream access token, refresh token, ID token and claims, mapped external user, provider data, authentication error, and request context. It can rewrite profile/contact fields or append metadata; pre-creation can also set username and verification flags, while post-creation appends project-role grants.

Internal post-authentication runs after each password, OTP, U2F, or passwordless validation and exposes `ctx.v1.authMethod` and `authError`; its creation hooks offer the same prospective-user mutation and post-creation grant APIs. Organization metadata is available again on corrected V1 releases.

### Account for the nonstandard V1 HTTP module

Embedded Actions import `zitadel/http`. Its `fetch()` is not the standard Fetch API: it accepts only `GET`, `POST`, `PUT`, and `DELETE`, uses JSON `Content-Type` and `Accept` defaults, and treats a supplied header map as a replacement. It returns `status`, a string `body`, `json()`, and `text()`, throwing for an invalid request or invalid JSON decoding.

```js
const http = require("zitadel/http");
const response = http.fetch("https://example.com/hook", {method: "POST", body: {user: "123"}});
```
