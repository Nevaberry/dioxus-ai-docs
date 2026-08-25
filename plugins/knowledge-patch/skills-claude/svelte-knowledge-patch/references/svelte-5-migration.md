# Svelte 5 migration

## Upgrade dependencies before syntax

For the `5.0.0` migration, move a Svelte 3 project to Svelte 4 first. From
Svelte 4, update `svelte` and ancillary packages such as
`vite-plugin-svelte`. Existing component syntax remains valid during the
upgrade, so an application does not need to wait for every component library
to migrate before adopting Svelte 5.

After the dependency upgrade is working, optionally migrate the application's
syntax:

```sh
npx sv migrate svelte-5
```

Treat dependency adoption and syntax conversion as separate stages so each can
be tested independently.
