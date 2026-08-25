# Authentication and Token Exchange

## Identity Assertion JWT Grant receiver

Since 26.7.0, partial experimental ID-JAG support lets Keycloak act as the receiving authorization server. Enable `identity-assertion-jwt` to accept a signed identity assertion at the token endpoint and issue an access token without another login. Other ID-JAG roles are not implemented, so this does not provide the complete flow.

## AuthZEN evaluation API

Enable experimental `authzen` to expose Keycloak as an AuthZEN Policy Decision Point. Single and batch evaluation endpoints evaluate subject, resource, and action against configured authorization policies and return permit-or-deny decisions.

## Token-exchange delegation

Enable experimental `token-exchange-delegation` to use a `delegation` parameterized scope. It verifies that the requester may act for the target user before token exchange. Delegation requires user consent and is reevaluated during refresh, so revoked impersonation rights take effect immediately.

## SAML step-up authentication

The `step-up-authentication-saml` feature is supported rather than preview. A SAML service provider can request a specific authentication context class to require step-up authentication.

## WebAuthn discoverable credentials

WebAuthn and WebAuthn Passwordless policies accept the specification values `required`, `preferred`, and `discouraged` for *Discoverable credential*. The former boolean *Require Discoverable Credential* setting is deprecated.

## Typed parameterized scopes

With experimental parameterized scopes enabled, captured values may be typed as `string`, `integer`, `boolean`, `username`, or `custom`. A custom value is checked against an administrator-defined regular expression. A parameter type is required when creating a parameterized scope while the feature is active.

## Passkey-aware conditional 2FA

The default Browser flow's conditional 2FA branch combines *Condition - User Configured* with *Condition - credential*. The credential condition skips the branch when passwordless WebAuthn has already authenticated the user.

WebAuthn and recovery-code executions are disabled by default. Change them to *Alternative* when configured users should be able to select them through *Try Another Way*.

## Authentication Method Reference claims

An authentication execution can define a reference value. The *Authentication Method Reference (AMR)* protocol mapper places the reference of every successfully completed execution into the OIDC access-token and ID-token `amr` claim.

## Client-policy flow selection

Client Policies can use `AuthenticationFlowSelectorExecutor` to select a flow dynamically and set its authentication level. Combine it with a condition such as `ACRCondition`, then use an ACR-to-LoA mapping to expose the selected level in the token.

## OIDC level-of-authentication edge behavior

Order *Conditional - Level Of Authentication* subflows from lowest to highest: the first one always runs during a user's initial authentication. *Max Age* `0` makes the level valid only for that authentication. An expired level that was not requested can still reuse SSO, but the result is `acr=0`.

An essential `claims` request must be satisfied or authentication fails. By contrast, `acr_values` is non-essential. Protect requests carried in the browser with PAR or a request object, and verify the returned `acr`.

```json
{"id_token":{"acr":{"essential":true,"values":["gold"]}}}
```

## Registration and credential-reset entry points

Send `prompt=create` on the OIDC authorization request to open registration. The `/registrations` authorization-path variant is deprecated. To begin credential reset, replace `/auth` with `/forgot-credentials` in the authorization path.

Direct links into `/login-actions` or `/broker` are unsupported because they bypass the OIDC or SAML flow.

## Session-limit authenticator placement

Add *User Session Count Limiter* as *Required* after the user is known in Browser, Direct Grant, Reset Credentials, and Post Broker flows. Keep one consistent configuration. It can deny the new session or terminate the oldest; `0` disables the associated realm or client limit.

In a Browser flow, place it inside an alternative real-authentication branch alongside the top-level Cookie execution. This avoids checking ordinary SSO-cookie reuse again. Session limiting is unavailable for CIBA.

## Standard token exchange v2 boundary

`token-exchange-standard:v2` is enabled by default, but each confidential requester must also enable *Standard token exchange* and authenticate at the token endpoint. Public requesters are unsupported.

V2 exchanges only a same-realm Keycloak access token. It can issue an access token, ID token, or, conditionally, a refresh token. It does not support the RFC 8693 `resource` parameter.

```bash
curl -u requester-client:secret https://keycloak.example/realms/test/protocol/openid-connect/token \
  -d grant_type=urn:ietf:params:oauth:grant-type:token-exchange \
  -d subject_token="$SUBJECT_TOKEN" \
  -d subject_token_type=urn:ietf:params:oauth:token-type:access_token \
  -d requested_token_type=urn:ietf:params:oauth:token-type:access_token
```

## Scope and audience filtering in v2

`scope` adds the requester's optional scopes to its defaults. Repeated `audience` parameters only filter already-resolved audiences, client roles, and role-bearing client scopes; they never add an audience. Requesting an unavailable audience rejects the exchange.

The subject token must name the requester in `aud` unless it was issued to that same client. Apply `downscope-assertion-grant-enforcer` when requested scopes must also be restricted to those granted to the subject token.

## Sender-constrained subject tokens

A DPoP- or mTLS-bound subject token can be exchanged only by the client to which the token was originally issued. The exchange request must include a valid DPoP proof or the matching client certificate.

## Refresh tokens, sessions, and revocation

Requesting `requested_token_type=urn:ietf:params:oauth:token-type:refresh_token` returns both access and refresh tokens only when *Allow refresh token in Standard Token Exchange* is not `No`.

Its *Same session* mode rejects transient or offline subject sessions and `offline_access`. An exchange never creates a new user session.

Revoking the original access token does not revoke an exchanged access token. It does revoke refresh tokens exchanged from that token, the requester client session associated with them, and downstream refresh-token exchange chains.

## Legacy exchange isolation and external-token risk

Legacy v1 is a disabled-by-default, deprecated preview retained for external-token exchange and user impersonation. It requires Fine-Grained Admin Permissions v1 because FGAP v2 deliberately has no token-exchange permissions.

For JWT subject tokens, the external-to-internal path validates signature and expiry but not `aud`. An ID token issued to a different client can therefore be accepted. Grant the `token-exchange` permission only to explicitly trusted clients.

## Standards-based logout

Keycloak 26 removes the legacy logout `redirect_uri` behavior and the `legacy-logout-redirect-uri` and `suppress-logout-confirmation-screen` SPI options. Clients must use OIDC RP-Initiated Logout.

## X.509 client-authentication trust anchor

Since 26.7, X.509 client credentials add a required *Certificate Authority subject DN* so a client certificate is anchored to the intended CA. Existing configurations continue to run, but a future major release will reject create, update, or import without the field.

Regex subject matching and the HAProxy `ssl-cert-chain-prefix` option are deprecated. Use an exact subject and `ssl-cert-chain`.

## Parameterized-scope feature rename

In 26.7, replace `--features=dynamic-scopes` with `--features=parameterized-scopes`. The old Java model names are deprecated. Database attributes migrate automatically from `is.dynamic.scope` and `dynamic.scope.regexp` to their `parameterized` equivalents.

## DPoP authorization-flow restriction

Keycloak 26.7 rejects implicit and hybrid authorization requests for clients that require DPoP-bound tokens, because those flows expose access tokens through the front channel.

## Removed and deprecated authentication switches

In 26.7, remove obsolete `token-exchange-external-internal:v2` and use standard token exchange. Also remove `spi-user-sessions--infinispan--use-batches` and `spi-user-sessions--infinispan--max-batch-size`.

The OIDC *Bearer only* switch and OAuth 1.0a Twitter broker are deprecated. Represent a service-only client by enabling no grants, and migrate Twitter brokering to a generic OAuth v2 provider.

## Account-takeover corrections

The 26.7.2 fixes replace the predictable account-linking hash that a malicious OIDC client could exploit and close an unauthenticated bypass in the reset-credentials flow. Deploy the fixes wherever either flow is exposed.
