---
name: zitadel-knowledge-patch
description: Zitadel
license: MIT
version: 4.15.3
metadata:
  author: Nevaberry
---

# Zitadel Knowledge Patch

Use the reference index to load only the material relevant to the task. Start with the breaking changes below when upgrading, generating clients, replacing Login, migrating Actions, or operating a self-hosted installation.

## Reference index

| Reference | Topics |
|---|---|
| [release-changes-by-topic.md](references/release-changes-by-topic.md) | Upgrade hazards, API transitions, security fixes, Login changes, identity providers, telemetry, setup, and maintenance behavior |
| [api-and-protocols.md](references/api-and-protocols.md) | Legacy and resource-based APIs, ConnectRPC, SCIM, OIDC, OAuth, JWT assertions, token claims, logout, SAML, and probes |
| [actions.md](references/actions.md) | Actions V2 targets and executions, payload verification, mutation contracts, V1 migration, and session-concurrency policy |
| [integrations-and-idps.md](references/integrations-and-idps.md) | Organization bootstrap, external identity providers, LDAP, service accounts, System API authentication, and audit events |
| [login-and-management.md](references/login-and-management.md) | Login V2 selection, policies, organizations, projects, notifications, SCIM, Web Keys, custom Login, sessions, MFA, and passkeys |
| [concepts-and-migrations.md](references/concepts-and-migrations.md) | Secret boundaries, password migration, event sourcing, instances, terminology, cross-organization access, and rolling upgrades |
| [application-examples.md](references/application-examples.md) | Iframe embedding, guest users, and restricting Management Console access |
| [sdk-and-clients.md](references/sdk-and-clients.md) | Management clients, Go SDK and OIDC library, Buf generation, and PKCE framework integrations |
| [self-hosting-and-operations.md](references/self-hosting-and-operations.md) | Containers, Compose, configuration, init/setup/start, PostgreSQL, proxies, cache, Helm, telemetry, mirror, blocking, and quotas |

## Breaking changes and deprecations

### Reassess licensing before an upgrade

- Treat the server repository as AGPLv3-licensed.
- Include license obligations in the upgrade review before deploying a newer server.

### Migrate CockroachDB before upgrading

- Do not attempt an in-place upgrade from CockroachDB: current storage is PostgreSQL-only.
- Use the mirror workflow to move the event history and required static data.
- Preserve the source encryption keys, keep the selected mirror scope consistent, rerun setup at the destination, and verify the result.
- Read [concepts-and-migrations.md](references/concepts-and-migrations.md) and [self-hosting-and-operations.md](references/self-hosting-and-operations.md) before planning the migration.

### Prefer resource-based APIs

- Replace deprecated V1 organization, user, project, member, machine-key, PAT, metadata, and instance operations with their resource-based services.
- Expect current services under `v2` or, where documented, `v3`; do not infer stability from a version-looking path.
- Use ConnectRPC or gRPC for new services. Do not expect new OpenAPI 2.0 endpoints.
- Move organization context from `x-zitadel-orgid` into the resource-based request's `organization_id` field.
- Branch on a stable `zitadel.error.v2.ErrorDetail.slug` only for stable relational-backed V2 methods.

### Migrate new automation to Actions V2

- Treat Actions V1 as frozen and scheduled for removal.
- Host V2 handlers as HTTP endpoints, create a target, and bind its ID to request, response, function, or event execution conditions.
- Remember that enabling V2 does not disable V1; prevent duplicate side effects during staged migration.
- Verify HMAC, JWT, or JWE payloads according to the configured target payload type.

### Design custom Login around sessions

- Use Login V2 and the Session API for new custom Login implementations.
- Treat every returned session token as a replacement and persist only the latest token.
- Complete OIDC, SAML, or device requests with an `IAM_LOGIN_CLIENT` credential and the authenticated session.
- Redirect the browser to the returned callback data instead of constructing the protocol callback yourself.
- Keep a passkey Login UI on the relying-party domain used to enroll credentials.

### Deploy the server as containers

- Use the container path for current self-hosting; do not rely on the old direct-Linux installation.
- Use Docker Compose as a development-oriented topology, not as an automatic production recommendation.
- Run `init` once per installation, `setup` for every deployed binary, and `start` only after setup succeeds.
- Route traffic to a new replica only after readiness succeeds.

## API and protocol quick reference

### Keep legacy scopes distinct

| Legacy service | Effective scope | REST prefix | gRPC prefix |
|---|---|---|---|
| Auth | Access-token subject | `/auth/v1/` | `/zitadel.auth.v1.AuthService/` |
| Management | `x-zitadel-orgid`, otherwise subject organization | `/management/v1/` | `/zitadel.management.v1.ManagementService/` |
| Admin | One virtual instance | `/admin/v1/` | `/zitadel.admin.v1.AdminService/` |
| System | Multiple self-hosted instances | `/system/v1/` | `/zitadel.system.v1.SystemService/` |

### Discover OIDC endpoints

- Load `/.well-known/openid-configuration`; paths intentionally span `/oauth/v2/` and `/oidc/v1/`.
- Use authorization code with PKCE for browser applications.
- Do not implement Resource Owner Password Credentials or the SAML OAuth assertion profile; they are unsupported.
- Enable **User Info inside ID Token** only when the ID token itself must carry profile, email, phone, or address claims alongside an access token.
- Validate logout redirects against the client selected by `id_token_hint` or `client_id`.

### Choose the correct machine authentication

| Caller | Credential flow | Critical identity values |
|---|---|---|
| API application | Basic or `private_key_jwt` | Application `clientId`; application key |
| Service account | Client credentials, PAT, or JWT bearer | Service-account user ID; service-account key |
| Self-hosted System API user | Direct signed JWT | Lowercase configured system-user ID; no OAuth exchange |
| Custom Login backend | PAT or service credential | Membership containing `IAM_LOGIN_CLIENT` |

For JWT profiles, set `iss` and `sub` to the required same identifier, use the exact public origin as `aud`, and send the downloaded key ID as `kid`.

## Login and session quick reference

### Complete an OIDC request

1. Proxy the authorization request and capture its request ID.
2. Read `/v2/oidc/auth_requests/{id}`.
3. Build or update a Session API session until policy requirements are met.
4. Save the latest opaque session token after every response.
5. POST the session ID and latest token to the auth-request resource.
6. Redirect to its returned `callbackUrl`.

Use the equivalent `/v2/saml/saml_requests/{id}` bridge for SAML. For HTTP-POST binding, submit the returned `RelayState` and `SAMLResponse` to the returned ACS URL.

### Apply authentication policy deliberately

- Read Login and password-complexity settings instead of hard-coding enabled methods.
- Distinguish password-check, external-login, MFA-initialization, second-factor, and multifactor lifetimes.
- Treat a zero lockout maximum as disabled, but a zero MFA-initialization lifetime as suppression of the setup prompt.
- Require verified contact data before SMS or email OTP enrollment.
- Use recovery codes as a supported MFA method and activate them when added.

### Rotate Web Keys safely

1. Create the next key without activating it.
2. Wait at least the JWKS cache age plus client refresh time.
3. Activate the next key; activation deactivates the old key.
4. Retain the old public key through token and `id_token_hint` lifetimes.
5. Delete only after those signatures no longer need validation.

## Actions V2 quick reference

### Wire a target

```json
{"name":"enrich create-user","restCall":{"interruptOnError":true},"endpoint":"https://actions.example.com/create-user","timeout":"10s"}
```

Create it at `POST /v2/actions/targets`, retain its target ID and signing key, then bind it:

```json
{"condition":{"request":{"method":"/zitadel.user.v2.UserService/CreateUser"}},"targets":["target-id"]}
```

### Return the right shape

- Decode request and response bodies with protobuf-aware JSON.
- Return only the modified protobuf request or response for a Call, not the surrounding context envelope.
- For a deliberate client error, return HTTP 200 from an interrupting target with `forwardedStatusCode` and `forwardedErrorMessage`.
- Expect only the best matching condition to run: method over service over all, or event over group over all.
- Treat event executions as post-storage reactions, never pre-operation guards.

## Self-hosting quick reference

### Preserve external identity

- Set `ExternalDomain`, `ExternalPort`, and `ExternalSecure` to the exact browser-visible endpoint.
- Preserve the original host through the proxy; rerun setup after changing any external endpoint value.
- Send the core API hop over HTTP/2 or h2c. HTTP/1.1 upstream transport is insufficient.
- Route `/ui/v2/login` to the Login container and other traffic to the core container.

### Preserve the secret and database boundaries

- Supply a master key of exactly 32 bytes; do not store it in the database it decrypts.
- Back up PostgreSQL, especially `eventstore.events`; application containers are stateless.
- Pre-provisioned roles and databases still need the ZITADEL schemas.
- Propagate database credential changes everywhere and manually reassign ownership when changing users.

### Expect eventual consistency

- Treat a successful command as durable even when a list query momentarily returns stale projection data.
- Prefer reads by ID when immediate projection catch-up is needed.
- Inspect projection sequence and failed-event tables before replaying or manipulating event state.
- Never infer contiguous event sequences.

## Security-sensitive defaults

- Validate JWT identity-provider `exp`, `iat`, audience, issuer, and signature claims.
- Bind authorization codes, refresh tokens, and token exchanges to the correct client and permitted scopes.
- Require a verified external email before identity-provider auto-linking.
- Protect outbound Action, identity-provider, and HTTP-provider connections with target restrictions and the protected HTTP client.
- Escape usernames before embedding them in LDAP filters.
- Use exact HTTPS redirects outside Development Mode and understand its glob syntax before enabling it.
- Review [release-changes-by-topic.md](references/release-changes-by-topic.md) for maintenance releases that alter authorization, login, proxy, projection, or token validation behavior.
