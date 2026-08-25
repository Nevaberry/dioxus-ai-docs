# Security, Access Control, and TLS

## Attribute-based access control

### Tag native and linked LDAP users (2026.06.0)

ABAC applies to native users and native linked LDAP users as well as externally
authenticated SSO users. Administrators can attach metadata tags to native
DBMS users and reference those tags in ABAC rules for dynamic role assignment.
Grant the specific privilege required to manage those tags:

```text
DBMS USER METADATA MANAGEMENT
```

### Reject unsupported UDF-based PBAC rules (2026.06.0)

A user-defined function can no longer be defined as part of a Property-Based
Access Control privilege. The combination is unsupported and did not enforce
the behavior implied by its definition. Express the policy without a UDF.

## Authentication and OIDC

### Move OIDC clients to PKCE (2026.06.0)

`dbms.security.oidc.<provider>.auth_flow` accepts PKCE and Implicit, with PKCE
as the default. Implicit flow is deprecated and will be removed; migrate
clients and configuration to PKCE.

The settings `dbms.security.oidc.<provider>.auth_params` and
`dbms.security.oidc.<provider>.client_id` are also deprecated. Do not build new
configuration around them.

### Validate time functions when creating auth rules (2026.05.0)

Creating an auth rule with an invalid time function now fails immediately. Do
not expect the error to be deferred until authorization-time evaluation.

## Privilege administration

### Grant server-management procedures precisely

The following procedures now require `SERVER MANAGEMENT`:

- `dbms.cluster.cordonServer()`
- `dbms.cluster.setAutomaticallyEnableFreeServers()`
- `dbms.cluster.uncordonServer()`

Running them under a general admin privilege is deprecated. Grant the specific
privilege to callers that still use the procedures, and note that
`dbms.cluster.uncordonServer()` itself is being replaced by `ENABLE SERVER`.

### Handle impossible revocations as errors (2025.06)

Revoking a privilege that cannot exist now raises an error. Administrative
automation must not treat that request as an idempotent no-op.

## TLS key exchange and cipher suites

### Enable the post-quantum hybrid only with a capable provider (2026.05.0)

TLS backed by OpenSSL provider 3.5 or later can use `X25519MLKEM768`, a hybrid
key exchange combining X25519 with ML-KEM-768. Verify the active provider
version before selecting it.

### Do not assume CBC suites remain enabled

From 2025.10, Neo4j excludes four insecure Java 21 CBC suites from its
defaults:

```text
TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384
TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256
TLS_DHE_RSA_WITH_AES_256_CBC_SHA256
TLS_DHE_RSA_WITH_AES_128_CBC_SHA256
```

They remain available only when explicitly configured. Prefer modern suites
instead of restoring them for general compatibility.

### Prepare for hostname verification on upgrade

`dbms.ssl.policy.*.verify_hostname` now defaults to `true` rather than
`false`. Verify that peer certificates cover the configured and advertised
hostnames. An existing explicit value remains authoritative.

## Private keys

### Replace legacy PKCS #1 RSA keys

Neo4j can still load a key with this header:

```text
-----BEGIN RSA PRIVATE KEY-----
```

That PKCS #1 form is deprecated and will be removed. Replace server keys with
a supported format before removal rather than relying on the compatibility
loader.

## Security-log collection (2026.04.0)

A self-managed Enterprise Edition deployment can send security logs for
display in the Aura console Security Log Analyzer. The deployment must be
registered with Fleet Manager, and log collection is disabled until an
administrator explicitly opts in.

Treat registration and log collection as separate controls; registration
alone does not authorize collection.
