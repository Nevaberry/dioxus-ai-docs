# Releases and Updates

Use this reference for dependency freshness policy, update candidate selection,
catalog-aware updates, global package groups, changesets, release lanes,
version plans, and update automation.

## Release-Age Policy

### Delay newly published versions (batch `2025-09`)

`minimumReleaseAge` is a delay in minutes between publication and eligibility
for installation. `minimumReleaseAgeExclude` bypasses the delay for listed
package names and, in later pnpm 10 releases, package patterns.

```yaml
minimumReleaseAge: 1440
minimumReleaseAgeExclude:
  - webpack
  - "@eslint/*"
```

An exact-version request is still gated even if metadata is cached. If a stable
dist-tag points to a version that is too new, pnpm does not fall back to a
prerelease.

pnpm 11 defaults `minimumReleaseAge` to 1440 and
`minimumReleaseAgeStrict` to false. Set the age to zero to opt out
(batch `11.0.0`).

### Exact-version exceptions (batch `2025-10`)

Exclusions accept exact versions and `||` disjunctions, so a specific release
can bypass the delay without exempting every version of the package.

```yaml
minimumReleaseAge: 1440
minimumReleaseAgeExclude:
  - nx@21.6.5
  - webpack@4.47.0 || 5.102.1
```

Any `pnpm audit --fix` adds the minimum patched version to this exclusion list
so security fixes are not delayed (batch `11.0.0`).

### Candidate selection (batches `2025-10` and `2026-08`)

`pnpm outdated` respects release age. If `latest` is too new, pnpm may choose
the highest mature version even when it is in a different major.

With a release-age gate active, `resolutionMode: lowest-direct` and
`resolutionMode: time-based` retain their lowest-satisfying direct-dependency
selection rather than being forced to the highest eligible version.

### Prune stale exceptions (batch `2026-08`)

`minimumReleaseAgeExcludePrune` makes `add`, `update`, and `remove` delete
package/version exclusions absent from the newly written lockfile. It keeps
package-name patterns and skips cleanup when `sharedWorkspaceLockfile` is
false.

```yaml
minimumReleaseAgeExcludePrune: true
```

## Catalog-Aware Updates

### Update catalog entries (batch `2025-05-06`)

`pnpm update` resolves dependencies referenced through `catalog:` and writes
new ranges to `pnpm-workspace.yaml`.

`catalogMode` controls whether additions select catalog entries:

- `strict` requires a version within the catalog range;
- `prefer` uses a compatible entry and otherwise saves a direct dependency;
- `manual` keeps catalog selection explicit.

### Move compatible catalog resolutions (batch `2026-08`)

In a non-manual mode, `pnpm add <pkg>@<version>` and
`pnpm update <pkg>@<version>` move a compatible catalog entry's resolved
version rather than silently dropping the explicit request. Strict mode still
rejects a version outside the catalog range.

Projects excluded from that install use the moved resolution on their next
installation.

### Prune unused catalog entries (batches `2025-08` and `2026-08`)

`cleanupUnusedCatalogs` removes unused catalog entries during install. Its
replacement is `catalogPrune`; the newer setting wins if both are set.

## Update Reports and Interactive Selection

`pnpm outdated` and `pnpm update --interactive` include Node.js, Deno, and Bun
dependencies declared with `runtime:` specifiers (batch `11.1-11.3`).

`pnpm update --global --interactive` selects global installation groups for
targeted updates without listing package names (batch `2026-08`).

Global packages are isolated into groups in pnpm 11. Space-separated names
create separate groups, while comma-separated names share a group and are
updated or removed together (batches `11.0.0` and `11.1-11.3`).

## Update Configuration

Top-level `update` replaces `updateConfig`. The deprecated key works until the
next major, but `update` wins if both are present. Use `update.ignoreDeps` for
package patterns (batch `11.10-11.17`).

```yaml
update:
  ignoreDeps:
    - webpack
    - "@babel/*"
```

## Generate Release Intents from Dependency Updates

`pnpm update --changeset` writes a patch release intent for workspace packages
whose dependencies or optional dependencies changed. A peer dependency change
produces a major intent. Catalog consumers are included
(batch `11.10-11.17`).

Enable this by default with `update.changeset: true` and override one command
with `--no-changeset`. If `.changeset/config.json` is missing, pnpm warns and
writes no intent.

```yaml
update:
  changeset: true
```

## GitHub Actions Dependency Updates

`pnpm outdated` and interactive update inspect action dependencies in workflow
files. A non-interactive update requires `--include-github-actions` or
`update.githubActions: true` (batch `11.10-11.17`).

Updates pin exact commits and retain release tags in comments.
`update.githubActionsServer` selects an Enterprise base URL; otherwise pnpm
uses `GITHUB_SERVER_URL` and then `https://github.com`. Setting
`githubActions: false` disables action inspection everywhere.

```yaml
update:
  githubActions: true
  githubActionsServer: https://github.example.com
```

## Native Workspace Release Management

### Change intents and version plans (batch `11.10-11.17`)

`pnpm change` writes changesets-compatible intent files. `pnpm change status`
previews the plan. `pnpm version -r` consumes intents with:

- dependent-package propagation;
- fixed groups;
- `maxBump`;
- filters and dry runs;
- changelog generation; and
- a committed ledger recording consumed intents.

An unpublished package first releases at its manifest version without applying
pending intents; those intents apply to its next release. `pnpm version
from-git` creates versions from Git state.

```sh
pnpm change
pnpm change status
pnpm version -r --dry-run
pnpm version from-git
```

With `--json`, an empty recursive version plan prints `[]`
(batch `2026-08`).

### Release lanes (batch `11.10-11.17`)

`pnpm lane <name> --filter <package>` moves selected packages to
`X.Y.Z-<lane>.N` prerelease versions. `pnpm lane main` returns them to the main
line. Configure lanes below `versioning.lanes`.

```sh
pnpm lane next --filter my-package
pnpm lane main --filter my-package
```

`versioning.changelog.storage` defaults to `registry`, composing changelogs at
publish time without committing `CHANGELOG.md`. Choose `repository` when
changelog files must be committed.

### Epic major-version bands (batch `11.10-11.17`)

`versioning.epics` links member packages to a lead. Lead major `M` confines
member majors to `M*100` through `M*100+99`. A member cannot cross the band
until the lead advances; a stable lead-major release rebases members to the
new band floor.

Membership selectors accept package names, directories, and negations.

## Convergence Overrides

An empty-range selector such as `"pkg@"` replaces only dependency edges whose
declared range accepts the exact override value. This converges compatible
consumers without forcing incompatible ones (batch `11.10-11.17`).

```yaml
overrides:
  "form-data@": 4.0.6
```

The override value must be exact. pnpm warns if all affected ranges admit a
newer convergence target.

## Staged Release Approval

`pnpm stage` publishes a hidden version and supports list, view, download,
approve, and reject operations (batch `11.1-11.3`). Registry metadata with an
`approver` field receives the strongest staged-publish trust rank
(batch `11.4-11.5`).

Use staged publishing for registry approval workflows; use release lanes for
coordinated workspace prerelease versioning.
