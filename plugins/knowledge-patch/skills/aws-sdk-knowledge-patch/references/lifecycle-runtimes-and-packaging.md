# Lifecycle, runtimes, and packaging

## Major-version lifecycle

General-availability major versions receive new services, existing-service API updates, Region support, bug fixes, and security fixes. Maintenance mode is limited to critical bug and security fixes. End of support stops all releases, although existing packages and source remain available and repositories may be archived.

### .NET

- AWS SDK for .NET v3 entered maintenance on March 1, 2026 and reached end of support on June 1, 2026. Version 4 has been generally available since April 28, 2025.
- Upgrade every `AWSSDK.*` reference to 4.0.0 or later together. Core and service package conflicts prevent mixing v3 and v4 packages in one application.
- In v4, request and response collection properties default to `null` instead of empty collections. This distinguishes unset values from explicitly empty values and avoids unnecessary allocations. Null-check before iteration.
- `Amazon.AWSConfigs.InitializeCollections = true` temporarily restores v3-style empty collections, but removes that distinction and its performance benefit.

### Go

AWS SDK for Go v1 was in maintenance from July 31, 2024 through July 30, 2025 and reached end of support on July 31, 2025. Existing binaries may continue to run, but v1 receives no fixes or service updates. Move source code to Go v2 using the one-time migration.

### JavaScript

AWS SDK for JavaScript v2 was in maintenance from September 8, 2024 through September 7, 2025 and reached end of support on September 8, 2025. Move to the modular v3 packages; an automated migration tool can assist with source conversion.

### Other successor lines

The lifecycle matrix marks AWS CLI 1.x as maintenance-announced and AWS SDK for Java 1.x and AWS Tools for PowerShell 4.x as end of support. Their generally available successor lines are AWS CLI 2.x, Java 2.x, and PowerShell 5.x.

## Python runtime cadence

Boto3, Botocore, and AWS CLI v1 retain compatibility for roughly six months after the Python Software Foundation ends a Python release.

| Python | AWS support boundary |
| --- | --- |
| 3.9 | Ended April 2026 |
| 3.10 | Scheduled for April 2027 |
| 3.11 | Scheduled for April 2028 |

AWS CLI v2 has no local Python dependency, so these runtime retirements do not apply to it.

## JavaScript runtime and ECMAScript cadence

JavaScript v3 supports current Node.js LTS releases and keeps the most recently retired major for about eight additional months. When that window closes, it also raises the browser ECMAScript target.

- Node.js 18 and targets below ES2023 lost support in January 2026.
- Node.js 20 and targets below ES2024 are scheduled to lose support in January 2027.
- New SDK releases might still execute on a retired Node.js version, but that combination is unsupported. npm warns on the package engine requirement and fails with `ENOTSUP` when `engine-strict=true`.
- Pinning an SDK release from before the January boundary can preserve runtime compatibility, but does not restore support, fixes, or service updates.

## JavaScript packaging and client removals

- The JavaScript v3 release in `2026-06` removed the IoT Events, IoT Events Data, Panorama, and SimSpace Weaver clients. Do not assume those packages remain in aggregate install or upgrade workflows.
- Bundler support was dropped from `dist-cjs`. Configure bundler resolution to use `dist-es`; reserve the CommonJS distribution for supported non-bundler consumers.

## Service API compatibility removals

- In `2026-07`, Cloud9 removed Amazon Linux 2 from the AMI options accepted by the public EC2-environment creation API after Amazon Linux 2 reached end of life on June 30, 2026.
- In `2026-07`, Outposts tightened the validation pattern for site `ContactPhoneNumber`. Sanitize and validate existing values because strings accepted by older clients can now fail validation.
