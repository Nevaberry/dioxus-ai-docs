# Plugin and Framework APIs

## Experimental Environment API

Vite 6 adds an experimental Environment API for framework and plugin authors
(since 6.0.0). It supports development integrations whose behavior can more
closely match production environments.

The API does not change normal single-client SPA behavior. Existing custom SSR
applications remain backward compatible, so adopt the Environment API for a
specific integration need rather than treating it as a mandatory rewrite.

Because the API is experimental, keep its use behind framework or plugin
boundaries and exercise the development paths that it coordinates.

## Coordinated multi-environment builds

The experimental Environment API adds a `buildApp` hook so plugins can
coordinate builds across multiple environments (since 7.0.0). Use this hook
when a framework integration owns the relationship between environment builds,
rather than independently launching builds that need shared orchestration.

Treat `buildApp` as part of the experimental API: isolate the integration and
test every environment's output and plugin lifecycle together.
