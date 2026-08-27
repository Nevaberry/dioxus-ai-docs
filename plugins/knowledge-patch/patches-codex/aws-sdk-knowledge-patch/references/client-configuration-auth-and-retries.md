# Client configuration, authentication, and retries

Use this reference when an SDK upgrade changes endpoint selection, retry timing,
authentication, transport, tracing, validation, idempotency, or exception
handling.

## Endpoints and retries

### Regional STS endpoint defaults

Since July 31, 2025, Python, PHP, C++, and .NET SDKs and AWS Tools for
PowerShell default to Regional STS endpoints rather than the global endpoint
that maps to `us-east-1`. Other generally available SDKs and CLIs already used
Regional endpoints; AWS CLI v1 remains the exception. Verify routing and
policies after an SDK upgrade. (`shared-defaults-and-runtime-support`)

### 2026 retry-default rollout

The retry update is opt-in for `standard` and `adaptive` modes and becomes the
default in November 2026. Java, Python, Ruby, PHP, C++, and AWS CLI
configurations that implicitly use `legacy` will also move to `standard`.
Supporting releases can test it with:
(`shared-defaults-and-runtime-support`)

```sh
export AWS_NEW_RETRIES_2026=true
```

Explicit `legacy`, maximum-attempt, and backoff settings are preserved. Before
the rollout, unset the flag to revert. Afterward, the flag is ignored; use
individual overrides or `AWS_RETRY_MODE=legacy` where supported.

### Retry quota and error-specific backoff

Updated standard retries have a 500-token quota. A transient-error retry costs
14 tokens and uses a 50 ms base delay; throttling costs 5 tokens and uses a
1,000 ms base delay. Brief transient failures retry faster, but sustained ones
exhaust quota sooner. (`shared-defaults-and-runtime-support`)

### DynamoDB and long-polling retry behavior

DynamoDB and DynamoDB Streams use a 25 ms base delay and four attempts by
default. Long-poll operations such as SQS `ReceiveMessage` delay before
returning an error after retry-quota exhaustion, preventing a depleted quota
from producing a hot polling loop. (`shared-defaults-and-runtime-support`)

## Authentication and TLS

### Authentication-scheme preference

Current SDK lines and CLI v2 can override service-model authentication ordering
with `auth_scheme_preference` or `AWS_AUTH_SCHEME_PREFERENCE`; on the JVM use
`aws.authSchemePreference`. Go v1, Java 1.x, JavaScript v2, .NET v3, and Tools
for PowerShell v4 do not support this setting. Valid preferences are `sigv4`,
`sigv4a`, and `httpBearerAuth`. If none is usable, the SDK uses its service
default. (`crypto-auth-and-rust-runtime`)

Use `sigv4a_signing_region_set` or `AWS_SIGV4A_SIGNING_REGION_SET` for the
default multi-Region set selected by SigV4a:

```ini
[default]
auth_scheme_preference=sigv4a,sigv4
sigv4a_signing_region_set=us-east-1,us-west-2
```

### Post-quantum TLS preparation

Future post-quantum negotiation requires TLS 1.3 or later. Move clients and
servers off TLS 1.2 and keep SDK, CLI, and third-party TLS dependencies readily
updatable. Planned public HTTPS and managed ELB, API Gateway, and CloudFront
termination uses hybrid ECDH plus ML-KEM. Existing certificates remain usable
because the change concerns session-key negotiation, not certificate format.
(`crypto-auth-and-rust-runtime`)

### IAM-authenticated Sign-In OAuth operations (2026-07)

AWS Sign-In provides `CreateOAuth2TokenWithIAM`,
`IntrospectOAuth2TokenWithIAM`, and `RevokeOAuth2TokenWithIAM` for
client-credentials token issuance, inspection, and revocation.

### Login credential token refresh (2026-07-2)

`credential-provider-login` now reads its token from disk on every use. Expect
authentication to follow the current on-disk token rather than cached state.

### AgentCore private-key JWT authentication (2026-07-2)

AgentCore Identity OAuth 2.0 credential providers can use private-key JWT client
authentication. They sign client assertions with a customer-managed KMS
asymmetric key instead of storing a client secret.

## Protocols, checksums, and tracing

### CRC32C and SHA-1 checksum support (2026-06)

The checksum implementation set includes CRC32C and SHA-1. Generated clients
and middleware may therefore select either algorithm where the service model
allows it.

### W3C trace-header propagation (2026-07)

The JavaScript v3 client core propagates W3C trace headers. Account for this in
header allowlists, tests, proxies, and tracing expectations.

### Mail Manager CBOR protocol selection (2026-07)

Mail Manager supports Smithy RPC v2 CBOR alongside AWS JSON 1.0. The SDK
automatically prioritizes the most performant supported protocol; do not force
JSON unless compatibility requires it.

### Smithy RPC v2 CBOR expansion and rollback (2026-07-2)

Application Insights, Kendra Ranking, WorkSpaces Instances, AppStream, and
Backup Gateway can negotiate Smithy RPC v2 CBOR alongside JSON and prefer the
most performant supported protocol. Pricing Calculator and BCM Recommended
Actions gained CBOR in 3.1094.0 but removed it in 3.1100.0; current clients use
their prior protocol.

## Validation and request semantics

### Outposts phone-number validation (2026-07)

Outposts site requests apply a stricter `ContactPhoneNumber` regular expression.
Previously accepted formats can now fail client-side or service validation.

### Organizations free-text validation (2026-07-2)

Organizations validates free-text values against common cross-site-scripting
patterns. Membership operations may now raise `InvalidInputException` for
values that older clients accepted.

### Roles Anywhere trust-anchor certificate inputs (2026-07-2)

Roles Anywhere accepts longer certificate strings in trust-anchor source data,
allowing use of its adjustable trust-anchor limits. Avoid retaining narrower
client-side constraints.

### Connect email attachment limit (2026-07-2)

Connect Customer emails accept up to 50 attachments instead of 10. Each remains
limited to 20 MB and the complete email to 25 MB, so validate both per-file and
aggregate size.

### Entity Resolution delete-not-found behavior (2026-08)

`DeleteSchemaMapping`, `DeleteMatchingWorkflow`, `DeleteIdMappingWorkflow`, and
`DeleteIdNamespace` now return a 404 `ResourceNotFoundException` for a missing
target instead of 200 success. Idempotent deletion flows must catch and treat
that exception according to intent.

### Stricter DSQL Kinesis ARN validation (2026-08)

DSQL rejects Kinesis stream ARNs containing characters outside the valid ARN
character set. Validate generated and user-supplied ARNs before the request.

### Organizations handshake-party inputs (2026-08)

For `InviteAccountToOrganization`, `HandshakePartyType` accepts only `ACCOUNT`
and `EMAIL` as inputs. `ORGANIZATION` is response-only.

### Longer Amplify OAuth tokens (2026-08)

Amplify `CreateApp` and `UpdateApp` accept longer `oauthToken` values for
third-party Git providers. Do not enforce the previous shorter client limit.

## Idempotency and long-running behavior

### Idempotent ARC plan execution (2026-07-2)

`StartPlanExecution` accepts a client token. Supply a stable token when retrying
an ARC Region Switch plan so retries do not start duplicate executions.

### Auto Scaling multi-instance termination (2026-08)

`TerminateInstanceInAutoScalingGroup` accepts `InstanceIds` and returns an
`Activities` list for batch termination. Also handle
`IdempotentCallInProgressFault` when a duplicate `LaunchInstances` client token
is still being processed.
