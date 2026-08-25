# Repositories, Rendering, and Hydration

## Helm rendering and credentials

### Validate the Helm 4 transition

Manifest generation uses Helm 4 in 3.5.0. Test representative charts during
an upgrade instead of assuming Helm 3 output is byte-for-byte identical.

`valueFiles` accepts wildcard glob patterns, `ValuesObject` is rendered as
YAML in logs, and dependency builds honor the repository `insecure` setting:

```yaml
spec:
  source:
    helm:
      valueFiles:
        - values-*.yaml
```

Review wildcard matches for unintended files, and treat logged values as
potentially sensitive even though their representation is clearer.

### Keep Helm registry passwords out of argv

As of 3.3.13, Argo CD passes Helm registry passwords through standard input
rather than command-line arguments. Preserve this path in wrappers so process
inspection cannot expose registry credentials.

## Repository identity and authentication

### Configure Azure authentication

- Git and OCI repositories support Azure workload identity since 3.0.0.
- Azure DevOps repositories support Azure Service Principal authentication in
  3.5.0.

Choose the mechanism that matches the runtime identity boundary, grant the
minimum repository permissions, and validate token rotation without embedding
long-lived secrets in repository configuration.

### Enable repo-server mutual TLS

Repo-server supports mTLS in 3.5.0. Configure a trusted CA, client and server
identities, endpoint names, certificate lifetime, and rotation as one change.
Test every repo-server caller before requiring mutual authentication.

### Preserve per-source clone depth

Repo-server honors the referenced source's depth instead of reusing the primary
source's depth as of 3.3.13. Multi-source Applications can therefore use
different depths. Diagnose missing revisions against the source that owns the
reference.

### Accept path-prefixed tags

Repository revision handling supports Git tags with path prefixes in 3.5.0.
Do not reject or strip a tag solely because its name contains slash-separated
segments.

## Config-management plugins and Kustomize

### Preserve empty variables

Config-management plugins receive environment variables whose values are empty
as of 3.0.0. Plugin code must distinguish an empty value from a missing
variable when configuration semantics differ.

Manifest generation also exposes the Application project as
`ARGOCD_APP_PROJECT_NAME` (3.0.0). Use it as project context, not as proof of
authorization.

### Update Kustomize integration

Kustomize label processing supports `--include-templates`, and integrations can
ignore missing components as of 3.0.0. Enable missing-component tolerance only
for deliberately optional components; otherwise it can hide packaging errors.

## OCI sources

OCI source support is beta as of 3.1.0. Gate adoption according to the
deployment's tolerance for beta interfaces, and verify repository credentials,
media types, caching, and promotion workflows.

## Source Hydrator

### Process webhooks and commits

Webhook handling recognizes `sourceHydrator` fields since 3.0.0. Hydration
commit messages can be templated since 3.2.0; include useful, non-secret
provenance in the template.

Webhook-triggered refreshes add configurable jitter in 3.5.0, and webhook
handling recognizes GitHub Container Registry events. Tune jitter to spread
load without making delivery latency unpredictable, and monitor webhook
failures.

### Authenticate the source repository

Source Hydrator can use a credential template for its source repository as of
3.2.0. Scope the template narrowly enough that an unrelated repository cannot
inherit excess access.

### Preserve unmanaged files

Hydration preserves files it did not generate and writes `.gitattributes` at
the hydrated repository root as of 3.2.0. Cleanup must not delete unknown
files, and repository rules must allow the root attributes file.

### Separate dry and sync repositories

Source Hydrator is beta in 3.5.0.
`spec.sourceHydrator.drySource.repoURL` and
`spec.sourceHydrator.syncSource.repoURL` can point to separate repositories;
diff and manifest commands use the dry source's revision. Audit credentials,
branch protections, and provenance independently for the two repositories.

### Tune hydration operations

In 3.5.0, manifest-hydration queue concurrency is configurable and the README
template can be managed dynamically through `argocd-cm`. Bound concurrency by
repository and API capacity, and review ConfigMap changes to the template as
generated-content changes.

## Source Integrity

Argo CD 3.5.0 implements Source Integrity configuration and CLI support, with
opt-in alpha verification for Source Hydrator dry sources. Treat verification
as alpha behavior, define failure handling before enabling it, and test how key
or signature rotation affects hydration.
