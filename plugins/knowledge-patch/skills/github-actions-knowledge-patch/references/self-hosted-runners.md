# Self-hosted runners

Use this reference when registering, upgrading, discovering, or autoscaling a
self-hosted runner fleet.

## Registration and execution gates

Runner `2.329.0` or later is required to configure or re-register a
self-hosted runner on the new platform.

Do not interpret that fixed registration minimum as a permanent execution
minimum. Every runner release, including patch releases, must be installed
within 30 days of publication. After that window, the service stops queuing
jobs to the outdated runner.

- Auto-update satisfies the rolling update requirement when the update
  service is reachable.
- Fleets with auto-update disabled need a scheduled manual upgrade process.
- A critical security release has no normal grace period: job queuing pauses
  until the release is installed.

Track the registration floor and the moving release-age floor separately in
fleet health checks.

## Cloud enforcement schedule

Full enforcement begins on these dates:

| Deployment | Enforcement |
| --- | --- |
| Enterprise Cloud with Data Residency | July 31, 2026 |
| Enterprise Cloud | September 25, 2026 |
| Enterprise Server | Not affected |

Before the standard Enterprise Cloud enforcement date, each brownout lasts
from 11:00 AM through 3:00 PM ET.

Registration-only brownouts occur on:

- August 24, 2026
- August 31, 2026
- September 2, 2026
- September 7, 2026
- September 11, 2026

Registration-and-runtime brownouts occur on:

- September 9, 2026
- September 14, 2026
- September 16, 2026
- September 18, 2026

After enforcement, runners below `2.329.0` cannot register or re-register.
Already registered runners below the moving execution floor stop running
jobs.

## Find runners that need upgrades

The self-hosted-runners REST API exposes runner versions when the request uses
API version `2026-03-10`. Use it as a fleet inventory rather than inferring
versions from labels or job history.

Enterprise audit-log searches can query these registration actions:

- `org.register_self_hosted_runner`
- `repo.register_self_hosted_runner`
- `enterprise.register_self_hosted_runner`

Their events include the runner version. They are not a complete inventory,
because an event is emitted only when a runner registers.

Runtime job annotations also identify outdated runners before enforcement.
Combine current REST inventory with annotations and registration events when
planning remediation.

## Custom scale-set autoscaling

The public-preview `actions/scaleset` Go client exposes the runner scale-set
APIs for custom autoscalers. It supports runners deployed on:

- containers;
- virtual machines;
- bare metal; and
- cloud infrastructure.

The client handles API orchestration. The integrator remains responsible for
infrastructure setup, runner provisioning, scaling decisions, and runner
destruction.

Actions Runner Controller remains the recommended implementation on
Kubernetes. Use the standalone client when Kubernetes is not the deployment
target or when the infrastructure needs a custom control plane. The client
also supports multiple labels per scale set.

## Runner 2.336.0 interfaces

Runner `2.336.0` adds support for `$GITHUB_ARTIFACTS` environment files. It
also exposes the effective cache mode to workflow steps through
`ACTIONS_CACHE_MODE`.

```yaml
jobs:
  inspect-cache-mode:
    runs-on: self-hosted
    steps:
      - run: echo "$ACTIONS_CACHE_MODE"
```

An action or workflow that depends on either interface must run on version
`2.336.0` or later. Gate self-hosted labels or check fleet inventory rather
than assuming all registered runners expose them.

## Canceled background-step behavior

Runner `2.336.0` changes cancellation handling for concurrent steps:

- canceled background steps no longer affect the job result; and
- cancellation waits for the worker to finish.

Account for the runner version when a workflow depends on the final job
result or on cleanup completing after a background step is canceled.
