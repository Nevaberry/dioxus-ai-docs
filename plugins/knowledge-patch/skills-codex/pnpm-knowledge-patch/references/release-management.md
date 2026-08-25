# Workspace Release and Update Management

## Native changes and recursive versioning (11.10-11.17)

`pnpm change` writes changesets-compatible intent files. `pnpm change status` previews the release plan, and `pnpm version -r` consumes it with dependent propagation, fixed groups, `maxBump`, filtering, dry runs, changelogs, and a committed consumption ledger. An unpublished package debuts at its manifest version without applying pending intents until its next release. `pnpm version from-git` is supported.

```sh
pnpm change
pnpm change status
pnpm version -r --dry-run
pnpm version from-git
```

## Release lanes and changelog storage (11.10-11.17)

`pnpm lane <name> --filter <pkg>` moves packages to `X.Y.Z-<lane>.N` prerelease lanes; `pnpm lane main` moves them back. Configure lanes under `versioning.lanes`.

`versioning.changelog.storage` defaults to `registry`, composing changelogs at publish time without committing `CHANGELOG.md`. Use `repository` for committed changelog files.

```sh
pnpm lane next --filter my-package
pnpm lane main --filter my-package
```

## Major-version bands with epics (11.10-11.17)

`versioning.epics` ties member packages to a lead package. Lead major `M` restricts members to majors `M*100` through `M*100+99`; a member cannot cross the band until the lead advances. A stable lead-major release rebases members to the new band floor. Membership accepts package name, directory, and negated selectors.

## Generate intents from dependency updates (11.10-11.17)

`pnpm update --changeset` writes a patch intent for workspace packages whose dependencies or optional dependencies changed, and a major intent when peer dependencies changed. Catalog consumers are included. Set `update.changeset: true` for the default and use `--no-changeset` per command. Without `.changeset/config.json`, pnpm warns and writes no intent.

```yaml
update:
  changeset: true
```

## Update GitHub Actions dependencies (11.10-11.17)

`pnpm outdated` and interactive `pnpm update` inspect workflow actions. Non-interactive updates opt in with `--include-github-actions` or `update.githubActions: true`. Updates pin exact commits and preserve release tags in comments. `update.githubActionsServer` selects an Enterprise base URL; otherwise `GITHUB_SERVER_URL` and then `https://github.com` are used. Set `githubActions: false` to skip actions everywhere.

```yaml
update:
  githubActions: true
  githubActionsServer: https://github.example.com
```

## Empty recursive plans are valid JSON (2026-08)

`pnpm version -r --json` prints `[]` when no pending changes exist, so automation can parse both empty and non-empty output.

```sh
pnpm version -r --json
```
