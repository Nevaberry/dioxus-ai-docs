# Upgrades, Extensions, and Themes

## Custom-theme migration boundaries

For Keycloak 24, move welcome themes extending the built-in theme from
PatternFly 3 to 5 and put overridden images under common resources. Change
Account Console themes from `parent=keycloak.v2` to `parent=keycloak.v3`. In
`content.json`, rename `content` to `children` and remove `id`, `icon`, and
`componentName`.

For Keycloak 26, replace shared `node_modules/...` paths with
`vendor/patternfly-v3`, `vendor/patternfly-v4`, `vendor/patternfly-v5`, or
`vendor/rfc4648`. Bundle Alpine.js and jQuery yourself because the common theme
no longer supplies them.

## FreeMarker compatibility

Keycloak 26.7 raises FreeMarker configuration defaults from 2.3.0 to 2.3.32.
Test custom themes that rely on deprecated directives, undocumented syntax, or
Java-internal access through `?api`.

## Keycloak JavaScript packaging and asynchronous APIs

At the 24 package-exports boundary, replace deep imports with `keycloak-js` and
`keycloak-js/authz`. In 26, the server no longer serves Keycloak JavaScript and
the UMD/global build is removed. Pass configuration explicitly, use a secure
context, and await `login()`, `createLoginUrl()`, and `createRegisterUrl()`.

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

From 24, a feature cannot appear in both enabled and disabled lists. An
unversioned enabled name selects the latest supported implementation; pin
`name:vN` when an upgrade must not change it. In 26, former `account3`,
`admin2`, and `login2` names become versioned base features such as
`--features=login:v1`. Disable with the unversioned base name.

## User Profile enablement migration

Keycloak 24 removes `declarative-user-profile` and enables User Profile in all
realms. Realms that had it enabled migrate with unmanaged attributes off;
realms that had it disabled migrate with unmanaged attributes on to preserve
permissive behavior. New default validation includes a three-character minimum
username and prohibited-character checks. Existing realms retain their earlier
`verify-profile` required-action state, while new realms enable it.

## User Profile extension and template changes

For the 24 SPI, rename `Attributes.getValues()` to `get()` and
`getFirstValue()` to `getFirst()`, move `isRootAttribute` to
`UserProfileUtil`, and remove `getReadable(boolean)`. Move declarative-profile
theme changes into `login-update-profile.ftl` and `register.ftl`; put
broker-first-login profile customization in `idp-review-user-profile.ftl`.

## User representation attributes

From 24, `UserRepresentation.getAttributes()` contains custom attributes only.
Username, email, names, and locale remain dedicated properties inherited from
`AbstractUserRepresentation`. Server code can use `getRawAttributes()` for a
combined map, but that method is not part of the representation payload.

## Event-listener migration

Keycloak 24 replaces the temporary-lockout log with the
`USER_DISABLED_BY_TEMPORARY_LOCKOUT` success event. In 26, realm deletion no
longer emits group-removal events, so extensions must handle
`RealmRemovedEvent`. New `UPDATE_CREDENTIAL` and `REMOVE_CREDENTIAL` events
replace credential-specific password and TOTP event types.

## Java extension API removals

In 25, replace token convenience methods `expiration`, `notBefore`, and
`issuedAt` with `exp`, `nbf`, and `iat`. Implementations of
`EnvironmentDependentProviderFactory` must call `isSupported(Config.Scope)`.

The 26.7 test framework consistently renames `*ConfigBuilder` classes to
`*Builder` and moves builder methods toward `attribute`, `realmRoles`, and
plural collection setters. Update extension tests before recompiling.

## Extension transaction and asynchronous REST boundary

From 26.7, a `KeycloakSession` transaction may be started only once, although
nested transactions remain supported. Do not restart a request transaction.
Async REST endpoints close their initiating session immediately, so
asynchronous work must own its session and transaction lifecycle and cannot
assume an active request context.

## Email verification and registration customization

The Keycloak 24 `send-verify-email` Admin API changes from
`executeActions.ftl` to `email-verification.ftl` and accepts a `lifespan`
override. Use `execute-actions-email` with `VERIFY_EMAIL` to keep the older
template flow.

From 26.7, self-registration with Verify Email collects profile details before
verification and defers password, OTP, or passkey setup until afterward. The
deprecated *Always set password on register form* switch restores the prior
sequence while migrating custom flows.
