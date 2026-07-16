# Svelte 5 migration

## Dependency upgrade order

For a Svelte 3 project, migrate to Svelte 4 first. From Svelte 4, update
`svelte` and related integration packages such as `vite-plugin-svelte` to their
Svelte 5-compatible releases.

Svelte 5 continues to run components written with the older component syntax,
so migration can be incremental. An application does not need to wait for all
of its component libraries to adopt runes before upgrading the application.

## Optional syntax migration

After upgrading dependencies, convert application syntax with:

```sh
npx sv migrate svelte-5
```

Treat the command as an optional application-wide conversion, not as a
prerequisite for running existing components on Svelte 5.

This staged migration behavior is attributed to batch `5.0.0`.
