# Notifications, Receivers, and Traces

## Event metadata

Annotations on Flux Kustomization and HelmRelease objects add metadata to
notification events (since 2.5.0). An image-policy marker can update the
`event.toolkit.fluxcd.io/image` annotation along with a workload value so the
provider receives the complete image reference:

```yaml
metadata:
  annotations:
    event.toolkit.fluxcd.io/image: docker.io/org/my-app:1.0.0 # {"$imagepolicy": "apps:my-app"}
spec:
  values:
    image:
      tag: 1.0.0 # {"$imagepolicy": "apps:my-app:tag"}
```

For change-request comment providers, set
`event.toolkit.fluxcd.io/change_request`. For commit-status providers, set
`event.toolkit.fluxcd.io/commit` (since 2.8.0).

## Commit statuses

Notification-controller can update Git commit statuses from events emitted by
Kustomizations backed by OCIRepository sources (since 2.5.0).

Use `Provider.spec.commitStatusExpr` to derive a status identifier with CEL
(since 2.6.0). This is useful for distinguishing clusters in a monorepo fleet:

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: github-status
  namespace: flux-system
spec:
  type: github
  address: https://github.com/my-gh-org/my-gh-repo
  secretRef:
    name: github-app-auth
  commitStatusExpr: "(event.involvedObject.kind + '/' + event.involvedObject.name + '/' + event.metadata.clusterName)"
```

Commit-status reporting accepts events from every Flux API, including
HelmReleases (since 2.8.0).

## Pull- and merge-request comments

Since 2.8.0, these Provider types post and update a deduplicated deployment
status comment directly, without an intermediary CI workflow:

- `githubpullrequestcomment`
- `gitlabmergerequestcomment`
- `giteapullrequestcomment`

Use the `change_request` event annotation for comment providers and the
`commit` annotation for status providers.

## Receiver targeting and authentication

### CEL resource filtering (since 2.5.0)

A Receiver can filter its declared resources with a CEL expression, causing a
webhook to reconcile only matching objects.

### Watched Receiver Secrets (since 2.7.0)

Notification-controller can immediately reconcile a Receiver when its
referenced `secretRef` changes. Label that Secret with
`reconcile.fluxcd.io/watch: Enabled`, or set a controller-wide
`--watch-configs-label-selector`.

### OIDC and CLI triggering (since 2.9.0)

A generic Receiver can validate an OIDC ID token instead of an HMAC shared
secret. Invoke it with `flux trigger receiver` rather than constructing the
webhook request manually.

GCR Receivers require `email` and `audience` in their referenced Secret when
upgrading to Flux 2.9.

## Provider authentication and transport

Notification-controller supports Azure Workload Identity when publishing to
Azure Event Hub (since 2.6.0). The `github` and `githubdispatch` Provider types
can authenticate as a GitHub App in the same release.

Since 2.7.0, a Provider can load proxy credentials from `spec.proxySecretRef`
and mutual-TLS material from `spec.certSecretRef`. Zulip is also a supported
Provider type. Object-level Workload Identity covers Azure DevOps, Azure Event
Hub, and Google Pub/Sub through `Provider.spec.serviceAccountName`.

## OpenTelemetry reconciliation traces

A Provider with `type: otel` converts Flux events into related spans (since
2.7.0). Source objects create root spans; consuming Kustomizations and
HelmReleases create child spans.

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta3
kind: Provider
metadata:
  name: jaeger
  namespace: flux-system
spec:
  type: otel
  address: http://jaeger-collector.jaeger:4318/v1/traces
```
