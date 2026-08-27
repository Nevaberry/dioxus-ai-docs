# Repositories, Rendering, and Hydration

## Config-management plugin environment

Config-management plugins receive environment variables even when their values
are empty (3.0.0). Plugin code must distinguish an empty value from an absent
variable when those states have different meaning.

Manifest generation also provides the Application project name as
`ARGOCD_APP_PROJECT_NAME` (3.0.0). Use that value directly instead of deriving
project identity from unrelated fields.

## Kustomize inputs

Kustomize label processing supports `--include-templates` (3.0.0), and
integrations can ignore missing components (3.0.0). Decide whether missing
components are optional before enabling that tolerance, because it removes a
manifest-generation failure signal.

## Repository authentication and identity

Git and OCI repositories can authenticate using Azure workload identity
(3.0.0). Azure DevOps repositories can also authenticate with an Azure Service
Principal (3.5.0). Select the mechanism that matches the repository and runtime
identity model.

ApplicationSet generators expose `repository_id` (3.1.0). Prefer it over clone
URL parsing where generated configuration needs a stable repository identity.

## OCI and Helm rendering

OCI source support is beta in 3.1.0. Gate use of it according to the
deployment's tolerance for beta source behavior.

Manifest generation moves from Helm 3 to Helm 4 in 3.5.0. Regression-test
charts, dependency builds, plugins, and rendered manifests that depended on
Helm 3 behavior. Additional Helm changes include:

- `valueFiles` accepts wildcard glob patterns.
- `ValuesObject` is rendered as YAML in logs.
- Dependency builds honor the repository `insecure` setting.

```yaml
spec:
  source:
    helm:
      valueFiles:
        - values-*.yaml
```

Argo CD passes Helm registry passwords through standard input rather than
command-line arguments (3.3.13). Keep wrappers compatible with stdin-based
credential delivery and avoid reintroducing secrets in argv.

## Referenced sources and revisions

Repo-server honors a referenced source's own depth instead of applying the
primary source's depth (3.3.13). Configure each source for the history it
requires in multi-source Applications.

Repository revisions support Git tags with path prefixes (3.5.0). Do not
reject or normalize such tag names as if every tag were a single path segment.

## Source Hydrator webhooks and credentials

Webhook handling recognizes `sourceHydrator` fields (3.0.0). Source Hydrator
can use a credential template for its source repository, and its commit
messages can be templated (3.2.0). Keep generated messages useful for
provenance without including credentials or other secrets.

Webhook-triggered Application refresh supports configurable jitter and
recognizes GitHub Container Registry events (3.5.0). Use jitter to avoid
synchronized refresh bursts while preserving acceptable refresh latency.

## Preserving hydrated repository contents

Hydration preserves files it did not generate and creates `.gitattributes` at
the hydrated repository root (3.2.0). Cleanup automation must not delete
unknown files merely because a hydration pass did not generate them.

## Source Integrity and separate repositories

Source Integrity checking and CLI configuration support arrive in 3.5.0, with
opt-in Alpha verification for Source Hydrator dry sources. Treat the
verification mode as alpha and plan for its interface or behavior to change.

Source Hydrator is beta in 3.5.0. Its
`spec.sourceHydrator.drySource.repoURL` and
`spec.sourceHydrator.syncSource.repoURL` fields allow the dry source and
destination to use different repositories. Diff and manifest commands use the
dry source's revision, so diagnostics must not substitute the sync-source
revision.

## Hydration operations

Manifest-hydration queue concurrency is configurable (3.5.0). Tune it against
repository and controller capacity. The hydration README template can be
managed dynamically through `argocd-cm`; manage changes to that template as
operational configuration.

## Repo-server transport

Repo-server supports mutual TLS (3.5.0). Roll out certificates, trust roots,
and client/server expectations together so enabling mTLS does not strand
components on incompatible connection settings.
