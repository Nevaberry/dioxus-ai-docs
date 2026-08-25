# Plugin and Framework APIs

## Build Development Integrations With the Environment API

Vite `6.0.0` adds an experimental Environment API for framework and plugin
authors. It supports development integrations that more closely match their
production behavior.

The API does not change normal single-client SPA behavior. Existing custom SSR
applications remain backward compatible.

Because the API is experimental, keep integration-specific code behind clear
framework or plugin boundaries and validate behavior in the environments the
integration creates.

## Coordinate Multiple Environment Builds

In `7.0.0`, the experimental Environment API adds a `buildApp` hook. Plugins
can use the hook to coordinate builds across multiple environments.

Use `buildApp` when one plugin must orchestrate related environment builds,
rather than treating each build as unrelated. The hook remains part of the
experimental Environment API.
