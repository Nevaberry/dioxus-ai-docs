# Security and authentication

## Authentication backend selection

### Separate HTTP API backend chain (`4.0.6`)

HTTP API access can authenticate through a backend chain independent of the
one used by messaging protocols:

```ini
auth_backends.1 = ldap
auth_backends.2 = internal
http_dispatch.auth_backends.1 = http
```

Beginning in 4.1.4, configuring an authentication or authorization backend
from a known but disabled plugin makes the node refuse to start. This prevents
a node from booting with client authentication that cannot work.

### Cache invalidation and credential refresh

The caching authentication and authorization backend provides an explicit
cache flush:

```shell
rabbitmqctl clear_auth_backend_cache
```

For AMQP 0-9-1, refreshing credentials clears the connection permission cache
and immediately revalidates consumer permissions. Starting in `4.3.5`, refresh
also replaces the connection's original user tags with the current tags of the
refreshed user.

Authentication events use logging category `user`: successes are emitted at
`info`, failures at `warning`.

## OAuth 2 and OpenID Connect

### Provider and discovery configuration (`4.1.0`)

The OAuth 2 plugin no longer supplies defaults for several Azure Entra and
Auth0 values. Configure all provider-required values explicitly.

The plugin supports configurable OpenID discovery endpoints and complex JWT
structures used by providers such as Keycloak. Scope aliases can be defined in
`rabbitmq.conf`:

```ini
auth_oauth2.scope_aliases.admin = tag:administrator configure:*/*
auth_oauth2.scope_aliases.developer = tag:management configure:*/* read:*/* write:*/*
```

Starting in 4.1.1, selected variables such as `{vhost}` and `{sub}` can be
interpolated in scope patterns.

### Token renewal

AMQP 1.0 clients can replace a JWT before expiry without disconnecting. If no
replacement arrives before expiry, RabbitMQ closes the connection. From 4.1.4,
a failed Stream Protocol JWT renewal closes the connection immediately, and a
successful renewal is reauthorized for the current virtual host.

### TLS-terminating proxies

When the login flow rewrites the token endpoint URL returned by OpenID
discovery, it honors `X-Forwarded-Proto`, `X-Forwarded-Host`, and
`X-Forwarded-Port`. Ensure the trusted TLS-terminating proxy supplies correct
values.

## TLS and encrypted values

When no CA certificate is explicitly configured and a system CA list exists,
RabbitMQ falls back to that list. The ineffective `*.cacerts` configuration
keys are removed in `4.2.0`; `cacertfile` remains valid and is not renamed.

Beginning in 4.1.4, values for `default_password` and `ssl_options.password`
are considered encrypted only when they start with `encrypted:`. A colon in an
ordinary or generated password does not imply encryption.

## Management UI credential encryption

When `management.credential_encryption_secret` is configured, `POST /api/login`
returns an AES-256-GCM-encrypted token prefixed `rmqe.`. The browser sends it as
`Authorization: Bearer rmqe.<token>`.

Use the same secret on every node. Enable this only after a rolling upgrade has
completed because older nodes reject these tokens.

## LDAP

The `in_group_nested` LDAP query matches group membership case-insensitively.
In `4.3.0`, LDAP queries, including multi-line queries, can be expressed in
`rabbitmq.conf`.

## HTTP authentication and authorization

Require authentication for the API reference page with:

```ini
management.require_auth_for_api_reference = true
```

An HTTP authorization backend can return `deny <Reason>` and disclose the
custom reason to AMQP clients when explicitly enabled:

```ini
auth_http.authorization_failure_disclosure = true
```

Protect a user from HTTP API mutation or deletion by assigning the `protected`
tag. CLI operations can remove the tag or delete and recreate the user:

```shell
rabbitmqctl set_user_tags "a-user" "protected"
```

Federation-link restarts and Shovel management `DELETE` operations require the
`policymaker` tag.

## Permission semantics

Credential refresh immediately rechecks an AMQP 0-9-1 consumer's permissions.
Passive queue and exchange declarations require `configure`, just like normal
declarations. When designing refreshable OAuth permissions, account for both
the permission recheck and refreshed user tags.
