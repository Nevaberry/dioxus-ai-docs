# Native Compiler and Tooling

Batch attribution: `5.9.0`, `6.0.0`, `7.0-native-port`, `7.0.0`.

## Contents

- [Choose the compiler package for the job](#choose-the-compiler-package-for-the-job)
- [Preserve the JavaScript compiler API for dependent tools](#preserve-the-javascript-compiler-api-for-dependent-tools)
- [Account for preview emit and watch limits](#account-for-preview-emit-and-watch-limits)
- [Control checker-worker parallelism](#control-checker-worker-parallelism)
- [Control parallel project builds](#control-parallel-project-builds)
- [Disable all compiler parallelism](#disable-all-compiler-parallelism)
- [Compare type ordering before a native migration](#compare-type-ordering-before-a-native-migration)
- [Use richer hover tooling](#use-richer-hover-tooling)

## Choose the compiler package for the job

### Stable native compiler

The stable native compiler installs from the standard `typescript` package and
provides the `tsc` command:

```sh
npm install -D typescript
npx tsc --build
```

Nightly native builds likewise use the standard package's `next` tag:

```sh
npm install -D typescript@next
```

### Preview-era installations

Projects still evaluating or unwinding a preview installation may have
`@typescript/native-preview`, which provides `tsgo` and can run beside the
JavaScript compiler. The preview command supports incremental compilation,
project references, and build mode:

```sh
npm install -D @typescript/native-preview
npx tsgo --build
npx tsgo --incremental
```

VS Code can use the native language service through the
`TypeScriptTeam.native-preview` extension. Keep the ability to toggle back to
the built-in service while diagnosing preview-only editor behavior.

## Preserve the JavaScript compiler API for dependent tools

The native implementation does not support the existing JavaScript-based
`typescript` compiler API. Its replacement API is not yet a stable integration
surface. Linters, formatters, editor extensions, and build tools that import the
old API need a JavaScript-based compiler package even if native `tsc` or `tsgo`
performs type-checking.

The `@typescript/typescript6` compatibility package exposes that API and a
`tsc6` executable. npm aliases let API consumers continue importing the package
name `typescript` while the native compiler uses another local name:

```json
{
  "devDependencies": {
    "@typescript/native": "npm:typescript@^7.0.2",
    "typescript": "npm:@typescript/typescript6@^6.0.2"
  }
}
```

Use the native alias for fast checking and the compatibility package for work
that invokes the compiler programmatically.

## Account for preview emit and watch limits

The native preview's downlevel JavaScript emit reaches only ES2021 and does not
compile decorators. Projects targeting older runtimes therefore need the
JavaScript compiler or another transpiler for emit.

Preview watch mode can also be less efficient in some projects. If that becomes
a bottleneck, let an external watcher invoke incremental checks:

```sh
tsgo --incremental
```

Keep these constraints scoped to preview deployments; validate current stable
behavior before retaining a workaround.

## Control checker-worker parallelism

The experimental `--checkers` flag chooses the number of type-checker workers.
Its default is `4`:

```sh
tsc --checkers 8
```

Additional workers can consume substantially more memory. Rare order-dependent
results also make a fixed worker count useful across local and CI environments.
`--checkers 1` serializes type checking, but parsing and emit can still run in
parallel.

## Control parallel project builds

Under `--build`, experimental `--builders` controls how many referenced
projects build concurrently:

```sh
tsc --build --checkers 2 --builders 2
```

Builder concurrency multiplies checker concurrency. For example,
`--checkers 4 --builders 4` can run up to 16 checkers and may need substantial
memory. Tune the product of the two settings, not each setting in isolation.

## Disable all compiler parallelism

`--singleThreaded` disables parallel parsing, checking, and emitting. Use it on
resource-constrained machines or when a higher-level build tool already
parallelizes compiler processes:

```sh
tsc --singleThreaded
```

## Compare type ordering before a native migration

The temporary `--stableTypeOrdering` flag makes the JavaScript compiler order
types and properties like the native compiler. It reduces declaration and
editor-output churn and can reveal rare inference that depends on ordering:

```sh
tsc --stableTypeOrdering
```

The flag can slow checking by up to 25%. Use it diagnostically; when it exposes
an inference error, add explicit type arguments or annotations instead of
depending on incidental ordering.

## Use richer hover tooling

Supported editors can show expandable quick-info tooltips. The `+` and `-`
controls expand referenced types in place and collapse back to the previous
view, which avoids forcing every nested type into the initial hover.

The language server also returns substantially longer hovers by default. VS
Code can change the truncation limit with `js/ts.hover.maximumLength`:

```json
{
  "js/ts.hover.maximumLength": 10000
}
```
