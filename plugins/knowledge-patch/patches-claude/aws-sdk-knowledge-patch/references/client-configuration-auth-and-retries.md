# Client configuration, authentication, retries, and transport

## Endpoints and retry defaults (`shared-defaults-and-runtime-support`)

### Regional STS endpoint defaults

Since July 31, 2025, Python, PHP, C++, and .NET SDKs and AWS Tools for
PowerShell default to Regional STS endpoints. Other generally available SDKs
and CLIs already used Regional endpoints; AWS CLI v1 remains the exception.
An SDK upgrade can therefore change endpoint routing away from the global
endpoint that maps to `us-east-1`.

### 2026 retry-default rollout

The postponed change to `standard` and `adaptive` retry modes is available as
an opt-in and becomes the default in November 2026. Java, Python, Ruby, PHP,
C++, and AWS CLI configurations that implicitly use `legacy` also move to
`standard`.

```sh
export AWS_NEW_RETRIES_2026=true
```

Explicit `legacy`, maximum-attempt, and backoff settings remain unchanged.
After rollout, the flag is ignored; use individual overrides or, where
supported, `AWS_RETRY_MODE=legacy`.

### Retry quota and error-specific backoff

Updated standard retries use a 500-token quota. Transient-error retries cost
14 tokens and use a 50 ms base delay; throttling retries cost 5 tokens and use
a 1,000 ms base delay. This makes brief transient failures retry faster while
sustained failures consume quota sooner.

### DynamoDB and long-polling retry behavior

DynamoDB and DynamoDB Streams use a 25 ms base delay and four attempts by
default. Long-polling operations such as SQS `ReceiveMessage` delay before
returning an error after quota exhaustion so depleted quotas do not create hot
polling loops.

## Authentication and TLS (`crypto-auth-and-rust-runtime`)

### Authentication-scheme preference

Current SDK lines and CLI v2 can override the service-model authentication
order with `auth_scheme_preference` or `AWS_AUTH_SCHEME_PREFERENCE`; the JVM
property is `aws.authSchemePreference`. Go v1, Java 1.x, JavaScript v2, .NET
v3, and Tools for PowerShell v4 do not support this setting.

Valid entries are `sigv4`, `sigv4a`, and `httpBearerAuth`. When none is
available, the SDK uses the service default. Set the default multi-Region set
for SigV4a with `sigv4a_signing_region_set` or
`AWS_SIGV4A_SIGNING_REGION_SET`.

```ini
[default]
auth_scheme_preference=sigv4a,sigv4
sigv4a_signing_region_set=us-east-1,us-west-2
```

### Post-quantum TLS preparation

Future hybrid ECDH plus ML-KEM negotiation requires TLS 1.3 or later. Move
clients and servers from TLS 1.2 and keep SDK, CLI, and third-party TLS
dependencies updatable. Existing certificates remain valid because planned
ELB, API Gateway, and CloudFront changes affect session-key negotiation rather
than certificate formats.

## Checksums and tracing

### Checksum algorithms (`2026-06`)

- **CRC32C and SHA-1 checksum support.** The SDK checksum implementation set
  includes CRC32C and SHA-1.

### JavaScript tracing (`2026-07`)

- **W3C trace-header propagation.** JavaScript v3 client core propagates W3C
  trace headers.

## Protocol selection

### Mail Manager (`2026-07`)

- **Mail Manager CBOR protocol selection.** Mail Manager supports Smithy RPC
  v2 CBOR and AWS JSON 1.0; the SDK automatically prefers the most performant
  supported protocol.

### CBOR expansion and rollback (`2026-07-2`)

- **Smithy RPC v2 CBOR expansion and rollback.** Application Insights, Kendra
  Ranking, WorkSpaces Instances, AppStream, and Backup Gateway can negotiate
  Smithy RPC v2 CBOR alongside their JSON protocols and prefer the most
  performant supported option. Pricing Calculator and BCM Recommended Actions
  briefly gained CBOR in 3.1094.0 but removed it in 3.1100.0, so current
  clients use their earlier protocols.

## Credential freshness (`2026-07-2`)

- **Login credential token refresh.** `credential-provider-login` always reads
  its token from disk, so authentication observes the current on-disk token.
