# ApplicationSets and Generators

## Progressive Sync lifecycle

- Progressive Sync is integrated into the UI since 3.1.0, allowing operators
  to inspect and work with staged rollout behavior there.
- Since 3.2.0, an ApplicationSet with Progressive Sync enabled can delete its
  generated Applications in order. Model teardown dependencies explicitly;
  ordered creation or update does not by itself guarantee safe deletion stages.

## Pull Request generators

Generator capabilities are provider-sensitive and cumulative:

- Since 3.0.0, a Pull Request generator can expose values for use by generated
  templates.
- Since 3.1.0, Bitbucket Cloud can filter pull requests by target branch, while
  Gitea can filter them by labels.
- Since 3.2.0, Pull Request generation can filter by title.
- Since 3.2.0, a missing repository produces zero generator results instead of
  failing the ApplicationSet.

An empty result is therefore ambiguous: it can mean no pull request matched or
the repository was missing. Monitor expected result counts or repository
availability if silently producing no Applications would be unsafe.

## Git and repository metadata

- The Git file generator can exclude files from its results since 3.1.0. Keep
  exclusion patterns narrow and test them against additions as well as the
  current repository tree.
- ApplicationSet generators provide `repository_id` since 3.1.0. Use this
  stable provider identity where a template needs to distinguish repositories;
  do not infer identity only by splitting a repository URL.

## Status accounting

ApplicationSet status gained `status.resourcesCount` in 3.2.0. The default
limit governing status resources also changed. Code that consumes status must
not equate a limited resource list with the total resource count; configure a
limit explicitly when automation depends on a predictable number of entries.
