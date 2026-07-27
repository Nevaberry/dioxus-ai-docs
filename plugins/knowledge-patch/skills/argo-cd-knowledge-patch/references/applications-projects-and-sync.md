# Applications, Projects, and Sync

## Comparison and reconciliation

- In 3.0.0, the defaults for comparison options changed. Do not assume that
  omitted options retain 2.x behavior; set behavior-critical comparison
  choices explicitly and inspect diffs during an upgrade.
- Known interim resources are excluded by default since 3.0.0. Transient
  objects that previously affected comparison or reconciliation may no longer
  appear unless the exclusion behavior is changed.
- Resource customizations can target `CustomResourceDefinition` resources
  since 3.0.0. Remember that a CRD customization concerns the CRD object
  itself, not automatically every custom resource defined by it.

## Sync execution

### Revision selection on retry

Since 3.2.0, the application controller can use a newer revision when retrying
a failed sync rather than remaining tied to the original attempt's revision.
Record both attempt and revision in deployment auditing, and disable assumptions
that retries necessarily reproduce the original manifest set.

### Explicit automated-sync state

Since 3.1.0, automated sync has an `enabled` field:

```yaml
spec:
  syncPolicy:
    automated:
      enabled: true
```

Use the field when generated configuration or policy checks need automation
intent to be explicit rather than inferred from the presence of `automated`.

### Application-level missing-resource dry runs

Since 3.1.0, an Application can set the sync option directly:

```yaml
spec:
  syncPolicy:
    syncOptions:
      - SkipDryRunOnMissingResource=true
```

This is useful when the same sync introduces an API type and its instances.
Avoid setting it indiscriminately because it suppresses dry-run detection of
unexpectedly absent APIs.

### Server-side apply migration

Server-side apply gained controls for field-manager migration in 3.1.0. Treat
the migration as a field-ownership change: identify the prior manager, choose
the intended manager, and inspect `managedFields` after reconciliation where
multiple controllers touch the same object.

### Sync result detail

Resources stored in a sync result include their images since 3.1.0. Consumers
can use that record to correlate a sync outcome with deployed image references
without reconstructing them solely from the live workload.

## Project sync windows

- Sync-window matching gained an opt-in AND operator in 3.0.0. Use it when all
  selected criteria must match rather than relying on the ordinary matching
  relationship.
- AppProject sync windows gained a `description` field in 3.1.0. Record the
  operational purpose, owner, and exception procedure close to the window.
