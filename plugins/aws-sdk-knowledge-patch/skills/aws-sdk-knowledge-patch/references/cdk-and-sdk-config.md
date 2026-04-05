# CDK and SDK Configuration Changes

## CDK Mixins (GA Mar 2026)

Composable, reusable abstractions for any CDK construct (L1, L2, or custom) via `.with()` syntax:

```typescript
// Apply mixins to L1 constructs for L2-like features
const bucket = new s3.CfnBucket(this, 'Bucket').with(
  AutoDelete(),
  Encryption(),
  Versioning(),
  BlockPublicAccess(),
);

// Combine into custom L2 constructs
// Apply compliance policies across a scope with Mixins.of()
Mixins.of(this).add(/* resource type or path pattern filtering */);
```

## Auth Scheme Preference (SigV4a)

New config setting to prefer SigV4a for cross-region signing (e.g., multi-region access points):

```ini
# ~/.aws/config
[default]
auth_scheme_preference = sigv4a, sigv4
sigv4a_signing_region_set = us-east-1, eu-west-1
```

Environment variables: `AWS_AUTH_SCHEME_PREFERENCE`, `AWS_SIGV4A_SIGNING_REGION_SET`.

## SDK Default Changes (July 2025)

- **STS endpoint**: Python, PHP, C++, .NET, PowerShell SDKs switch default to `regional` (was global)
- **Retry strategy**: Switch to `standard` (token-bucket throttling) delayed — AWS found concerns, will reschedule

## SDK Version Lifecycle

| SDK | Maintenance | End of Support | Migrate To |
|---|---|---|---|
| JS v2 | Sep 2024 | Sep 2025 | JS v3 |
| Go v1 | Jul 2024 | Jul 2025 | Go v2 |
| .NET v3 | Mar 2026 | Jun 2026 | .NET v4 (GA Apr 2025) |

### JS v3 Node.js Support

Follows Node.js release schedule + 8 months. Node.js 18 dropped Jan 2026 (requires 20+). Node.js 20 drops Jan 2027.

### Python (boto3) Support

6-month grace period after PSF EOL. Python 3.9 drops Apr 2026, 3.10 drops Apr 2027.
