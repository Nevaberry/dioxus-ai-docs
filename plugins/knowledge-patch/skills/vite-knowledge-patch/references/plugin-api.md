# Plugin and Framework APIs

## Environment API

Vite's experimental Environment API gives framework and plugin authors a way
to build development integrations that more closely match production (since
6.0.0).

Adopting the API is not required for ordinary applications:

- Single-client SPA behavior is unchanged.
- Existing custom SSR applications remain backward compatible.
- The main audience is framework and plugin integration code.

Because the API is experimental, keep Environment-specific integration logic
encapsulated and test it across the environments the framework supports.

## Coordinated environment builds

The experimental Environment API adds a `buildApp` hook (since 7.0.0). Plugins
can use the hook to coordinate the building of multiple environments rather
than treating every environment build as an unrelated operation.

Use `buildApp` when a plugin needs application-level orchestration across those
builds. Keep single-environment work in the narrower integration path when no
coordination is required.
