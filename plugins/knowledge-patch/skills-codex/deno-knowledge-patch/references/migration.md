# Deno 2 Migration

Use this reference for the following topic-specific compatibility details.

## Configuration validation (2.0.0)

Supported `compilerOptions` are now an allowlist and unsupported options produce errors. Remote import maps and the deprecated `files` configuration are no longer supported in `deno.json`.

## Removed commands and broad flags (2.0.0)

Deno 2 removes `deno bundle` and `deno vendor`. It also removes `--allow-hrtime`, `--allow-none`, `--jobs`, `--trace-ops`, `--ts`, the generic `--unstable` flag, and `--lock-write`, so 1.x automation using them must be revised.

## Required 2.3.1 follow-up (2.3.0)

The 2.3.0 release was produced with incorrect version metadata and can report the wrong version. Upgrade to 2.3.1 rather than remaining on this build.

```sh
deno upgrade 2.3.1
```

## Resource-oriented API removals (2.0.0)

`Deno.File`, `Deno.Buffer`, the reader, writer, closer, and seeker interfaces, direct `new Deno.FsFile()` construction, and resource `.rid` properties are gone. The removed free functions include `close`, `copy`, `iter`, `read`, `readAll`, `seek`, `shutdown`, `write`, `writeAll`, and the `fdatasync`, `flock`, `fstat`, `fsync`, `ftruncate`, `funlock`, and `futime` families, including their synchronous forms.

## Runtime baseline (2.6-guide)

Deno 2.6 embeds V8 14.2, establishing the JavaScript-language compatibility baseline for the release.

## Soft-removed legacy runtime APIs (2.0.0)

`Deno.run()`, `Deno.isatty()`, and `Deno.serveHttp()` are soft-removed, while `Deno.run()` no longer supports `clearEnv`, `gid`, or `uid`. `Deno.customInspect` is removed outright.

## Toolchain baseline (2.5-guide)

Deno 2.5 embeds V8 14.0 and TypeScript 5.9.2. Its Temporal implementation was substantially overhauled but remains behind `--unstable-temporal`.

## Type-checking defaults (2.0.0)

Deno 2 uses TypeScript 5.6 and `npm:@types/node@22`, and enables `noImplicitOverride` and `useUnknownInCatchVariables` during checking. Overrides therefore need the `override` modifier, and caught values are `unknown` unless narrowed.

## TypeScript and V8 versions (2.3-guide)

Deno 2.3 embeds TypeScript 5.8 and V8 13.5, which sets the checker, language-feature, and JavaScript-runtime compatibility baseline for this release.
