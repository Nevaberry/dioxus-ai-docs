# ApplicationSets and Generators

## Progressive Sync and lifecycle

Progressive Sync is integrated into the UI as of 3.1.0. Since 3.2.0,
ApplicationSets with Progressive Sync enabled can delete generated Applications
in order. Treat deletion ordering as lifecycle control: teardown stages may
depend on earlier resources remaining available.

## Generator inputs and filtering

### Pull Request generators

- Generator-defined values can feed generated templates (3.0.0).
- Bitbucket Cloud can filter by target branch and Gitea can filter by labels
  (3.1.0).
- Pull requests can be filtered by title (3.2.0).
- A missing repository produces zero generator results rather than failing the
  ApplicationSet (3.2.0). Alert when an empty result is unexpected.

### Git and repository generators

Git file generators can exclude files from results as of 3.1.0. Generators
also expose `repository_id`; use that stable identity rather than parsing the
clone URL when populating templates or downstream keys.

Repository discovery in 3.5.0 can filter repositories by archived status.
Apply the filter explicitly so archived repositories do not silently continue
to generate Applications.

## Reconciliation and concurrency

### Recover when patch finds no Application

In 3.4.6, reconciliation falls back to creating an Application when its patch
returns `NotFound`. Investigate repeated create fallbacks as possible deletion
or ownership races, but do not treat the initial patch miss as terminal.

### Manage generated Applications concurrently

ApplicationSets can manage generated Applications concurrently in 3.5.0.
When tuning concurrency, account for API-server capacity and downstream
controller load rather than considering only ApplicationSet throughput.

Deletion retains the controller finalizer while children terminate and
verifies terminating Applications against the API server. Preserve this
sequence so parent deletion cannot race ahead of child cleanup.

## Status and cardinality

ApplicationSet status has `status.resourcesCount` since 3.2.0, and the default
status-resource limit changed. Use the count to distinguish intentional
truncation from missing output. Configure a limit explicitly for automation or
dashboards that require predictable status cardinality.

## Namespaces, proxy, and user interface

### Address namespaced ApplicationSets

ApplicationSet-in-any-namespace support is stable in 3.5.0. `argocd appset`
commands can specify an ApplicationSet namespace, and previously missing
`argocd app` subcommands accept `--app-namespace`. Pass namespaces explicitly
in multi-tenant scripts.

### Configure the proxy directly

The ApplicationSet proxy URL is exposed as a native flag in 3.5.0. Prefer the
flag over indirect parameter handling, and verify that credentials and
no-proxy rules remain scoped to intended destinations.

### Use expanded previews and navigation

The 3.5.0 UI can display an ApplicationSet in an Application resource tree and
preview generated Applications. Use previews to validate template changes,
but confirm applied API objects for automation and incident response.
