# Svelte 5 migration

## Stage the upgrade

For the `5.0.0` migration path, upgrade a Svelte 3 project to Svelte 4 first.
From Svelte 4, update `svelte` and ancillary dependencies such as
`vite-plugin-svelte` before doing an optional syntax conversion.

Svelte 5 continues to support existing component syntax. An application can
upgrade even when its own components or component-library dependencies have
not all migrated to runes syntax.

After the dependency upgrade is working, the optional application-wide syntax
migration is:

```sh
npx sv migrate svelte-5
```

Treat dependency compatibility and syntax modernization as separate steps so
that failures can be attributed to the correct change.
