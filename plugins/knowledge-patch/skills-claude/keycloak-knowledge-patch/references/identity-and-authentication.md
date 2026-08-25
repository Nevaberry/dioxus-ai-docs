# Identity and Authentication

## Redirect URI safeguards

Match valid redirect URIs exactly and case-sensitively unless the registered
value ends in a wildcard. Even with a trailing wildcard, force exact matching
when the requested URI contains userinfo or a `/../` parent-directory path.
The full `*` pattern accepts every HTTP or HTTPS redirect and is unsafe for
production.

## Adapter-mediated web origins

Keycloak embeds a client's *Web Origins* in its access token so the application
can decide whether to allow CORS requests. Only Keycloak client adapters
implement this convention; it is not portable OIDC client metadata.

## Consent-screen client item

When *Consent required* is off, *Display client on screen* controls whether a
client-specific item is added alongside configured client-scope consents. The
custom client consent text is used only when consent and that client item are
both enabled.

## Logout delivery and confirmation

Use a backchannel logout URL only while front-channel logout is disabled. If
none is set, Keycloak can fall back to the *Admin URL* through its nonstandard
adapter protocol. Only the legacy Keycloak Java OIDC adapters and Elytron
WildFly OIDC adapter support those callbacks. No logout request is sent when
neither URL exists.

With *Logout confirmation* enabled, browser logout ends on a completion page.
If the client supplies a validated `post_logout_redirect_uri`, present it as a
continuation link or button rather than redirecting automatically.

Keycloak 26 removes legacy logout `redirect_uri` behavior together with the
`legacy-logout-redirect-uri` and `suppress-logout-confirmation-screen` SPI
options. Use OIDC RP-Initiated Logout.

## Passkey-aware conditional 2FA

The default Browser flow's conditional 2FA branch combines *Condition - User
Configured* with *Condition - credential*. The credential condition skips the
branch after passwordless WebAuthn already authenticated the user. WebAuthn and
recovery-code executions are disabled by default; set them to *Alternative* so
configured users can choose them through *Try Another Way*.

WebAuthn and WebAuthn Passwordless policies accept `required`, `preferred`, and
`discouraged` for *Discoverable credential*. Replace the deprecated boolean
*Require Discoverable Credential* option. (26.7.0)

## Authentication execution references

Give an execution a reference value when tokens must record the completed
method. The *Authentication Method Reference (AMR)* protocol mapper adds every
successful execution reference to the OIDC access- and ID-token `amr` claim.

## Dynamic flow selection and assurance

Client Policies can use `AuthenticationFlowSelectorExecutor` to select a flow
dynamically and set its authentication level. Combine it with conditions such
as `ACRCondition`, then configure an ACR-to-LoA mapping so the level appears in
the token.

Order *Conditional - Level Of Authentication* subflows from lowest to highest:
the first always runs for a user's initial authentication. *Max Age* `0` makes
a level valid only for that authentication. An expired, unrequested level can
reuse SSO but yields `acr=0`.

An essential OIDC `claims` request must be satisfied or the request fails;
`acr_values` is non-essential. Protect assurance requests carried through the
browser with PAR or a request object, then verify the returned `acr`.

```json
{"id_token":{"acr":{"essential":true,"values":["gold"]}}}
```

SAML service providers can request a particular authentication context class
for step-up authentication. `step-up-authentication-saml` is supported rather
than preview. (26.7.0)

## Registration and credential-reset entry points

Send `prompt=create` on the OIDC authorization request to open registration;
the `/registrations` authorization-path variant is deprecated. Replace `/auth`
with `/forgot-credentials` to start credential reset. Direct links into
`/login-actions` or `/broker` are unsupported because they bypass the OIDC or
SAML flow.

The 24 `send-verify-email` Admin API uses `email-verification.ftl` rather than
`executeActions.ftl` and accepts a `lifespan` override. Use
`execute-actions-email` with `VERIFY_EMAIL` to retain the earlier template flow.
From 26.7, self-registration with Verify Email collects the profile first and
defers password, OTP, or passkey setup until after verification. The deprecated
*Always set password on register form* switch restores the previous order.

## Session-limit authenticator placement

Add *User Session Count Limiter* as *Required* after the user is known in
Browser, Direct Grant, Reset Credentials, and Post Broker flows, using one
consistent configuration. It can deny the new session or terminate the oldest;
`0` disables the corresponding realm or client limit. In a Browser flow, put
it inside an alternative real-authentication branch alongside the top-level
Cookie execution so normal SSO-cookie reuse is not checked again. Session
limiting is unavailable for CIBA.

## X.509 client authentication

X.509 client credentials require a *Certificate Authority subject DN* from
26.7 so the certificate anchors to the intended CA. Older configurations still
run, but a future major release will reject create, update, or import without
the anchor. Replace regex subject comparison with an exact subject and replace
HAProxy `ssl-cert-chain-prefix` with `ssl-cert-chain`.

## Authorization resource URI validation

Authorization Services reject malformed URI templates on create or update
from 26.7. Placeholders must be nonempty and slash-free; wildcards are valid
only as trailing `/*` or a valid suffix such as `/*.html`; unmatched braces are
invalid. Existing malformed URIs remain until updated, so audit every
resource's `uris` before upgrading.

## Account takeover fixes

Use 26.7.2 or a later patched release for account-linking and reset-credentials
flows. The release replaces a predictable account-linking hash exploitable by a
malicious OIDC client and closes a separate unauthenticated reset-credentials
bypass.
