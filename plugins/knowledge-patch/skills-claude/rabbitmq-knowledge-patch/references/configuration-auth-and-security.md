# Configuration, Authentication, and Security

Use this reference when changing authentication backends, OAuth/OIDC, TLS,
authorization, credentials, or management HTTP protections.

## Configure authentication backends and caches (4.0.6, 4.1.0)

### Separate HTTP API authentication backends

Give the HTTP API its own backend chain with `http_dispatch.auth_backends`;
protocol connections continue to use `auth_backends`:

```ini
auth_backends.1 = ldap
auth_backends.2 = internal
http_dispatch.auth_backends.1 = http
```

### Authentication cache invalidation

Explicitly clear the caching authentication and authorization backend with
`rabbitmqctl clear_auth_backend_cache`.

### Case-insensitive nested LDAP groups

LDAP `in_group_nested` matching is case-insensitive.

### Missing authentication plugins fail startup

From 4.1.4, configuring a backend supplied by a known but disabled plugin
prevents node startup instead of leaving the node running with unusable client
authentication.

### LDAP queries in `rabbitmq.conf`

LDAP queries, including multi-line queries, can be defined in
`rabbitmq.conf`.

## Configure OAuth and OIDC (4.1.0, 4.3.5)

### AMQP 1.0 OAuth token renewal

AMQP 1.0 clients can replace a JWT before expiry without disconnecting. The
broker closes the connection if the replacement is not supplied in time.

### Stream OAuth renewal enforcement

From 4.1.4, failed JWT renewal immediately closes a Stream Protocol
connection. A renewed token is rechecked against the connection's current
virtual host.

### Explicit OAuth provider configuration

Do not rely on former Azure Entra or Auth0 defaults. Configure every required
provider value explicitly.

### OAuth scope aliases and variables

Declare aliases in `rabbitmq.conf`. From 4.1.1, scope patterns can interpolate
supported variables such as `{vhost}` and `{sub}`.

```ini
auth_oauth2.scope_aliases.admin = tag:administrator configure:*/*
auth_oauth2.scope_aliases.developer = tag:management configure:*/* read:*/* write:*/*
```

### Broader OAuth and OIDC compatibility

The OAuth 2 plugin accepts configurable discovery endpoints and complex JWT
shapes used by providers such as Keycloak.

### OAuth discovery behind TLS-terminating proxies

When rewriting the token endpoint found through discovery, the login flow
honors `X-Forwarded-Proto`, `X-Forwarded-Host`, and `X-Forwarded-Port` from a
TLS-terminating proxy.

### User tags on credential refresh

Credential refresh replaces the connection's original user tags with the
refreshed user's current tags.

## Handle certificates and encrypted values (4.1.0, 4.2.0, 4.3.5)

### System CA fallback

When no CA certificate is configured explicitly, a node uses the system CA
list when one is available.

### Explicit encrypted-value marker

From 4.1.4, `default_password` and `ssl_options.password` are encrypted only
when prefixed with `encrypted:`. A colon in an ordinary password is not an
encryption marker.

### Removed `*.cacerts` settings

Remove ineffective `*.cacerts` settings from `rabbitmq.conf`. The supported
`cacertfile` setting is unchanged.

### Encrypted management UI credentials

With `management.credential_encryption_secret`, `POST /api/login` returns an
AES-256-GCM `rmqe.` token that the browser sends as
`Authorization: Bearer rmqe.<token>`. Configure the same secret on every node
and enable this only after the rolling upgrade; older nodes reject the token.

## Enforce authorization and protect identities (4.0.6, 4.2.0, 4.3.0)

### Protected HTTP API reference

Set `management.require_auth_for_api_reference = true` to authenticate access
to the `/api` reference page.

### HTTP API protection for users

Apply the `protected` tag to prevent HTTP API updates and deletion. CLI
operations can still remove the tag or delete and recreate the user.

```shell
rabbitmqctl set_user_tags "a-user" "protected"
```

### AMQP 0-9-1 permission reevaluation

Credential refresh clears the permission cache and immediately revalidates
consumer permissions. Passive queue and exchange declarations require
`configure`, like regular declarations.

### Management actions require `policymaker`

Restarting federation links and deleting Shovels through management require
the `policymaker` user tag.

### HTTP authorization denial reasons

An HTTP backend can return `deny <Reason>` for disclosure to AMQP clients when
explicitly enabled:

```ini
auth_http.authorization_failure_disclosure = true
```

### MQTT authorization-failure behavior

From 4.1.8, `mqtt.disconnect_on_unauthorized` controls whether an authorization
failure closes the connection. The default is `true`; `false` keeps it open
and returns the protocol error.

```ini
mqtt.disconnect_on_unauthorized = false
```

## Harden management HTTP behavior (4.3.5)

### Management HTTP header controls

Use `management.headers.referrer_policy` for `Referrer-Policy`. Setting
`management.http.hide_allow_header = true` hides `Allow` except on required
`405 Method Not Allowed` responses.

### Optional JSON filename enforcement

`management.definitions.require_json_extension = true` rejects definition
uploads without a `.json` extension in both the UI and HTTP API. It defaults
to `false`; content is always validated as JSON.

### Authentication event log category

Authentication events use the `user` category. Successful logins are `info`;
failed attempts are `warning`.
