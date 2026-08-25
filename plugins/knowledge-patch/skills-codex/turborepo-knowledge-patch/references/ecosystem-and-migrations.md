# Ecosystem, Documentation, and Migrations

## Use Dependency-Aware Bun Support

`turbo prune` supports Bun 1.2 or newer and its text lockfile (since 2.5.0):

```bash
turbo prune web
```

Stable Bun support parses the `bun.lock` v1 format granularly (since 2.6.0).
Changing one application's dependencies invalidates only packages affected by
that dependency change rather than every package in the repository.

## Use Yarn Catalogs

The lockfile parser understands catalogs from Yarn 4.10.0 and newer (since
Turborepo 2.7.0). Catalog changes invalidate only affected packages and tasks:

```yaml
catalog:
  react: ^19.2.3
```

## Find Versioned Documentation

Documentation routes can return Markdown when requested with
`Accept: text/markdown`, and appending `.md` to a route also requests Markdown
(since 2.8.0). `/sitemap.md` is the machine-readable documentation index.
Version-pinned documentation is available on version subdomains such as
`v2-7-6.turborepo.dev`.

```bash
curl -sL -H "Accept: text/markdown" https://turborepo.dev/repo/docs
curl -sL https://turborepo.dev/sitemap.md
```

Search documentation from the terminal with `turbo docs` (since 2.8.0):

```bash
turbo docs "package configurations"
```

## Install Supplemental Repository Guidance

An official Turborepo skill supplies monorepo patterns and anti-patterns to
compatible development assistants (since 2.8.0):

```bash
npx skills add vercel/turborepo
```

Treat this as supplemental project guidance and still check the installed CLI,
configuration schema, and repository behavior.

## Run Catalog-Aware Migrations

The migration codemod handles package-manager catalogs (since 2.10.0):

```bash
npx @turbo/codemod migrate
```

Review the resulting manifest and lockfile changes before committing them.

## Use Cargo Workspaces

Turborepo supports repositories containing only a Cargo workspace and infers
tasks for workspace members (since 2.10.0). Native Cargo integration also
provides a formatting task (since 2.10.8), so formatting can run through the
same task graph as other Cargo work.

## Run on Android Through Termux

The `turbo` CLI supports Android when run in a Termux environment (since
2.10.8).

## Use uv Workspaces

Turborepo discovers uv workspaces and runs their native tasks (since 2.10.8).
Its uv integration also:

- hashes dependency closures from the uv lockfile;
- watches uv workspace changes; and
- prunes uv workspaces with dependency-aware outputs.

These behaviors keep Python workspace cache invalidation and pruned artifacts
scoped to the relevant dependency closure.
