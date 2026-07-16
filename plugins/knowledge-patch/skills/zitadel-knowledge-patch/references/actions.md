# Actions

## Actions V1 retirement and migration boundary

Actions V1 is frozen and planned for removal in ZITADEL V5, so use V2 for new implementations. Migration moves embedded goja JavaScript using supplied `ctx` and `api` objects to externally hosted HTTP handlers: API pre/post hooks become request/response executions, token and SAML hooks become function executions, and reactions to stored changes become event executions.

## Target creation and execution wiring

Create the endpoint definition with `POST /v2/actions/targets`, retain its returned target ID and signing key, then attach the target to a condition with `PUT /v2/actions/executions`.

```json
{"name":"enrich create-user","restCall":{"interruptOnError":true},"endpoint":"https://actions.example.com/create-user","timeout":"10s"}
```

```json
{"condition":{"request":{"method":"/zitadel.user.v2.UserService/CreateUser"}},"targets":["target-id"]}
```

## Target modes and failures

A Webhook handles the target status but ignores its response, a Call handles both status and response, and Async handles neither and can run in parallel; targets run in their listed order. Any non-2xx response fails the execution and is logged as `PreconditionFailed`, while `interruptOnError: true` makes an HTTP status of 400 or higher stop the remaining targets.

## Forwarding a deliberate client error

To pass a chosen 4xx through ZITADEL, a target configured with `interruptOnError: true` must itself return HTTP 200 with the forwarding body; only 400–499 are forwarded, and other requested codes become `PreconditionFailed`.

```json
{"forwardedStatusCode":403,"forwardedErrorMessage":"Blocked by policy"}
```

## Execution conditions and best-match selection

Request and response conditions select a fully qualified gRPC method, a service, or all API calls; function conditions select a function name, while event conditions select one event, an event group, or all events. ZITADEL uses only the best match, with `method > service > all` for calls and `event > group > all` for events.

## Request and response mutation contracts

A request target receives `fullMethod`, `instanceID`, `orgID`, `projectID`, `userID`, and the complete protobuf request represented as JSON; a response target receives the same context plus the original request and response. Decode these messages with protobuf-aware JSON such as `protojson`, and for a Call return only the modified request or response message rather than the surrounding context envelope.

## OIDC function contracts

The `preuserinfo` and `preaccesstoken` functions receive userinfo, the user and Base64-valued metadata, organization data, and user grants. A Call can return `set_user_metadata`, `append_claims`, and `append_log_claims`; a bare claim key is namespaced as `urn:zitadel:iam:<key>`, and logs are emitted under the function-specific action-log claim.

```json
{"set_user_metadata":[{"key":"tier","value":"cHJv"}],"append_claims":[{"key":"tier","value":"pro"}],"append_log_claims":["mapped tier"]}
```

## SAML function contract

The `presamlresponse` function receives userinfo, user, and grant context, and a Call may persist Base64-valued metadata or append SAML attributes. The response field is the singular `append_attribute`, whose entries contain `name`, `name_format`, and `value`.

```json
{"append_attribute":[{"name":"department","name_format":"urn:oasis:names:tc:SAML:2.0:attrname-format:basic","value":"support"}]}
```

## Event execution timing and envelope

Event executions run only after a matching event has been stored, so they are reactive rather than pre-operation hooks. Their envelope identifies the aggregate and type, resource owner, instance, aggregate version and sequence, event type and creation time, and the creator's user ID.

## Target payload verification and encryption

`PAYLOAD_TYPE_JSON` is the default and carries `ZITADEL-Signature`, an HMAC over the content and a timestamp that the target should verify with its generated signing key and an age limit; patching a target can generate a replacement key. `PAYLOAD_TYPE_JWT` is signed with the instance key published through WebKeys, while `PAYLOAD_TYPE_JWE` encrypts that signed JWT to the target's key: Base64-encode the public-key PEM, post it to `/v2/actions/targets/{targetID}/publickeys`, and activate the returned key at `/v2/actions/targets/{targetID}/publickeys/{keyID}/activate`.

## External identity-provider claim remapping

A response execution on `/zitadel.user.v2.UserService/RetrieveIdentityProviderIntent` can inspect `idpInformation.rawInformation` and return a modified response that fills `idpInformation.userName` and required `addHumanUser` profile, email, username, and link fields. Use this when nonstandard upstream claim names leave required auto-creation fields such as `givenName` empty.

## Legacy V1 flow and trigger identifiers

V1 management APIs identify flows and triggers numerically as follows:

```text
external authentication  flow 1: post-authentication 1, pre-creation 2, post-creation 3
complement token         flow 2: pre-userinfo 4, pre-access-token 5
internal authentication  flow 3: post-authentication 1, pre-creation 2, post-creation 3
complement SAMLResponse  flow 4: pre-SAMLResponse 6
```

## Legacy V1 token and SAML mutation APIs

Pre-userinfo runs before ID-token, userinfo, and introspection claims, while pre-access-token runs only before a JWT access token; `api.v1.claims.setClaim()` adds only absent, non-`urn:zitadel:iam` keys, `api.v1.user.setMetadata()` persists metadata, and pre-access-token also has `appendLogIntoClaims()`. Before a SAML response, `api.v1.attributes.setCustomAttribute(key, nameFormat, ...values)` adds a non-conflicting attribute.

## Legacy V1 authentication hooks

External post-authentication exposes the upstream access token, refresh token, ID token and claims, mapped external user, provider data, authentication error, and request context, and can rewrite profile/contact fields or append metadata; pre-creation can also set username and verification flags, while post-creation appends project-role grants. Internal post-authentication runs after each password, OTP, U2F, or passwordless validation and exposes `ctx.v1.authMethod` and `authError`; its creation hooks offer the same prospective-user mutation and post-creation grant APIs.

## Legacy V1 HTTP module

Embedded actions import `zitadel/http`; its `fetch()` is not the standard Fetch API, accepts only `GET`, `POST`, `PUT`, and `DELETE`, uses JSON `Content-Type` and `Accept` defaults, and treats a supplied header map as a replacement. It returns `status`, a string `body`, `json()`, and `text()`, throwing for an invalid request or invalid JSON decoding.

```js
const http = require("zitadel/http");
const response = http.fetch("https://example.com/hook", {method: "POST", body: {user: "123"}});
```

## Concurrent-session limits with Actions V2

Actions V2 can enforce a maximum number of concurrent sessions for each user, enabling a per-user session-concurrency policy through Actions-based session management.
