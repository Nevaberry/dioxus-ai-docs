# Client configuration, authentication, retries, and transport

## Regional STS endpoint default

On July 31, 2025, the Python, PHP, C++, and .NET SDKs and AWS Tools for PowerShell changed their default from the global STS endpoint to Regional endpoints. AWS CLI v1 remained the exception among generally available SDKs and CLIs. Audit code that implicitly depended on requests routing through `us-east-1`, including assumptions about latency, failure domains, endpoint allowlists, and audit records.

## 2026 retry behavior

The planned July 2025 switch to `standard` retry mode was postponed. Supporting releases can opt into updated `standard` and `adaptive` behavior now, and the updated behavior becomes the default in November 2026.

```sh
export AWS_NEW_RETRIES_2026=true
```

When the default changes, clients without explicit retry configuration may move from `legacy` to `standard`. The rollout does not change an explicitly selected `legacy` mode, and it preserves explicit maximum-attempt and backoff values.

- Before the default rollout, unset `AWS_NEW_RETRIES_2026` to revert.
- After the rollout, override individual retry settings as needed.
- Where legacy mode remains available, set `AWS_RETRY_MODE=legacy` in Java, Python, Ruby, PHP, C++, or the AWS CLI.

### Retry quota and delays

Updated standard retries use a 500-token quota:

| Retry category | Quota cost | Base delay |
| --- | ---: | ---: |
| Transient errors, including connection failures and HTTP 500/502/503/504 | 14 tokens, increased from 5 | 50 ms |
| Throttling | 5 tokens | 1,000 ms |

The higher transient-error charge makes a client fail faster during a sustained outage. With jitter, the first retry for a brief transient failure is about 25 ms on average.

### DynamoDB and long polling

- DynamoDB and DynamoDB Streams use a 25 ms base delay and four maximum attempts by default under the updated behavior.
- Long-polling calls such as SQS `ReceiveMessage` add a delay before surfacing an error after retry quota exhaustion. This prevents a depleted quota from turning polling loops into CPU- and request-heavy tight loops.

## Authentication-scheme selection

Configure a priority-ordered authentication list with `auth_scheme_preference` in shared AWS config, `AWS_AUTH_SCHEME_PREFERENCE` in the environment, or `aws.authSchemePreference` on the JVM.

```ini
[default]
auth_scheme_preference=sigv4a,sigv4
sigv4a_signing_region_set=us-east-1,us-west-2
```

The recognized values are `sigv4`, `sigv4a`, and `httpBearerAuth`. The client selects the first scheme supported by the service. If none of the requested schemes is available, it falls back to the service's default.

SigV4a takes longer to sign than SigV4 but produces requests valid across Regions. Configure its default Region set with `sigv4a_signing_region_set` or `AWS_SIGV4A_SIGNING_REGION_SET`.

## Tracing and protocol negotiation

- In `2026-07`, JavaScript v3 client core began propagating W3C trace headers. Preserve those headers through custom middleware and proxies when end-to-end trace continuity is required.
- In `2026-07`, Mail Manager added Smithy RPC v2 CBOR alongside AWS JSON 1.0. The SDK automatically prioritizes its most performant supported protocol, so custom endpoint or middleware code must tolerate either supported wire protocol.

## Post-quantum TLS preparation

AWS-LC implements ML-KEM. The stated public HTTPS deployment plan waits for standardized IETF TLS integration, then uses hybrid ECDH plus ML-KEM key agreement.

- Keep clients on TLS 1.3 or later and able to receive updated SDK, CLI, and third-party TLS components.
- ELB, API Gateway, and CloudFront are planned to negotiate the hybrid exchange with existing certificates; this does not require replacing certificates solely for ML-KEM key agreement.
- ML-DSA signing in KMS and post-quantum certificate authentication are separate, later workstreams.
