# Migration and Packages

## Publishing Qwik libraries

Since 1.9, Qwik library builds no longer perform the Qwik transform. Library
authors should publish a fresh build instead of relying on consumer-side
behavior from an older artifact.

For a library intended to support both package generations, extend its
accepted Qwik range with `| ^2.0.0`.

## Keeping V1 libraries in V2 applications

Since 1.11, a V2 application can retain libraries built against V1 by
installing both generations:

```json
{
  "dependencies": {
    "@builder.io/qwik": "^1.11.0",
    "@qwik.dev/core": "^2.0.0"
  }
}
```

Keep the two runtimes deliberate; do not remove the V1 package while a
retained library still imports it.

## Vite dependency placement

`vite` is a peer dependency of Qwik, Qwik City, Qwik React, and Qwik Labs.
Applications must declare Vite directly. This avoids duplicate Vite imports
through framework packages.

## Vite 7 toolchain

Qwik core and Qwik City moved to Vite 7 in 1.16. Align the application's Vite
dependency, plugins, and configuration with that major when upgrading either
package.

## Tailwind integrations

The Qwik integration supports Tailwind CSS 4. The CLI also lets projects
continue using Tailwind CSS 3; choose the generation that matches the
application's existing stylesheet and plugin configuration.

## Compiled i18n scaffolding

Add the compiled-i18 integration with the Qwik CLI:

```sh
qwik add compiled-i18
```

In a monorepo, combine it with `projectDir` to target a subproject:

```sh
qwik add compiled-i18 --projectDir=packages/my-package
```
