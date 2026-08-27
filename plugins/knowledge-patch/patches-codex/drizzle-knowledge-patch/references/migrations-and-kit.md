# Migrations and Drizzle Kit

## Runtime-aware module loading

As of `drizzle-kit@0.31.10`, the CLI chooses module loading according to the
runtime that launches it.

| Launch runtime | Module-loading path |
| --- | --- |
| Node | Uses the `tsx` loader instead of `esbuild-register` |
| Bun | Bypasses `tsx` and uses Bun's native import system |
| Deno | Bypasses `tsx` and uses Deno's native import system |

On the Node path, `tsx` allows Drizzle Kit to load both ESM and CommonJS
projects.

## Diagnose loading failures

Begin with the real project command rather than assuming that Drizzle Kit is
running under Node.

1. Record the installed `drizzle-kit` version.
2. Record whether Node, Bun, or Deno launches the CLI.
3. Identify the project's module format.
4. Map the failure to the loader path in the table above.
5. Reproduce the problem with the same runtime and command.
6. Apply loader-specific changes only to the path that actually runs.
7. Retest both configuration loading and source-module loading.

## Node projects

For a Node launch on `drizzle-kit@0.31.10` or newer, investigate the `tsx`
path. Do not restore `esbuild-register` based on behavior from an older CLI
release.

Because the current Node path supports ESM and CommonJS projects, first
separate a genuine module-format problem from a stale loader assumption.

## Bun and Deno projects

Bun and Deno do not use Drizzle Kit's Node `tsx` path. Diagnose their native
import behavior instead.

Adding or changing `tsx` solely to affect a Bun or Deno launch does not target
the loader that those runtimes use.

## Handoff checklist

Report all of the following:

- the `drizzle-kit` version;
- the runtime that launched the CLI;
- whether the tested path used Node's `tsx` loader or native imports; and
- whether the project modules were ESM or CommonJS.
