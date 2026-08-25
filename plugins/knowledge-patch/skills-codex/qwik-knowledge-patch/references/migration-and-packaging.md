# Migration and Packaging

## Qwik library builds and V2 consumers

As of 1.9, library builds no longer perform the Qwik transform. Library
authors should publish a new build and extend the package's accepted Qwik
range with `| ^2.0.0` when it should support V2 consumers.

A V2 project can retain V1 libraries by installing both generations. This
arrangement was supported as of 1.11:

```json
{
  "dependencies": {
    "@builder.io/qwik": "^1.11.0",
    "@qwik.dev/core": "^2.0.0"
  }
}
```

Republish the library after adopting the current library-build behavior; do
not rely on the earlier library transform being applied during its build.

## Vite dependency placement

`vite` is a peer dependency of Qwik, Qwik City, Qwik React, and Qwik Labs.
Applications are expected to depend on Vite directly. Keep it in the
application manifest so package resolution does not create or depend on
duplicate Vite imports.

Source batch: `v1.8-1.13`.
