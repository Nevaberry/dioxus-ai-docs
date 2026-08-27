---
name: keycloak-knowledge-patch
description: Keycloak
version: "26.7.0"
license: MIT
metadata:
  author: Nevaberry
---


# Keycloak Knowledge Patch

Use this skill for Keycloak implementation, configuration, authentication,
administration, extension, operation, and upgrade work. Establish the exact
server, Operator, adapter, and client-library versions before applying
version-dependent guidance. Prefer the deployment's manifests, configuration,
code, and observed behavior when they differ from general guidance.

## Reference index

| Reference | Topics |
| --- | --- |
| [Admin, Account, and Organization APIs](references/admin-account-and-organizations.md) | Client Admin API, Account REST, SCIM, organizations, permissions, realm search, and corrected API behavior |
| [Identity and Authentication](references/identity-and-authentication.md) | Redirects, origins, consent, logout delivery, browser flows, passkeys, assurance, session limits, X.509, and authorization resources |
| [Protocols, Token Exchange, and Brokering](references/protocols-token-exchange-and-brokering.md) | Standard and legacy exchange, external tokens, OID4VCI, ID-JAG, SSF, AuthZEN, SAML step-up, delegation, DPoP, and parameterized scopes |
| [Server, Operator, and Observability](references/server-operator-and-observability.md) | Quarkus configuration, builds, health, queues, trust, datasources, clustering, caches, proxies, metrics, storage, Kubernetes, and shutdown |
| [Upgrades, Extensions, and Themes](references/upgrades-extensions-and-themes.md) | Major-version migrations, JavaScript, themes, User Profile, representations, SPIs, events, registration, feature changes, and extension lifecycle |

## Working method

1. Identify the exact Keycloak image and Operator versions from deployment
   manifests, build metadata, or startup output.
2. Identify separately versioned consumers such as `keycloak-js`, Java
   extensions, themes, adapters, generated clients, and custom resources.
3. Load the reference matching the task. For an upgrade, load both the
   operational and extension/theme references, plus any protocol reference
   used by the deployment.
4. Treat preview and experimental features as explicit opt-ins. Verify their
   feature flags and profile before depending on endpoints or persisted data.
5. Test authentication, token refresh, logout, proxy, readiness, database, and
   rolling-upgrade behavior at their actual boundaries.
6. Preserve exact option spelling and distinguish build-time options from
   runtime configuration.

## Breaking changes and deprecations

### Preserve sessions during major upgrades

- When carrying online sessions forward, take the required intermediate
  persistence migration path; enabling persistence after the migration point
  cannot safely merge persisted and non-persisted sessions.
- Expect incompatible cache-marshalling changes to clear caches. Verify that
  sessions are database-backed before the cache transition.
- Apply explicit bounds to custom session caches instead of assuming the
  standard cache limits carry over.

### Replace legacy hostname and proxy settings

- Use hostname v2 semantics. Supply a full frontend URL when scheme, port, or
  path matters, and always give the admin hostname as a full URL.
- Replace `proxy` with one trusted `proxy-headers` format plus the required
  hostname and HTTP settings.
- Enable dynamic backchannel resolution only with a full frontend URL.

### Migrate browser integrations and themes

- Import browser code from `keycloak-js` or `keycloak-js/authz`; do not rely on
  deep imports, a server-hosted script, or a UMD/global build.
- Pass configuration explicitly, run in a secure context, and await login and
  URL-construction APIs.
- Move maintained themes to the current parent and shared-resource paths, and
  test custom FreeMarker templates against the newer compatibility level.

### Update authentication and logout entry points

- Use OIDC RP-Initiated Logout instead of legacy `redirect_uri` behavior.
- Use `prompt=create` for registration and the supported
  `/forgot-credentials` authorization-path variant for credential reset.
- Do not deep-link into `/login-actions` or `/broker`.
- Replace the boolean WebAuthn discoverable-credential option with
  `required`, `preferred`, or `discouraged`.

### Update extensions and API representations

- Treat `UserRepresentation.getAttributes()` as custom attributes only; use
  dedicated root properties or server-side `getRawAttributes()` as needed.
- Query identity providers through their dedicated endpoint rather than
  expecting them in ordinary realm representations.
- Do not restart a request transaction. Asynchronous work must own a separate
  session and transaction lifecycle.
- Replace removed token convenience methods and update provider-factory and
  test-builder APIs before recompiling extensions.

### Remove obsolete configuration and dependencies

- Remove obsolete token-exchange and persistent-session batching switches.
- Replace `dynamic-scopes` with `parameterized-scopes`.
- Supply removed drivers and frontend libraries explicitly, and migrate away
  from removed handlers, BOMs, test helpers, admin clients, and brokers.
- Replace deprecated bootstrap administrator variables with
  `KC_BOOTSTRAP_ADMIN_USERNAME` and `KC_BOOTSTRAP_ADMIN_PASSWORD`.

## Security-critical quick reference

### Redirects, origins, and logout

- Match redirect URIs exactly and case-sensitively unless the registered value
  has a trailing wildcard.
- Force exact matching when a wildcard request contains userinfo or `/../`,
  and never use a full `*` pattern in production.
- Treat token-embedded Web Origins as adapter-specific behavior, not portable
  OIDC client metadata.
- Validate `post_logout_redirect_uri`; logout confirmation presents it as a
  continuation instead of automatically redirecting.

### Token exchange

- Use standard token exchange v2 only with confidential, authenticated
  requesters that explicitly enable the capability.
- Treat `audience` as a filter, never as a way to add an audience, and do not
  send the unsupported `resource` parameter.
- Require the original sender and matching DPoP proof or mTLS certificate for
  sender-constrained subject tokens.
- Restrict legacy exchange permission to trusted clients because its external
  JWT path does not validate `aud`.

### Authentication assurance

- Order conditional LoA subflows from lowest to highest.
- Use an essential `claims` request when failure is required; `acr_values` is
  non-essential.
- Protect browser-carried assurance requests with PAR or a request object and
  verify the returned `acr`.
- Place the session limiter after the user is known and avoid checking normal
  SSO-cookie reuse a second time.

### Secrets, trust, and client credentials

- Use `KCRAW_` for literal environment values containing dollar signs, and do
  not define its `KC_` counterpart simultaneously.
- Never place secrets in build options because build values are persisted in
  plaintext.
- Trust the authenticator CA for direct WebAuthn attestation.
- Anchor X.509 client credentials to an exact CA subject DN and move away from
  regex subject matching.
- Allow at least 86 characters in stores receiving newly generated client
  secrets, and verify rotated-secret invalidation behavior.

## High-value features

### Declarative client administration

- Enable Client Admin API v2 for strictly validated OIDC and SAML client
  management over REST, Java, generated JavaScript, CLI, or Operator resources.
- Use its management-interface OpenAPI document as the schema contract.
- Apply `q` filtering to the full representation before `fields` projection.

### Organizations and provisioning

- Separate organization write, read, and query roles, and combine member
  listing with user-view permission.
- Use fine-grained organization resources for per-organization delegation.
- Enable group-role mappings when organization group roles must appear in
  realm, client, and organization token claims.
- Enable `scim-api` for preview user and group provisioning, PATCH, filtering,
  pagination, extensions, and schema discovery.

### Policy, credential, and event protocols

- Enable `authzen` for single or batch authorization-policy evaluations.
- Enable `ssf` for signed CAEP or RISC events delivered through durable push
  or poll streams.
- Enable `identity-assertion-jwt` only for the receiving authorization-server
  role; the complete ID-JAG flow is not implemented.
- Configure OID4VCI refresh separately from credential lifetime, and use the
  dedicated client-attestation feature when required.
- Enable token-exchange delegation only when consent and refresh-time
  reassessment match the intended impersonation policy.

### Operational resilience

- Route traffic with `/health/ready`; startup and liveness may be UP while
  asynchronous initialization remains incomplete.
- Bound queued requests with `http-max-queued-requests` to shed excess work
  with HTTP 503.
- Give provider JARs deterministic modification times before optimized builds.
- Treat the synchronously replicated database and its invalidation outbox as
  central to stateless multi-cluster operation.
- Roll clustered shutdowns one node at a time and account for cache-rebalance
  time.
