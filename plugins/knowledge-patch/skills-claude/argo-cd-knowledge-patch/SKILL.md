---
name: argo-cd-knowledge-patch
description: Argo CD
version: 3.2.0
license: MIT
metadata:
  author: Nevaberry
---


# Argo CD Knowledge Patch

Use this skill when upgrading or configuring Argo CD, writing Applications or
ApplicationSets, integrating repositories and Source Hydrator, operating the
CLI or API, or updating security, health, and observability behavior. Start
with the behavior changes below, then open the reference for the task at hand.

## Reference index

| Reference | Topics |
| --- | --- |
| [Applications, projects, and sync](references/applications-projects-and-sync.md) | Comparison, reconciliation, automated sync, sync windows, apply and replace behavior |
| [ApplicationSets and generators](references/applicationsets-and-generators.md) | Progressive Sync, generators, concurrency, namespaces, deletion, status and UI |
| [Repositories, rendering, and hydration](references/repositories-rendering-and-hydration.md) | Helm, Git, OCI, Kustomize, plugins, webhooks, Source Hydrator and Source Integrity |
| [CLI, API, and extensions](references/cli-api-and-extensions.md) | Diff and resource commands, plugins, namespaces, core mode, typed events and UI extensions |
| [Security, identity, and RBAC](references/security-identity-and-rbac.md) | Authorization defaults, tokens, SSO, impersonation, Secret masking and static assets |
| [Operations and observability](references/operations-and-observability.md) | Repo-server, Redis, transport, probes, metrics, tracing, logging and caching |
| [Resource health and actions](references/resource-health-and-actions.md) | Built-in health coverage, corrected states, scaling, rollout and lifecycle actions |

## Upgrade-critical behavior changes

### Revalidate authorization

- Log access enforces RBAC by default. Give every role that reads pod logs an
  explicit permission and test both CLI and API access.
- Fine-grained RBAC inheritance is disabled by default. Policies that granted
  an Application permission and expected it to flow to resources need review.
- User-defined roles and policies undergo referential-integrity checks. Repair
  dangling references rather than relying on permissive loading.
- Server operations can use impersonation, including logs and deletes. Treat
  any compatibility switch that relaxes strict enforcement as a temporary
  migration control.

### Recheck comparison and reconciliation assumptions

- Comparison-option defaults changed, and known interim resources are excluded
  by default. Make behavior-critical comparison settings explicit.
- Diff filtering preserves manager-owned descendants, and annotation backfill
  must not replace an annotation already present on the live resource.
- A failed sync retry can move to a newer revision. Automation must not assume
  every attempt deploys the content selected by the original attempt.
- The replace path preserves non-ignored fields. Server-side apply remains on
  apply semantics without also running auth reconciliation.
- Setting the reconciliation timeout to zero disables soft expiry but does not
  disable use of the diff cache.

### Validate rendering changes

Manifest generation uses Helm 4. Test charts against its rendering behavior,
especially dependency builds and value-file selection. Wildcard patterns are
accepted in `valueFiles`, values objects render as YAML in logs, and dependency
builds honor the repository `insecure` setting.

```yaml
spec:
  source:
    helm:
      valueFiles:
        - values-*.yaml
```

### Review repository and hydration trust boundaries

- Source Hydrator is beta and can use separate dry-source and sync-source
  repositories. Diff and manifest operations use the dry source's revision.
- Source Integrity provides opt-in alpha verification for dry sources. Gate it
  according to the deployment's tolerance for alpha behavior.
- Repo-server supports mutual TLS. Align certificates, trust roots, endpoints,
  and rotation before requiring client authentication.
- Azure DevOps repositories can use a service principal; Git and OCI
  repositories can use Azure workload identity.

## Application and sync quick reference

### Enable automated sync explicitly

Set automation intent on `SyncPolicy.automated.enabled`:

```yaml
spec:
  syncPolicy:
    automated:
      enabled: true
```

Review generators and overlays for omitted values when the intended behavior
depends on unambiguous automated sync.

### Configure missing-resource dry runs deliberately

Set `SkipDryRunOnMissingResource` once at Application scope when a sync creates
a type before applying instances of it:

```yaml
spec:
  syncPolicy:
    syncOptions:
      - SkipDryRunOnMissingResource=true
```

Skipping the dry run also removes an early signal for genuinely missing APIs.

### Plan field-manager migration

Before changing server-side apply migration controls, identify the current
manager, the desired Argo CD manager, and fields shared with other controllers.
Inspect managed fields after the first migrated sync. A successful apply alone
does not prove safe ownership transfer.

### Make sync-window intent explicit

- Add a `description` that records purpose, owner, and exception path.
- Enable AND matching only when every configured selector must match.
- Use the overrun option only when an in-progress sync may continue past the
  window's end.

## ApplicationSet quick reference

### Treat Progressive Sync as lifecycle control

Progressive Sync is visible in the UI, and generated Applications can be
deleted in order. Design teardown stages as carefully as rollout stages because
later deletion may depend on earlier resources remaining available.

### Handle empty and filtered generator results

- Pull Request generators expose template values and can filter by title.
  Bitbucket Cloud adds target-branch filtering; Gitea adds label filtering.
- A missing repository returns zero results instead of failing the
  ApplicationSet. Alert when an empty set is unexpected.
- Git file generators can exclude files. Generators expose `repository_id`,
  which is safer than parsing a clone URL for a stable repository key.
- Repository discovery can filter archived repositories.

### Make concurrent deletion safe

ApplicationSets can manage generated Applications concurrently. During
deletion, keep the controller's finalizer behavior intact: it retains the
finalizer while children terminate and verifies terminating Applications
against the API server.

### Bound status consumption

ApplicationSet status exposes `status.resourcesCount`, while the default limit
for status resources changed. Use the count to distinguish truncation from
missing generator output and configure an explicit limit for consumers that
need predictable cardinality.

## Repository and rendering quick reference

### Preserve Source Hydrator intent

- Webhooks recognize `sourceHydrator` fields and hydration commit messages are
  templatable.
- A credential template can authenticate the source repository.
- Hydration preserves files it did not generate and places `.gitattributes` at
  the hydrated repository root. Do not clean hydration output by deleting
  unknown files.
- Queue concurrency is configurable, and the README template can be managed
  dynamically from `argocd-cm`.

### Update manifest-generation inputs

- Config-management plugins receive variables even when values are empty;
  distinguish an empty value from an absent variable.
- Manifest generation exposes the project through
  `ARGOCD_APP_PROJECT_NAME`.
- Kustomize supports label `--include-templates` and can ignore missing
  components.
- OCI sources are beta. Apply the same repository-authentication and rollout
  discipline used for other beta APIs.

## CLI, API, and extension quick reference

- Server-side diff is stable in CLI workflows; `get-resource` retrieves one
  resource belonging to an Application.
- CLI plugins add commands. Namespace-aware `argocd appset` and `argocd app`
  operations avoid relying on a single control-plane namespace.
- `bcrypt` prompts when `--password` is omitted. Argo CD and Helm registry
  passwords can be supplied through standard input, keeping secrets out of
  process arguments and shell history.
- Event-list APIs return Argo CD's typed `EventList`; update clients that assume
  an untyped Kubernetes list.
- Custom UI extensions must follow React 19 integration guidance and can use
  the exposed `ReactJSXRuntime` global.

## Operations, health, and observability quick reference

### Keep traces connected

OpenTelemetry context propagates over HTTP. Preserve trace headers across
proxies and extensions, use the manifest environment references for
`otlp.attrs`, and configure `ARGOCD_REPO_SERVER_OTLP_HEADERS` when repo-server
export needs headers.

### Protect repo-server availability

Large monorepos can cause lock contention severe enough to require repo-server
pod restarts. Monitor saturation and restart frequency, expose the parallelism
limit metric, and plan the patch-level upgrade that contains the deferred fix.
Enable pprof from the parameters ConfigMap only within an appropriate access
boundary.

### Prefer built-in health and actions

Built-in health and resource actions cover common operators, Gateway API,
policy, database, telemetry, scaling, rollout, Job, and Numaplane workflows.
Check the health-and-actions reference before maintaining overlapping custom
Lua.
