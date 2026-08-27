# Applications, Projects, and Sync

## Comparison and reconciliation

### Make changed defaults explicit

In 3.0.0, comparison-option defaults changed from the 2.x behavior and known
interim resources became excluded by default. Set options explicitly when
transient-object participation or comparison behavior is operationally
important.

Resource customization also applies to `CustomResourceDefinition` objects.
Audit CRD-level customizations when comparison or health changes affect many
resource instances.

### Preserve webhook-managed fields

In 3.4.6, diff filtering for webhook mutations preserves descendant fields
owned by a manager. Annotation backfill also runs only when the live annotation
is unset, so it no longer overwrites a value already present on the live
resource. Diagnose ownership and live state before adding ignore rules to work
around either older behavior.

### Understand reconciliation timeout zero

In 3.5.0, `timeout.reconciliation=0` disables soft expiry while still allowing
the diff cache to be used. Do not interpret zero as disabling every cached-diff
path.

### Filter forbidden namespaces before caching

The server now discards objects from disallowed namespaces before they enter
its cache (3.5.0). This changes both internal cache contents and what callers
can retrieve; investigate namespace allowlists when resources disappear from
queries.

## Sync execution

### Enable automated sync explicitly

Since 3.1.0, `SyncPolicy.automated.enabled` can state automation intent:

```yaml
spec:
  syncPolicy:
    automated:
      enabled: true
```

Use an explicit value in generated manifests and overlays when sync automation
must not depend on legacy implicit behavior.

### Skip missing-resource dry runs at Application scope

Since 3.1.0, an Application can declare the option once:

```yaml
spec:
  syncPolicy:
    syncOptions:
      - SkipDryRunOnMissingResource=true
```

Use it when the same sync creates an API type before its instances. Skipping a
dry run also suppresses early validation for APIs that are genuinely absent.

### Control server-side apply migration

Server-side apply gained field-manager migration controls in 3.1.0. Identify
the existing and target managers, review shared fields, and inspect managed
fields after migration.

As of 3.3.13, selecting server-side apply no longer also runs auth reconcile.
Keep expectations for that sync path aligned with server-side-apply semantics.

### Preserve fields on replace

The replace sync path no longer clobbers non-ignored fields as of 3.3.13. Avoid
compensating patches that would reintroduce blanket field replacement.

### Expect retry revision movement

Since 3.2.0, the application controller can select a newer revision when it
retries a failed sync. Record the revision for each attempt rather than
assuming the original revision remains fixed throughout the retry sequence.

### Inspect images in sync results

Since 3.1.0, each resource recorded in a sync result includes its images. Use
those records to establish what image accompanied a successful or failed
deployment.

## Projects, destinations, and sync windows

### Document and combine sync-window selectors

- AppProject sync windows have a `description` field since 3.1.0. Record the
  purpose, owner, and exception procedure.
- Sync-window matching has an opt-in AND operator since 3.0.0. Enable it only
  when all configured selectors must match.
- A 3.5.0 overrun option allows a sync already in progress to continue after
  its window closes. Make the availability-versus-policy tradeoff explicit.

### Use destination service accounts in global projects

Global project configuration supports `destinationServiceAccounts` in 3.5.0,
extending destination service-account policy beyond individually defined
projects. Reconcile global and local project rules so a broad global setting
does not unintentionally widen destination access.

## Application state

### Account for Redis-backed health

Application health is stored in Redis by default as of 3.0.0. When health is
stale or absent, include Redis availability, keys, and compression settings in
the investigation rather than checking only the application controller.

### Use core mode without `server.secretkey`

In 3.5.0, the application controller can sync in core mode when
`server.secretkey` is absent. Do not retain a synthetic secret solely to work
around the older failure mode.
