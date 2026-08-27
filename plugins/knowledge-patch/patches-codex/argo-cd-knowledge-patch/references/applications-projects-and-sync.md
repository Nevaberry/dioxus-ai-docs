# Applications, Projects, and Sync

## Comparison and reconciliation defaults

The 3.0.0 defaults change several assumptions carried from earlier
installations:

- Comparison-option defaults change. Make any behavior-critical comparison
  option explicit before upgrading.
- Known interim resources are excluded by default, so transient objects that
  previously participated in comparison and reconciliation may disappear from
  those paths.
- The application controller stores Application health in Redis by default.
  Include Redis state when diagnosing stale or missing health.
- Resource customization can target `CustomResourceDefinition` objects. A CRD
  customization can therefore affect comparison or health behavior broadly.

Setting `timeout.reconciliation=0` (3.5.0) disables soft expiry but does not
disable use of the diff cache. Diagnose zero-timeout installations with that
cache behavior in mind.

## Sync retries and result records

When retrying a failed sync, the application controller can select a newer
revision rather than staying on the revision from the original attempt
(3.2.0). Capture the effective revision for every attempt when reproducibility
matters.

Resources in a sync result include their container images (3.1.0). Use those
records with the revision to establish what an attempt actually deployed.

## Explicit automated sync

`SyncPolicy.automated` has an `enabled` field (3.1.0):

```yaml
spec:
  syncPolicy:
    automated:
      enabled: true
```

Set it explicitly when generated configuration must express automation intent
without relying on the presence or shape of other automated-sync fields.

## Application-scoped missing-resource dry runs

`SkipDryRunOnMissingResource` can be set as an Application sync option
(3.1.0):

```yaml
spec:
  syncPolicy:
    syncOptions:
      - SkipDryRunOnMissingResource=true
```

This is useful when the same sync introduces a resource type and instances of
that type. Scope it carefully because it also skips an early check for an API
that is unexpectedly absent.

## Server-side apply and replace behavior

Server-side apply has controls for field-manager migration (3.1.0). Identify
the current and intended managers, review shared fields, and inspect managed
fields after migration.

Several corrected paths affect sync and diff behavior:

- When server-side apply is selected, Argo CD no longer also runs auth
  reconcile (3.3.13). The path now stays on server-side-apply semantics.
- Replace sync no longer clobbers fields that are not ignored (3.3.13).
- Webhook-mutation diff filtering preserves descendant fields owned by a
  manager rather than dropping them (3.4.6).
- Annotation backfill runs only when the live value is unset, so an existing
  live annotation takes precedence (3.4.6).

Regression-test resource ownership, ignored fields, manager-owned descendants,
and existing live annotations when moving between these behaviors.

## Server-side diff and Secret handling

Server-side diff prevents CLI Secret-mask spoofing and masks Secret data in the
last-applied-configuration annotation (3.3.13). Keep diff clients current and
do not treat client-supplied masking output as a security boundary.

## Sync windows

AppProject sync windows support a `description` field (3.1.0). Record the
window's purpose and ownership there so exceptions can be evaluated in
context.

Sync-window matching has an opt-in AND operator (3.0.0). Use it when every
configured selector must match, and test selector combinations before changing
an existing project.

An overrun option (3.5.0) lets a sync already in progress continue after its
window ends. Choose explicitly between allowing completion and enforcing the
window boundary.
