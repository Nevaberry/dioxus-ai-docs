# Migrations and Drizzle Kit

## Runtime-aware module loading

As of `drizzle-kit@0.31.10`, module loading depends on the runtime used to
launch Drizzle Kit.

| Launch runtime | Loading path |
| --- | --- |
| Node | Use the `tsx` loader instead of `esbuild-register` |
| Bun | Bypass `tsx` and use Bun's native import system |
| Deno | Bypass `tsx` and use Deno's native import system |

The Node change allows the CLI to load both ESM and CommonJS projects.

## Diagnosis workflow

When Drizzle Kit fails to load configuration or project modules:

1. Capture the command that launches the CLI.
2. Identify whether Node, Bun, or Deno executes it.
3. Check the installed `drizzle-kit` version.
4. Select the loading path from the table above.
5. Inspect only the dependencies and configuration relevant to that path.
6. Reproduce through the same runtime after making a change.

For a Node launch, do not assume that `esbuild-register` is still the
active loader.

For a Bun or Deno launch, do not diagnose the native import path as if it
were controlled by Node's `tsx` loader.

## Review notes

Keep these distinctions explicit in a review or handoff:

- `drizzle-kit` version
- launch runtime
- project module format
- loader or native import path actually exercised

This prevents a fix for one runtime from being applied to a different
runtime path.
