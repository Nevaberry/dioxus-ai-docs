# Self-Hosted Runners

Use this reference when registering runners, planning fleet upgrades,
auditing versions, building a custom autoscaler, or consuming interfaces added
to the runner process.

## Registration and rolling execution gates

Runner `2.329.0` or later is required to configure or re-register a
self-hosted runner on the new platform. This registration minimum is distinct
from the moving execution requirement.

Every runner release, including patch releases, must be installed within 30
days of publication. When a runner falls outside that window, the service
stops queuing jobs to it. Auto-update satisfies the rolling requirement when
the update service is reachable. Fleets with auto-update disabled need a
regular manual upgrade process.

A critical security release does not receive the normal 30-day grace period:
job queuing pauses until the release is installed.

After enforcement:

- versions below `2.329.0` cannot register or re-register; and
- already registered runners below the moving execution floor stop receiving
  jobs.

## Cloud enforcement schedule

| Deployment | Full enforcement |
| --- | --- |
| Enterprise Cloud with Data Residency | July 31, 2026 |
| Enterprise Cloud | September 25, 2026 |
| Enterprise Server | Not affected |

Before standard Enterprise Cloud enforcement, each brownout runs from
11:00 AM through 3:00 PM ET.

Registration-only brownouts:

- August 24, 2026
- August 31, 2026
- September 2, 2026
- September 7, 2026
- September 11, 2026

Registration-and-runtime brownouts:

- September 9, 2026
- September 14, 2026
- September 16, 2026
- September 18, 2026

Treat the brownouts as operational tests: verify that inventory, upgrades,
and update-service connectivity are working before full enforcement.

## Fleet discovery and upgrade auditing

The self-hosted-runners REST API exposes runner versions when called with API
version `2026-03-10`. Use that inventory to find runners below the registration
minimum or outside the release-age window.

The following enterprise audit-log events include the runner version at
registration time:

- `org.register_self_hosted_runner`
- `repo.register_self_hosted_runner`
- `enterprise.register_self_hosted_runner`

These events are not a complete fleet inventory because they are emitted only
when a runner registers. Runtime job annotations also identify outdated
runners before enforcement.

## Custom autoscaling without Kubernetes

The public-preview `actions/scaleset` Go client exposes runner scale-set APIs
for custom autoscalers on containers, virtual machines, bare metal, or cloud
infrastructure. It handles API orchestration, while the integrator remains
responsible for:

- infrastructure setup;
- runner provisioning;
- capacity scaling; and
- runner destruction.

The standalone client supports multiple labels per scale set. Actions Runner
Controller remains the recommended implementation for Kubernetes.

## Runner `2.336.0` environment interfaces

Runner `2.336.0` adds two interfaces for workflows and actions:

- `$GITHUB_ARTIFACTS` environment files; and
- `ACTIONS_CACHE_MODE`, which exposes the effective cache mode to steps.

Any workflow or action that reads or writes these interfaces requires runner
`2.336.0` or later. Gate self-hosted labels or check fleet versions before
depending on them.

```yaml
jobs:
  inspect-cache-mode:
    runs-on: self-hosted
    steps:
      - run: echo "$ACTIONS_CACHE_MODE"
```
