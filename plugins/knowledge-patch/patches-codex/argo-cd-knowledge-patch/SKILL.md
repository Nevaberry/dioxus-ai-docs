---
name: argo-cd-knowledge-patch
description: Argo CD
version: "3.2.0"
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
| [Repositories, rendering, and hydration](references/repositories-rendering-and-hydration.md) | Repository identity, Helm and OCI, config-management plugins, Kustomize, Source Hydrator |
| [CLI, API, and extensions](references/cli-api-and-extensions.md) | Server-side diff, resource retrieval, plugins, password input, logs, exec, extensions |
| [Security, identity, and RBAC](references/security-identity-and-rbac.md) | Log permissions, fine-grained RBAC, tokens, bearer auth, SSO, impersonation |
| [Operations and observability](references/operations-and-observability.md) | Repo-server contention, Redis, probes, OpenTelemetry, metrics, logs, webhooks |
| [Resource health and actions](references/resource-health-and-actions.md) | Built-in health coverage, scaling, rollout controls, Job and database actions |

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

### Validate newer rendering and API behavior

- Manifest generation uses Helm 4. Regression-test charts and plugins that
  depended on Helm 3 output or command behavior.
- Event-listing APIs return Argo CD's typed `EventList`. Update clients that
  assumed an untyped Kubernetes list.
- Objects in disallowed namespaces are filtered before entering the server
  cache, so they are absent from cache-backed retrieval as well as responses.
- Setting `timeout.reconciliation=0` disables soft expiry while retaining use
  of the diff cache; do not interpret zero as disabling that cache.

### Check transport and repository scale

- Pod exec and port forwarding use WebSockets instead of SPDY. Proxies and
  ingress layers must pass the WebSocket upgrade correctly.
- Large monorepos can trigger repo-server lock contention severe enough to
  require pod restarts. Monitor repo-server health and plan a patch-level
  upgrade that contains the deferred fix.
- Repo-server connections can use mutual TLS. Coordinate certificates and
  trust configuration before enabling it.
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

### Review server-side apply and replace paths

Server-side apply has controls for field-manager migration. Before changing
them, identify the existing manager, the intended Argo CD manager, and fields
shared with other controllers. Current server-side-apply syncs no longer also
run auth reconcile, and replace sync no longer clobbers non-ignored fields.

Webhook-diff filtering preserves manager-owned descendants, while annotation
backfill leaves an existing live annotation untouched. Include ownership and
live-value cases in diff regression tests.

### Make sync-window intent visible

- AppProject sync windows accept a `description`; use it to record purpose and
  ownership.
- Sync-window matching has an opt-in AND operator for requiring every selector
  to match.
- An overrun option lets a sync already in progress continue past the window's
  end. Decide explicitly whether completion or strict cutoff is desired.

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
supports label filtering, and Pull Request generation can filter by title. A
missing repository yields zero results rather than an ApplicationSet error, so
alert on an unexpected empty set.

Git file generators can exclude files, and generators provide `repository_id`.
Prefer repository identity over parsing a clone URL when templates need a
stable repository key. Repository discovery can also filter archived entries.

### Plan concurrent management and deletion

Generated Applications can be managed concurrently. During ApplicationSet
deletion, the controller retains its finalizer while children terminate and
checks terminating Applications against the API server. Account for that wait
in deletion automation instead of forcibly stripping the finalizer.

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
- Dry and sync sources can use separate repository URLs; diff and manifest
  commands follow the dry source revision.

Do not implement hydration cleanup by deleting unknown files. Review generated
commit messages for useful, non-secret provenance, and size hydration queue
concurrency for repository capacity.

### Update manifest-generation inputs

- Config-management plugins receive environment variables whose values are
  empty. Distinguish an empty value from an absent variable in plugin code.
- Manifest generation exposes the project as `ARGOCD_APP_PROJECT_NAME`.
- Kustomize label handling supports `--include-templates`, and integrations can
  ignore missing components.
- Git and OCI repositories can use Azure workload identity.
- Helm `valueFiles` supports wildcard globs; dependency builds honor the
  repository `insecure` setting.

## Access and CLI quick reference

### Use the current CLI capabilities

- Server-side diff is stable in CLI workflows.
- `get-resource` retrieves one resource belonging to an Application.
- CLI plugins can add commands.
- `bcrypt` prompts when `--password` is omitted; Argo CD and Helm registry
  passwords can be supplied through standard input. Avoid secrets in argv.
- Pod-log search can perform case matching.
- Namespace-aware Application and ApplicationSet commands accept their
  respective namespace controls.

### Propagate caller identity safely

The server forwards the authenticated user ID to extensions in a request
header. Extensions should use it only inside the authenticated server trust
boundary and must not treat a direct-client copy as equivalent evidence.

Bearer-token authentication is supported. OAuth2 login accepts `--sso-host`
to choose the SSO callback host; align it with externally reachable routing and
registered redirect URLs.

## Operations, health, and observability

### Keep traces connected

OpenTelemetry trace context propagates across HTTP requests. Preserve trace
headers in proxies and extensions, use the manifest environment references for
`otlp.attrs`, and pass `ARGOCD_REPO_SERVER_OTLP_HEADERS` where repo-server
export authentication requires headers.

### Expand probes and metrics deliberately

- `argocd-server` exposes a gRPC health check suitable for operational probes.
- Cluster metrics can add cluster names and labels.
- GitHub API rate-limit and sync-duration metrics are available.
- Repo-server parallelism and webhook-handler failures are observable.
- Log timestamp formatting is configurable, and klog follows that format.
- Node labels can be propagated into the Application pod view.

High-cardinality cluster and node labels can increase storage or UI costs.
Select only labels used by dashboards, alerts, or operators.

### Use built-in health and actions before custom code

Built-in health coverage has expanded across common operators, Gateway API,
policy, database, telemetry, and rollout resources. Resource actions cover
parameterized scaling, rollout flow control, Job lifecycle operations, database
suspension, pipeline recycling, restart, and Application auto-sync. Check the
health-and-actions reference before maintaining overlapping custom behavior.
