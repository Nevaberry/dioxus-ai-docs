# Lifecycle, runtimes, and packaging

Use this reference before upgrading an SDK major line, runtime, CLI, PowerShell
module, bundler target, or client whose public API may have been removed.

## SDK and tool lifecycle

### .NET SDK v3 end of support

The .NET SDK v3 entered maintenance on March 1, 2026 and reached end of support
on June 1, 2026. Existing packages remain available, but they receive no new
updates or releases. Migrate applications to v4. (`sdk-lifecycle-and-eol`)

### .NET SDK v4 package and collection changes

Upgrade all `AWSSDK.*` dependencies together to 4.0.0 or later: v3 and v4 core
and service packages cannot coexist. Request and response collections now
default to `null` instead of empty collections, so add null handling or use the
temporary migration switch below. (`sdk-lifecycle-and-eol`)

```csharp
Amazon.AWSConfigs.InitializeCollections = true;
```

### CLI v1 maintenance announcement

AWS CLI v1 is in the Maintenance Announcement phase, while CLI v2 remains the
generally available line. Target v2 for upgrades and new deployments.
(`sdk-lifecycle-and-eol`)

### Tools for PowerShell v4 end of support

AWS Tools for PowerShell v4 reached end of support on June 1, 2026. Move v4
installations to v5, which has been generally available since June 23, 2025.
(`sdk-lifecycle-and-eol`)

## JavaScript packaging and removed clients

### Removed JavaScript v3 service clients (2026-06)

IoT Events, IoT Events Data, Panorama, and SimSpace Weaver clients were removed.
Code using those clients cannot upgrade unchanged; migrate the integration or
pin the older release deliberately.

### ESM output required for bundlers (2026-06)

Bundler support was removed from `dist-cjs`. Configure bundlers to consume
`dist-es`.

## Runtime support

### Python runtime support cadence

Boto3, Botocore, and AWS CLI v1 support a Python release for six months after
its Python Software Foundation end-of-support date. Python 3.9 support ended in
April 2026, 3.10 ends in April 2027, and 3.11 ends in April 2028. AWS CLI v2 has
no dependency on a local Python runtime. (`shared-defaults-and-runtime-support`)

### JavaScript v3 Node.js and ECMAScript cadence

JavaScript v3 supports current Node.js LTS majors plus the most recently retired
major for about eight months. Dropping a Node.js line also drops the equivalent
ECMAScript browser target. Node.js 18 and pre-ES2023 support ended in January
2026; Node.js 20 and pre-ES2024 support are scheduled to end in January 2027.
Pinning an older SDK may retain runtime compatibility, but not support, service
updates, or fixes. (`shared-defaults-and-runtime-support`)

## Removed, deprecated, and maintenance-bound service APIs

### Cloud9 Amazon Linux 2 API removal (2026-07)

Cloud9's public EC2-environment creation API no longer accepts Amazon Linux 2
as an AMI option. Remove that choice from request generation and user-facing
selectors.

### Inspector scan and API-model changes (2026-07-2)

Inspector2 supports three- and seven-day ECR rescan durations, Windows paths for
deep inspection, Azure SBOM export, and correct tag propagation for connector
CloudFormation stacks. The `Tags` field was removed from
`ListCodeSecurityIntegration` and `ListCodeSecurityScanConfiguration`; callers
must not deserialize or depend on it.

### GameLift managed-fleet expiration (2026-07-2)

A managed GameLift Servers fleet expires one year after creation, enters
`EXPIRED`, emits a `FLEET EXPIRED` event, and scales to zero. It cannot then host
new sessions or scale up, so replacement must be planned before expiration.

### Chime SDK Voice proxy API deprecations (2026-07-2)

The proxy-session operations `CreateProxySession`, `DeleteProxySession`,
`GetProxySession`, `ListProxySessions`, and `UpdateProxySession` are deprecated,
as are `PutVoiceConnectorProxy`, `DeleteVoiceConnectorProxy`, and
`GetVoiceConnectorProxy`. Do not build new flows on them and plan replacements.

### Textract A2I maintenance restriction (2026-08)

Amazon A2I entered maintenance mode in July 2026. `StartHumanLoop` rejects
accounts that are not recognized existing customers, so new callers must not
assume they can activate a human-review loop.

### Cloud Directory end of support (2026-08)

Amazon Cloud Directory is marked end-of-support in its public CLI reference.
Avoid new integrations and plan migration for existing ones.
