# Notifications, observability, and Receivers

## Add metadata to events

Since 2.5.0, annotations on Flux `Kustomization` and `HelmRelease` objects can
add metadata to notification events. An image-policy marker can update an
event annotation along with the workload value:

```yaml
metadata:
  annotations:
    event.toolkit.fluxcd.io/image: docker.io/org/my-app:1.0.0 # {"$imagepolicy": "apps:my-app"}
spec:
  values:
    image:
      tag: 1.0.0 # {"$imagepolicy": "apps:my-app:tag"}
```

The provider then receives the new full image reference in the event body.

## Report Git commit status

Notification-controller can update Git commit statuses for events from
Kustomizations backed by `OCIRepository` sources since 2.5.0. By 2.8.0,
commit-status reporting accepts events from every Flux API, including
HelmReleases.

Annotate the involved object with the revision used for status reporting:

```yaml
metadata:
  annotations:
    event.toolkit.fluxcd.io/commit: "<commit-sha>"
```

Since 2.6.0, a notification `Provider` can derive a distinct status identifier
with the CEL-based `spec.commitStatusExpr`. This is useful when many clusters
report status to one monorepo commit:

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

## Comment on pull and merge requests

The 2.8.0 provider types below post and update a deduplicated deployment-status
comment without an intermediary CI workflow:

- `githubpullrequestcomment`
- `gitlabmergerequestcomment`
- `giteapullrequestcomment`

For these providers, annotate the event source with `change_request` rather
than `commit`:

```yaml
metadata:
  annotations:
    event.toolkit.fluxcd.io/change_request: "42"
```

Use `change_request` for comment providers and `commit` for status providers.

## Configure Provider authentication and transport

Since 2.6.0, notification-controller supports Azure Workload Identity when it
publishes to Azure Event Hub. The `github` and `githubdispatch` providers can
authenticate as a GitHub App.

Provider transport options added in 2.7.0 include:

- `spec.proxySecretRef` for proxy credentials;
- `spec.certSecretRef` for mutual-TLS key and certificate material;
- `zulip` as a Provider type.

GitRepository GitHub App authentication also supports mutual TLS in this
generation; configure the repository transport material separately from the
App credentials.

## Export OpenTelemetry reconciliation traces

A Provider of type `otel`, added in 2.7.0, converts Flux events into related
spans. Source objects emit root spans; consuming Kustomizations and
HelmReleases emit child spans.

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

Point `address` at an OTLP HTTP trace endpoint.

## Filter Receiver targets

Since 2.5.0, a `Receiver` can use a CEL expression to filter its declared
resources. A webhook then reconciles only objects that match the expression
instead of every declared target.

Referenced `Receiver.spec.secretRef` objects can trigger immediate
reconciliation when they receive the
`reconcile.fluxcd.io/watch: Enabled` label, or when they match the controller's
`--watch-configs-label-selector` setting (since 2.7.0).

## Secure and trigger generic Receivers

Since 2.9.0, generic Receivers can validate an OIDC ID token instead of an
HMAC shared secret. Invoke a Receiver with the CLI rather than constructing a
webhook request manually:

```shell
flux trigger receiver
```

For GCR Receivers upgraded to 2.9.0, add both `email` and `audience` to the
referenced Secret. Their absence is an upgrade error even if the Receiver API
itself has already been migrated.
