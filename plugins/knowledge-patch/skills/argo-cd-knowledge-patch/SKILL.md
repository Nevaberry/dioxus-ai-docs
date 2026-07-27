---
name: argo-cd-knowledge-patch
description: Argo CD
version: 3.2.0
license: MIT
metadata:
  author: Nevaberry
---

# Argo CD Knowledge Patch

Use this skill when upgrading or configuring Argo CD, authoring Applications or
ApplicationSets, extending the CLI or API, configuring repositories and Source
Hydrator, or updating health, security, and observability integrations. Start
with the behavior changes below, then open the reference for the task at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [Applications, projects, and sync](references/applications-projects-and-sync.md) | Comparison, reconciliation, automated sync, sync windows, dry runs, server-side apply |
| [ApplicationSets and generators](references/applicationsets-and-generators.md) | Progressive Sync, deletion order, Pull Request and Git generators, generator values and status |
| [Repositories, rendering, and hydration](references/repositories-rendering-and-hydration.md) | Repository identity, OCI, config-management plugins, Kustomize, Source Hydrator |
| [CLI, API, and extensions](references/cli-api-and-extensions.md) | Server-side diff, resource retrieval, plugins, password input, logs, exec, extensions |
| [Security, identity, and RBAC](references/security-identity-and-rbac.md) | Log permissions, fine-grained RBAC, tokens, bearer auth, SSO, static assets |
| [Operations and observability](references/operations-and-observability.md) | Repo-server contention, Redis, probes, OpenTelemetry, metrics, logs, pod view |
| [Resource health and actions](references/resource-health-and-actions.md) | Built-in health coverage, scaling, rollout controls, Job and Numaplane actions |

## Upgrade-critical behavior changes

### Audit log and resource RBAC

- Log access now enforces RBAC by default. Grant explicit log permissions to
  every role that must read pod logs.
- Fine-grained RBAC inheritance is disabled by default. Recheck policies that
  expected an Application permission to flow to its resources.
- User-defined roles and policies receive referential-integrity checks. Fix
  dangling role or policy references instead of relying on permissive loading.

Treat these as authorization changes, not UI-only changes. Test both the CLI
and API with representative project roles after an upgrade.

### Recheck comparison and reconciliation assumptions

- Comparison-option defaults changed. Make behavior-critical options explicit
  rather than carrying forward assumptions from an older installation.
- Known interim resources are excluded by default, changing which transient
  resources participate in comparison and reconciliation.
- Application health is stored in Redis by default. Include Redis state and
  compression configuration when diagnosing stale or missing health.
- A failed sync retry may use a newer revision instead of staying pinned to
  the revision selected by the original attempt. Automation must not assume
  that every retry deploys identical Git content.

### Check transport and repository scale

- Pod exec and port forwarding use WebSockets instead of SPDY. Proxies and
  ingress layers must pass the WebSocket upgrade correctly.
- Large monorepos can trigger repo-server lock contention severe enough to
  require pod restarts. The release notes defer the fix to a later patch, so
  monitor repo-server health and plan the patch-level upgrade.
- Kubernetes 1.32 is supported, but cluster compatibility does not remove the
  need to validate Argo CD CRDs, admission policies, and extensions.

## Application and sync quick reference

### Enable automated sync explicitly

`SyncPolicy.automated.enabled` makes automation intent explicit:

```yaml
spec:
  syncPolicy:
    automated:
      enabled: true
```

Review generated manifests and overlays for an omitted `enabled` field when
the desired state depends on unambiguous automated-sync behavior.

### Configure missing-resource dry runs at Application scope

`SkipDryRunOnMissingResource` can be declared once for the Application:

```yaml
spec:
  syncPolicy:
    syncOptions:
      - SkipDryRunOnMissingResource=true
```

Use it when a sync creates a type before applying instances of that type. Keep
the scope deliberate: skipping a dry run also removes an early validation
signal for genuinely missing APIs.

### Review server-side apply migration

Server-side apply has controls for field-manager migration. Before enabling or
changing them, identify the existing manager, the intended Argo CD manager,
and fields shared with other controllers. Inspect managed fields after the
first migrated sync instead of treating a successful apply as proof of safe
ownership transfer.

### Make sync-window intent visible

- AppProject sync windows accept a `description`; use it to record the reason,
  owner, and expected exception path.
- Sync-window matching has an opt-in AND operator. Enable it only when all
  configured selectors must match; the default matching assumption may differ.

### Inspect what actually synced

Sync-result resource records include container images. Use them when checking
which image accompanied a successful or failed deployment. Resource
customization also applies to `CustomResourceDefinition` objects, so audit CRD
customizations when comparison or health behavior changes cluster-wide.

## ApplicationSet quick reference

### Treat Progressive Sync as lifecycle control

Progressive Sync is available in the UI, and generated Applications can be
deleted in order when it is enabled. Design deletion stages as carefully as
creation and update stages; downstream teardown can depend on upstream
resources remaining available.

### Handle generator results explicitly

Pull Request generators can expose values to generated templates. Filters are
provider-specific: Bitbucket Cloud supports target-branch filtering, Gitea
supports label filtering, and Pull Request generation can filter by title.
A missing repository yields zero results rather than an ApplicationSet error,
so alert on an unexpected empty set.

Git file generators can exclude files, and generators can provide
`repository_id`. Prefer repository identity over parsing a clone URL when the
generated template needs a stable repository key.

### Bound status growth

ApplicationSet status includes `status.resourcesCount`, and the default limit
for status resources changed. Use the count to distinguish intentional
truncation from missing generator output, and configure limits explicitly when
status consumers require predictable cardinality.

## Repository and rendering quick reference

### Preserve Source Hydrator intent

- Webhooks recognize `sourceHydrator` fields.
- Commit messages can be templated.
- The source repository can authenticate through a credential template.
- Hydration preserves files it did not generate and places `.gitattributes` at
  the hydrated repository root.

Do not implement hydration cleanup by deleting unknown files; that conflicts
with the preservation behavior. Review generated commit messages for useful,
non-secret provenance.

### Update manifest-generation inputs

- Config-management plugins receive environment variables whose values are
  empty. Distinguish an empty value from an absent variable in plugin code.
- Manifest generation exposes the project as `ARGOCD_APP_PROJECT_NAME`.
- Kustomize label handling supports `--include-templates`, and integrations can
  ignore missing components.
- Git and OCI repositories can use Azure workload identity. OCI source support
  is beta, so gate it according to the deployment's tolerance for beta APIs.

## Access and CLI quick reference

### Use the current CLI capabilities

- Server-side diff is stable in CLI workflows.
- `get-resource` retrieves one resource belonging to an Application.
- CLI plugins can add commands.
- `bcrypt` prompts when `--password` is omitted; the Argo CD password can also
  be supplied through standard input. Avoid putting secrets in argv or shell
  history.
- Pod-log search can perform case matching.

### Propagate caller identity safely

The server forwards the authenticated user ID to extensions in a request
header. Extensions should use that identity only within the trust boundary of
the authenticated Argo CD server and must not accept a spoofable direct-client
header as equivalent evidence.

Bearer-token authentication is supported. OAuth2 login also accepts
`--sso-host` to choose the SSO callback host; align that host with externally
reachable routing and registered redirect URLs.

## Operations, health, and observability

### Keep traces connected

OpenTelemetry trace context propagates across HTTP requests. Preserve trace
headers in proxies and extensions, and use the manifest-provided environment
references for `otlp.attrs` when composing deployment overlays.

### Expand probes and metrics deliberately

- `argocd-server` exposes a gRPC health check suitable for operational probes.
- Cluster metrics can add cluster names and labels.
- GitHub API rate-limit and sync-duration metrics are available.
- Log timestamp formatting is configurable, and klog follows the configured
  log format.
- Node labels can be propagated into the Application pod view.

High-cardinality cluster labels and node labels can increase storage or UI
costs. Select only labels used by dashboards, alerts, or operators.

### Use built-in health and actions before custom Lua

Built-in health coverage has expanded across common operators, Gateway API,
policy, database, telemetry, and rollout resources. Resource actions now cover
parameterized scaling, rollout flow control, Job lifecycle operations, and
Numaplane promotion. Check the health-and-actions reference before maintaining
a custom health script or action with overlapping behavior.
