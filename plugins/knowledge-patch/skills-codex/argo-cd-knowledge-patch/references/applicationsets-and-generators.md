# ApplicationSets and Generators

## Progressive Sync lifecycle

Progressive Sync is represented in the UI (3.1.0). ApplicationSets with
Progressive Sync enabled can also delete generated Applications in order
(3.2.0). Treat the strategy as deletion orchestration as well as rollout
orchestration; design teardown order around dependencies between Applications.

## Pull Request generator values and filters

Pull Request generators can expose values for generated templates (3.0.0).
Filter support is provider-specific:

- Bitbucket Cloud can filter by target branch (3.1.0).
- Gitea can filter by labels (3.1.0).
- Pull Request generation can filter by title (3.2.0).

A missing repository returns zero generator results instead of failing the
ApplicationSet (3.2.0). Monitor unexpected empty sets so a missing repository
is not mistaken for a valid no-match state.

## Git and repository generator data

The Git file generator can exclude files from generated results (3.1.0).
ApplicationSet generators also provide `repository_id` (3.1.0), giving
templates a repository identity without parsing a clone URL.

Repository discovery can filter archived repositories (3.5.0). Combine that
filter deliberately with other generator filters so archiving a repository has
the intended effect on generated Applications.

## Status resource counts

ApplicationSet status contains `status.resourcesCount`, and the default limit
for status resources changes (3.2.0). Use the count to distinguish truncated
status from incomplete generation. Configure an explicit limit if an external
consumer assumes predictable status cardinality.

## Create fallback during reconciliation

If an ApplicationSet patch returns `NotFound`, reconciliation falls back to
creating the resource (3.4.6) instead of ending at the failed patch. Account for
that create path in admission, audit, and race-condition tests.

## Concurrent management and safe deletion

ApplicationSets can manage generated Applications concurrently (3.5.0). Size
concurrency around API-server and controller capacity rather than assuming
serial updates.

During deletion, the controller keeps the finalizer while child Applications
terminate and verifies terminating Applications against the API server
(3.5.0). Allow time for that lifecycle instead of stripping the finalizer as a
first response to a slow deletion.

## Namespaces and proxy configuration

ApplicationSet-in-any-namespace support is stable (3.5.0). `argocd appset`
commands can target an ApplicationSet namespace, and Application subcommands
that previously lacked it accept `--app-namespace`. Pass namespace context in
automation where names are not globally unique.

The ApplicationSet proxy URL is exposed as a native flag (3.5.0). Configure it
directly instead of relying on indirect parameter handling.

## ApplicationSet and Application UI

The UI can display an ApplicationSet within an Application resource tree and
preview the Applications it generates (3.5.0). New-Application creation
supports multi-source Applications, the network view understands Gateway API
resources, and Application lists can filter by repository URL or target
revision.

Use the preview to inspect generated intent, but retain manifest and API-level
checks for automation because UI visibility does not change reconciliation
semantics.
