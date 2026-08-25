# Protocols, Token Exchange, and Brokering

## Identity Brokering API v2

Identity Brokering API v2 is disabled by default. Authorize external-token
retrieval per confidential client with *Allow retrieve external tokens* and an
identity-provider allow list. Use `POST` and handle OAuth-style JSON responses.
V2 replaces V1's per-user broker roles. *Store token in session* provides
automatic expiry cleanup and faster access but does not persist the token
across sessions. V1 remains enabled by default but is deprecated. (26.7.0)

## OID4VCI configuration and issuance

Experimental OID4VCI configuration is available in the admin UI with HAIP
conformance, per-user credential management, and user-initiated issuance from
the account console. Enable `client-auth-abca` for attestation-based client
authentication. The pre-authorized code grant is named
`oid4vc-vci-preauth-code`. Configure `vc.refresh_interval_in_seconds`
separately from credential lifetime; its default is the smaller of seven days
or the credential lifetime. (26.7.0)

## Identity Assertion JWT Grant receiver

Enable experimental `identity-assertion-jwt` when Keycloak acts as the
receiving authorization server. It accepts a signed identity assertion at the
token endpoint and issues an access token without another login. Other ID-JAG
roles are not implemented, so Keycloak cannot provide the complete flow.
(26.7.0)

## Shared Signals Framework transmitter

Enable experimental `ssf` to transmit signed Security Event Tokens using CAEP
1.0 or RISC 1.0 over push or poll delivery. Manage streams, subjects, and event
types through the admin console or REST API. A durable outbox and cluster-aware
retry processing keep event delivery alive across restarts. (26.7.0)

## AuthZEN evaluation API

Enable experimental `authzen` to expose an AuthZEN Policy Decision Point. It
evaluates subject, resource, and action against configured authorization
policies; both single and batch endpoints return permit-or-deny decisions.
(26.7.0)

## Token exchange delegation

Enable experimental `token-exchange-delegation` for a `delegation`
parameterized scope. Keycloak verifies that the requester may act for the
target user before exchange. Delegation requires consent and is reassessed on
refresh so revoked impersonation rights take effect immediately. (26.7.0)

## Standard token exchange v2 boundary

`token-exchange-standard:v2` is enabled by default, but each requester must be
confidential, enable *Standard token exchange*, and authenticate at the token
endpoint. Public requesters are unsupported. V2 exchanges only a same-realm
Keycloak access token for an access token, ID token, or conditionally a refresh
token. It does not support RFC 8693 `resource`.

```bash
curl -u requester-client:secret https://keycloak.example/realms/test/protocol/openid-connect/token \
  -d grant_type=urn:ietf:params:oauth:grant-type:token-exchange \
  -d subject_token="$SUBJECT_TOKEN" \
  -d subject_token_type=urn:ietf:params:oauth:token-type:access_token \
  -d requested_token_type=urn:ietf:params:oauth:token-type:access_token
```

## Scope and audience filtering

`scope` adds the requester's optional scopes to its defaults. Repeated
`audience` values only filter already resolved audiences, client roles, and
role-bearing client scopes; they never add an audience. Reject an unavailable
audience. The subject token must include the requester in `aud` unless issued
to that same client. Apply `downscope-assertion-grant-enforcer` when requested
scopes must also be limited to those granted to the subject token.

## Sender-constrained subject tokens

A DPoP- or mTLS-bound subject token can be exchanged only by the client to
which it was issued. Require a valid DPoP proof or the matching client
certificate on the exchange request.

## Refresh tokens, sessions, and revocation

Requesting
`requested_token_type=urn:ietf:params:oauth:token-type:refresh_token` returns
both access and refresh tokens only when *Allow refresh token in Standard Token
Exchange* is not `No`. *Same session* rejects transient or offline subject
sessions and `offline_access`; exchange never creates a new user session.

Revoking the original access token does not revoke an exchanged access token.
It does revoke refresh tokens exchanged from it, their requester client
session, and downstream refresh-token exchange chains.

## Legacy exchange isolation and external JWT risk

Legacy V1 is a disabled-by-default, deprecated preview retained for external
token exchange and user impersonation. It needs fine-grained admin permissions
V1 because FGAP V2 has no token-exchange permissions. For JWT subject tokens,
its external-to-internal path validates signature and expiry but not `aud`, so
an ID token issued to another client may be accepted. Grant `token-exchange`
permission only to explicitly trusted clients.

## Typed parameterized scopes

Experimental parameterized scopes validate captured values as `string`,
`integer`, `boolean`, `username`, or `custom`; an administrator-defined regular
expression validates `custom`. A type is required when creating a
parameterized scope while the feature is enabled. (26.7.0)

From 26.7, replace `--features=dynamic-scopes` with
`--features=parameterized-scopes`. Old Java names are deprecated and database
attributes migrate from `is.dynamic.scope` and `dynamic.scope.regexp` to their
`parameterized` equivalents.

## OIDC token-shape compatibility

Keycloak 25 attaches the new default `basic` client scope to existing and new
OIDC clients to supply `sub` and `auth_time`. Migration is skipped in a realm
that already has a scope named `basic`. `session_state` leaves tokens but
remains in the token response. `nonce` becomes ID-token-only and is omitted on
refresh. Attach the supplied *Session State (session_state)* and *Nonce
backwards compatible* mappers when older clients require the earlier shapes.

## Identity-provider representation changes

In 26, ordinary realm representations no longer embed identity providers;
only exports do. API consumers must query the dedicated identity-provider
instances endpoint with filtering and pagination. From 26.7, an identity
provider alias is immutable after creation; Admin REST returns HTTP 400 for an
attempted alias change.

## DPoP flow restrictions

From 26.7, reject implicit and hybrid authorization requests for clients that
require DPoP-bound tokens; those flows expose access tokens through the front
channel.

## Removed and deprecated protocol switches

From 26.7, remove obsolete `token-exchange-external-internal:v2` in favor of
standard token exchange. Remove
`spi-user-sessions--infinispan--use-batches` and
`spi-user-sessions--infinispan--max-batch-size`. The OIDC *Bearer only* switch
and OAuth 1.0a Twitter broker are deprecated. Configure service-only clients
with no grants, and migrate Twitter brokering to a generic OAuth v2 provider.
