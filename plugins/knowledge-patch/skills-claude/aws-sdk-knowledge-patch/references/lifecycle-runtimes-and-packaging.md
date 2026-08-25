# Lifecycle, runtimes, and packaging

## SDK and tool lifecycle (`sdk-lifecycle-and-eol`)

### AWS SDK for .NET

- **.NET SDK v3 end of support.** Version 3 entered maintenance on March 1,
  2026 and reached end of support on June 1, 2026. Existing packages remain
  available, but receive no further updates or releases; migrate to v4.
- **.NET SDK v4 package and collection changes.** Upgrade every `AWSSDK.*`
  dependency together to 4.0.0 or later because v3 and v4 core and service
  packages cannot coexist. Collection properties now default to `null`; add
  null handling or temporarily restore v3 initialization with:

  ```csharp
  Amazon.AWSConfigs.InitializeCollections = true;
  ```

### AWS CLI and Tools for PowerShell

- **CLI v1 maintenance announcement.** CLI v1 is in the Maintenance
  Announcement phase. CLI v2 remains generally available and is the target
  for upgrades and new deployments.
- **Tools for PowerShell v4 end of support.** Version 4 reached end of support
  on June 1, 2026; move to v5, which has been generally available since June
  23, 2025.

## Runtime support (`shared-defaults-and-runtime-support`)

### Python

- **Python runtime support cadence.** Boto3, Botocore, and AWS CLI v1 support
  Python releases for six months after Python Software Foundation end of
  support. Python 3.9 support ended in April 2026, 3.10 ends in April 2027,
  and 3.11 ends in April 2028. AWS CLI v2 does not depend on local Python.

### JavaScript v3

- **JavaScript v3 Node.js and ECMAScript cadence.** The SDK supports current
  Node.js LTS majors plus the most recently retired major for roughly eight
  months. Dropping a Node.js line also drops the equivalent ECMAScript browser
  target. Node.js 18 and pre-ES2023 support ended in January 2026; Node.js 20
  and pre-ES2024 support are scheduled to end in January 2027. Pinning an
  older SDK can retain runtime compatibility but not support or updates.

## JavaScript packaging and removals

### Client and output changes (`2026-06`)

- **Removed JavaScript v3 service clients.** IoT Events, IoT Events Data,
  Panorama, and SimSpace Weaver clients were removed; applications using them
  cannot upgrade unchanged.
- **ESM output required for bundlers.** Bundler support was removed from
  `dist-cjs`; configure bundlers to consume `dist-es`.

## Service lifecycle and deprecations

### Deprecated voice APIs (`2026-07-2`)

- **Chime SDK Voice proxy API deprecations.** The proxy-session operations
  `CreateProxySession`, `DeleteProxySession`, `GetProxySession`,
  `ListProxySessions`, and `UpdateProxySession`, plus
  `PutVoiceConnectorProxy`, `DeleteVoiceConnectorProxy`, and
  `GetVoiceConnectorProxy`, are deprecated.

### Maintenance and end-of-support services (`2026-08`)

- **Textract A2I maintenance restriction.** Amazon A2I entered maintenance
  mode in July 2026. `StartHumanLoop` now rejects accounts that are not
  recognized as existing customers.
- **Cloud Directory end of support.** The public CLI reference marks Amazon
  Cloud Directory end-of-support; do not base new integrations on it.
