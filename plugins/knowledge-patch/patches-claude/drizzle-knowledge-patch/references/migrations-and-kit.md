# Migrations and Drizzle Kit

## Runtime-aware module loading

As of `drizzle-kit@0.31.10`, a Drizzle Kit process launched by Node uses the
`tsx` loader instead of `esbuild-register`.

This Node loader path allows the CLI to load both ESM and CommonJS projects.

Bun and Deno do not use that `tsx` path. A launch under either runtime uses
the runtime's native import system.

## Runtime matrix

| Launch runtime | Module-loading path | Diagnostic implication |
| --- | --- | --- |
| Node | `tsx` | Check the current Node loader path for ESM or CommonJS loading |
| Bun | Bun native imports | A Node loader dependency does not control this path |
| Deno | Deno native imports | A Node loader dependency does not control this path |

The command that launches Drizzle Kit determines the relevant row. Do not
choose a loader fix from the package format alone.

## Diagnostic workflow

1. Capture the exact command that reproduces the loading failure.
2. Identify the runtime executing that command.
3. Record the installed `drizzle-kit` version.
4. Identify whether the project modules are ESM or CommonJS.
5. Follow the loader path for the actual runtime.
6. Make the smallest change that belongs to that path.
7. Rerun the exact command under the same runtime.

For a Node launch on the current path, reason about `tsx`, not
`esbuild-register`.

For Bun or Deno, reason about the native importer instead of trying to tune
the bypassed Node loader.

## Common category errors

Do not add `esbuild-register` to repair the current Node path. Drizzle Kit
replaced it with `tsx` for Node launches.

Do not add or configure `tsx` solely to repair a Bun or Deno launch. Those
runtimes bypass it.

Do not report that the CLI universally uses one loader. Loader selection is
runtime-aware.

Do not verify a change under Node when the project's actual command runs
under Bun or Deno, or vice versa.

## Verification checklist

- The launch command is recorded.
- The executing runtime is identified as Node, Bun, or Deno.
- The installed `drizzle-kit` version is recorded.
- The diagnosis follows the loader path used by that runtime.
- Both ESM and CommonJS expectations are evaluated on the Node path.
- The final test uses the same runtime as the original command.

In the handoff, state whether verification used Node's `tsx` loader or a
runtime-native import system.
