# Self-Hosted Runners

## Separate registration and execution gates

Runner `2.329.0` or later is required to configure or re-register a
self-hosted runner on the new platform. This registration floor is separate
from the moving execution requirement.

Every release, including a patch release, must be installed within 30 days of
publication. After that window, the service stops queuing jobs to a runner on
the old release. A critical security release pauses job queuing until it is
installed and has no normal grace period.

Auto-update satisfies the rolling requirement only when the update service is
reachable. For fleets with auto-update disabled, schedule discovery, rollout,
and verification often enough to stay inside the release-age window.

## Cloud enforcement and brownouts

Full enforcement begins on this schedule:

| Deployment | Enforcement begins |
| --- | --- |
| Enterprise Cloud with Data Residency | July 31, 2026 |
| Enterprise Cloud | September 25, 2026 |
| Enterprise Server | Not affected |

Before the standard Enterprise Cloud date, every brownout runs from 11:00
AM–3:00 PM ET:

| Effect | Dates in 2026 |
| --- | --- |
| Registration only | August 24, August 31, September 2, September 7, September 11 |
| Registration and runtime | September 9, September 14, September 16, September 18 |

After enforcement, a runner below `2.329.0` cannot register or re-register.
An already registered runner below the moving execution floor stops receiving
jobs. Validate both gates during fleet readiness reviews.

## Discover runners that need upgrades

Use the self-hosted-runners REST API with API version `2026-03-10` to retrieve
runner versions and build a complete fleet inventory.

Registration audit-log searches can use these events:

- `org.register_self_hosted_runner`
- `repo.register_self_hosted_runner`
- `enterprise.register_self_hosted_runner`

These events include the registered runner version, but they are not a
complete inventory because they exist only when registration occurs. Runtime
job annotations also identify outdated runners before enforcement; use them as
an operational signal, not as the sole inventory source.

## Custom autoscaling without Kubernetes

The public-preview `actions/scaleset` Go client handles runner scale-set API
orchestration for custom autoscalers on containers, VMs, bare metal, or cloud
infrastructure. It also supports multiple labels per scale set.

The client does not provide infrastructure setup, provisioning, capacity
decisions, scaling, or runner destruction. The integrator owns that lifecycle.
Actions Runner Controller remains the recommended implementation for
Kubernetes; use the standalone client for custom infrastructure outside that
model.

## Runner environment interfaces

Runner `2.336.0` adds two interfaces:

- `$GITHUB_ARTIFACTS` environment files; and
- `ACTIONS_CACHE_MODE`, which exposes the effective cache mode to steps.

Workflows and actions that read or write either interface require runner
`2.336.0` or later. Gate self-hosted labels or add an explicit runner-version
check before depending on them.

```yaml
jobs:
  inspect-cache-mode:
    runs-on: self-hosted
    steps:
      - run: echo "$ACTIONS_CACHE_MODE"
```

## Background-step cancellation behavior

On runner `2.336.0`, a canceled background step no longer affects the job
result, and cancellation waits for the worker to finish. A workflow whose
correctness depends on either behavior must pin or gate its self-hosted runner
version. See
[workflow-semantics-and-limits.md](workflow-semantics-and-limits.md) for the
background-step controls.
