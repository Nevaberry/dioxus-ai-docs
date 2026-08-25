# Client, Theme, and Extension Migrations

## Custom-theme migration boundaries

For Keycloak 24, welcome themes extending the built-in theme must move from PatternFly 3 to PatternFly 5 and put overridden images under common resources. Account Console themes must change `parent=keycloak.v2` to `parent=keycloak.v3`.

In `content.json`, rename `content` to `children` and remove `id`, `icon`, and `componentName`.

For Keycloak 26, shared third-party paths move from `node_modules/...` to `vendor/patternfly-v3`, `vendor/patternfly-v4`, `vendor/patternfly-v5`, and `vendor/rfc4648`. Alpine.js and jQuery are no longer supplied by the common theme; bundle them when a custom theme still depends on them.

## Keycloak JS packaging and asynchronous APIs

At the 24 package-exports boundary, replace deep imports with `keycloak-js` and `keycloak-js/authz`.

In 26 the server no longer serves Keycloak JS, the UMD/global build is removed, and adapter configuration must be supplied explicitly. Run the library in a secure context and await `login()`, `createLoginUrl()`, and `createRegisterUrl()`.

```javascript
import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: "https://sso.example.com",
  realm: "example",
  clientId: "web"
});

await keycloak.login();
```

## Versioned feature selection

From 24, the same feature cannot appear in both the enabled and disabled lists. An unversioned enabled name selects the latest supported implementation; pin `name:vN` when an upgrade must not change that implementation.

The former `account3`, `admin2`, and `login2` names become versioned base features in 26, for example `--features=login:v1`. Disable a versioned feature using its unversioned base name.

## User Profile enablement migration

Keycloak 24 removes `declarative-user-profile` and enables User Profile for every realm. A realm that previously enabled it migrates with unmanaged attributes off. A realm that had it disabled migrates with unmanaged attributes on, preserving permissive behavior.

New default validation constrains core fields, including a three-character minimum username and prohibited-character checks. Existing realms retain their previous `verify-profile` required-action state; new realms enable it.

## User Profile SPI and template changes

The 24 SPI renames `Attributes.getValues()` to `get()` and `getFirstValue()` to `getFirst()`. It moves `isRootAttribute` to `UserProfileUtil` and removes `getReadable(boolean)`.

Move custom declarative-profile theme changes into `login-update-profile.ftl` and `register.ftl`. Move broker-first-login profile customization into `idp-review-user-profile.ftl`.

## OIDC token-shape compatibility

In Keycloak 25, the new default `basic` client scope supplies `sub` and `auth_time` to existing and new OIDC clients. If a realm already has a scope named `basic`, migration is skipped.

`session_state` leaves tokens but remains in the token response. `nonce` becomes ID-token-only and is omitted on refresh. Attach the supplied `Session State (session_state)` and `Nonce backwards compatible` mappers when older clients depend on the previous token shapes.

## User representation attribute boundary

From 24, `UserRepresentation.getAttributes()` contains custom attributes only. Root fields such as username, email, first and last names, and locale remain dedicated properties inherited from `AbstractUserRepresentation`.

Server code that needs a combined map can call `getRawAttributes()`, but that method is not part of the representation payload.

## Removed integrations and artifacts

Keycloak 25 stops bundling the Oracle JDBC driver and removes the legacy LinkedIn OAuth provider. Install a compatible Oracle driver separately and use the remaining LinkedIn OIDC provider.

Keycloak 26 removes the GELF handler, adapter and miscellaneous BOMs, `keycloak-test-helper`, and the JEE admin client. The Jakarta admin client remains available.

## Event-listener migration

Keycloak 24 replaces the temporary-lockout log with the `USER_DISABLED_BY_TEMPORARY_LOCKOUT` success event.

In 26, deleting a realm no longer emits group-removal events; extensions should handle `RealmRemovedEvent`. The new `UPDATE_CREDENTIAL` and `REMOVE_CREDENTIAL` events supersede the credential-specific password and TOTP event types.

## Java extension API removals

In 25, replace token convenience methods `expiration`, `notBefore`, and `issuedAt` with `exp`, `nbf`, and `iat`. Implementations of `EnvironmentDependentProviderFactory` must use `isSupported(Config.Scope)`.

The 26.7 test framework consistently renames `*ConfigBuilder` classes to `*Builder`. Builder methods move toward `attribute`, `realmRoles`, and plural collection setters.

## Email verification and registration flow

The Keycloak 24 `send-verify-email` Admin API switches from `executeActions.ftl` to `email-verification.ftl` and accepts a `lifespan` override. Use `execute-actions-email` with `VERIFY_EMAIL` to retain the older template flow.

Since 26.7, self-registration with Verify Email collects the profile first and postpones password, OTP, or passkey setup until verification completes. The deprecated *Always set password on register form* switch restores the earlier sequence.

## Authorization resource URI validation

Since 26.7, Authorization Services reject malformed URI templates during create or update. Placeholders must be nonempty and slash-free. A wildcard is valid only as a trailing `/*` or a valid suffix such as `/*.html`; unmatched braces are invalid.

Existing malformed values remain stored until updated. Audit each resource's `uris` before upgrading.

## Extension transaction and asynchronous REST boundary

In 26.7, a `KeycloakSession` transaction may be started only once. Nested transactions remain supported, but an extension must not restart the request transaction.

An asynchronous REST endpoint closes its initiating session immediately. Asynchronous work must own its session and transaction lifecycle and cannot assume an active request context.

## Client secrets and generated AES keys

New client secrets generated by 26.7 are always 86 characters. Ensure downstream secret stores accept that length.

New `aes-generated` providers default to 256-bit keys; existing providers do not change. To rotate, add a higher-priority provider containing a 32-byte key and keep it until sessions protected by the old key have expired.

## FreeMarker compatibility level

Keycloak 26.7 raises FreeMarker's configuration defaults from 2.3.0 to 2.3.32. Test custom themes that rely on deprecated directives, undocumented syntax, or Java-internal access through `?api`.
