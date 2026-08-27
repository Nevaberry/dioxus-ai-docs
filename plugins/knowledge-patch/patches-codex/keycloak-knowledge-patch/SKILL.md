---
name: keycloak-knowledge-patch
description: Keycloak
version: "26.7.0"
license: MIT
metadata:
  author: Nevaberry
---


# Keycloak Knowledge Patch

Use this skill when configuring, extending, integrating, administering, or upgrading Keycloak. Start with the breaking-change checks below, then open the topic reference that matches the task.

## Reference index

| Reference | Topics |
| --- | --- |
| [Admin and Account APIs](references/admin-and-account-apis.md) | Client Admin API v2, Account REST permissions and consent, fine-grained administration fixes |
| [Authentication and Token Exchange](references/authentication-and-token-exchange.md) | Authentication flows, LoA and AMR, token exchange, WebAuthn, DPoP, AuthZEN, ID-JAG |
| [Identity, Brokering, and Organizations](references/identity-brokering-and-organizations.md) | Identity providers, organizations, SCIM, OID4VCI, SSF, redirects, logout delivery |
| [Client, Theme, and Extension Migrations](references/migration-clients-themes-and-extensions.md) | Themes, Keycloak JS, User Profile, token shape, SPIs, Java extension compatibility |
| [Deployment and Storage Migrations](references/migration-deployment-and-storage.md) | Persistent sessions, caches, databases, trust, proxying, Operator, clustering |
| [Server Configuration and Operations](references/server-configuration-and-operations.md) | Environment mapping, optimized builds, readiness, queues, metrics, secrets, bootstrap |

## Breaking-change triage

### Preserve sessions before crossing into 26

- Upgrade through 25 and enable preview `persistent-user-sessions` on that first upgrade.
- Only sessions already backed by remote Infinispan or embedded-cache JDBC persistence can migrate.
- Do not enable persistence later and expect persisted and non-persisted sessions to merge safely.
- Expect 26 to clear caches because Protostream is incompatible with the former JBoss Marshalling format.

### Replace removed hostname and proxy configuration

- Treat hostname v2 as the active model: `hostname` accepts a host or full URL, and `hostname-admin` requires a full URL.
- Replace removed hostname-v1 path and port settings.
- Replace `proxy` with exactly one trusted `proxy-headers` format and explicit HTTP/hostname settings.
- Use a full frontend URL with `hostname-backchannel-dynamic=true` for dynamic backchannel resolution.

### Move caches and transactions to runtime-safe settings

- Supply `cache`, `cache-stack`, and `cache-config-file` at runtime; they are no longer build options.
- Account for `transaction-xa-enabled=false` by default.
- With multiple datasources, configure all but at most one as XA.
- Bound custom session-cache definitions consistently with the standard configuration.

### Update themes and browser clients

- Migrate welcome themes from PatternFly 3 to 5 and Account Console themes from `keycloak.v2` to `keycloak.v3`.
- Replace shared `node_modules/...` theme paths with the appropriate `vendor/...` path; bundle Alpine.js or jQuery when needed.
- Import from `keycloak-js` or `keycloak-js/authz`; the server no longer serves the library and the global UMD build is gone.
- Pass adapter configuration explicitly and await `login()`, `createLoginUrl()`, and `createRegisterUrl()`.

### Audit identity and token compatibility

- Use dedicated identity-provider endpoints for normal realm reads; only exports embed identity providers.
- Treat an identity-provider alias as immutable after creation.
- Attach compatibility mappers when clients still require `session_state` in tokens or `nonce` after refresh.
- Use standards-based RP-Initiated Logout; legacy logout `redirect_uri` behavior is removed.
- Update custom code that assumed `UserRepresentation.getAttributes()` included root user fields.

### Rework removed and renamed extension APIs

- Replace token convenience setters `expiration`, `notBefore`, and `issuedAt` with `exp`, `nbf`, and `iat`.
- Pass `Config.Scope` to `EnvironmentDependentProviderFactory.isSupported`.
- Do not restart a request's `KeycloakSession` transaction; a transaction may be started only once.
- Give asynchronous REST work its own session and transaction lifecycle.
- Update event listeners for credential events and realm deletion behavior.

### Plan large-schema migrations

- Inspect startup output for manual index SQL when affected tables exceed 300,000 rows.
- Run the emitted statements after startup; do not assume automatic migration created those indexes.
- Check `USER_ATTRIBUTE`, `FED_USER_ATTRIBUTE`, `RESOURCE_SERVER_PERM_TICKET`, and `IDENTITY_PROVIDER` according to the upgrade path.

## Security-critical checks

### Apply post-release security fixes

- Use the 26.7.2 fixes when account linking or reset-credentials flows are exposed; both received account-takeover corrections.
- Ensure Admin REST does not expose vault-resolved rotated secrets and `show-config` does not reveal the vault keystore password.
- Verify disabling client-secret rotation invalidates the rotated secret.
- Confirm fine-grained permissions protect Role Groups, hidden group parents, and parameterized user-property mappings.

### Harden redirects and browser requests

- Prefer exact, case-sensitive redirect URIs.
- Never use the full `*` redirect pattern in production.
- Know that userinfo and `/../` paths force exact matching even when a trailing wildcard is configured.
- Protect browser-carried LoA requests with PAR or a request object, and verify the returned `acr`.

### Anchor credentials and sender constraints

- Configure the X.509 client's exact Certificate Authority subject DN; regex matching is deprecated.
- Use HAProxy `ssl-cert-chain`, not `ssl-cert-chain-prefix`.
- Exchange DPoP- or mTLS-bound tokens only as the original client with the corresponding proof or certificate.
- Reject implicit and hybrid flows for clients requiring DPoP-bound tokens.

### Protect legacy token exchange

- Prefer standard token exchange v2 for same-realm Keycloak access tokens.
- Keep public clients out of v2; confidential requesters must authenticate and explicitly enable the capability.
- Treat legacy v1 as deprecated and narrowly authorize its `token-exchange` permission.
- Do not rely on legacy external JWT exchange to validate `aud`.

## High-value authentication guidance

### Configure standard token exchange v2

1. Enable *Standard token exchange* on the confidential requester.
2. Authenticate the requester at the token endpoint.
3. Send a same-realm Keycloak access token as `subject_token`.
4. Request an access token, ID token, or permitted refresh token.
5. Use `audience` only to filter already-resolved audiences; it cannot add one.
6. Apply `downscope-assertion-grant-enforcer` when requested scopes must be bounded by the subject token.

V2 does not support RFC 8693 `resource`, never creates a new user session, and requires the requester in the subject token's `aud` unless the token was issued to that requester.

### Build passkey-aware conditional 2FA

- Combine *Condition - User Configured* with *Condition - credential* in the conditional 2FA branch.
- The credential condition skips 2FA after passwordless WebAuthn already authenticated the user.
- Make WebAuthn and recovery codes *Alternative* when configured users should see them under *Try Another Way*.
- Use `required`, `preferred`, or `discouraged` for discoverable credentials; the former boolean option is deprecated.

### Express LoA and AMR correctly

- Order *Conditional - Level Of Authentication* subflows from lowest to highest.
- Remember the first LoA subflow always runs on initial authentication.
- Use an essential `claims` request when the level must be enforced; `acr_values` is only advisory.
- Map successful execution references into `amr` with the AMR protocol mapper.
- Use Client Policies and `AuthenticationFlowSelectorExecutor` when flow and level selection depend on client conditions.

### Place the session limiter safely

- Put *User Session Count Limiter* after the user is known in Browser, Direct Grant, Reset Credentials, and Post Broker flows.
- Reuse one consistent configuration.
- In Browser, put it inside an alternative real-authentication branch alongside the top-level Cookie execution so SSO-cookie reuse is not counted again.
- Choose whether overflow denies the new session or terminates the oldest; `0` disables the relevant limit.
- Do not design around this authenticator for CIBA, where it is unavailable.

## High-value API and identity features

### Use Client Admin API v2 deliberately

- Enable `client-admin-api:v2` for strictly validated declarative OIDC and SAML client management.
- Use REST, Java, generated JavaScript, CLI, or the management-interface OpenAPI document.
- Filter collections with the supported SCIM subset and project fields only after filtering.
- Expect HTTP 400 for malformed expressions, unknown fields, or ordering operators.

### Choose the right identity capability

- Enable `scim-api` for preview user/group CRUD, PATCH, filtering, pagination, Enterprise User extensions, and schema discovery.
- Enable `identity-assertion-jwt` when Keycloak must receive a signed identity assertion and issue an access token without another login.
- Enable `authzen` for single or batch permit/deny policy evaluations.
- Enable `ssf` to transmit signed CAEP or RISC Security Event Tokens over push or poll delivery.
- Enable `stateless` for multi-cluster v2's embedded caches and database-backed invalidation outbox.

### Administer organizations safely

- Assign `manage-organizations`, `view-organizations`, or `query-organizations` for coarse-grained access.
- Require `view-users` or equivalent fine-grained permission before viewing members.
- Use organization-specific fine-grained permissions for scoped access.
- Expect organization group roles in members' `realm_access` and `resource_access` claims.
- Enable *Add group role mappings* to group those roles by organization in the `organization` claim.

## High-value operational guidance

### Preserve exact environment values

- Use `KCRAW_` instead of `KC_` when dollar characters and `${...}` must remain literal.
- Never define both raw and evaluated forms for the same key.
- Pair `KC_<suffix>` with `KCKEY_<suffix>` when normalization cannot represent the exact option key.

### Keep optimized builds reproducible

- Never place secrets in build options; every build option is persisted in plaintext.
- Under `start --optimized`, repeated matching build options are ignored and differing values are rejected.
- Rebuild to change a build option.
- Normalize provider JAR modification times before `kc.sh build` in container images.

### Gate traffic on readiness

- With health enabled, startup and liveness may be UP while initialization continues.
- Route traffic only when `/health/ready` is UP.
- Set `server-async-bootstrap=false` when endpoints must remain closed until initialization finishes.
- Set `http-max-queued-requests` to bound waiting requests; excess requests receive HTTP 503.

## Working method

1. Identify whether the task concerns integration behavior, authentication, an API, an extension, or deployment.
2. Run the relevant breaking-change and security checks above.
3. Open the matching reference file and apply all constraints for that topic.
4. Prefer explicit feature names and exact option keys over assumptions based on older defaults.
5. Test migrations against representative realms, sessions, custom providers, themes, and client token expectations.
