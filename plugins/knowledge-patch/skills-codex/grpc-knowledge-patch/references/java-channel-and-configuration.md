# Java Channel and Configuration APIs

## RFC 3986 parsing is the default

gRPC Java enables RFC 3986 parsing by default. Target interpretation can change
without an application opt-in, especially around reserved characters, percent
escapes, authorities, and path-like components.

Keep representative target strings in tests for every custom scheme and
resolver. Include ordinary names, unusual authorities, escaped characters,
reserved characters, and ambiguous path forms, and assert which resolver and
address input each target produces.

## Per-channel name resolver registries

`Grpc.newChannelBuilder` has an overload that accepts a
`NameResolverRegistry`. Use it when channel construction must use an explicitly
supplied registry instead of process-global resolver state.

This is useful for isolated tests, embedded runtimes, and applications whose
channels need different resolver sets. Test construction with both the global
registry and an explicit registry, and verify unknown-scheme behavior in the
isolated registry rather than relying on providers registered elsewhere in the
process.

## Numeric values in default service configuration

`defaultServiceConfig()` validation accepts numeric values represented by any
`Number`, not only `Double`. Integer-looking JSON values such as
`maxAttempts: 4` and `backoffMultiplier: 2` no longer cause
`IllegalArgumentException`; accepted values are normalized to `Double`.

Pass values in the natural numeric representation produced by the application's
configuration parser. Retain validation tests for both integer-looking and
decimal-looking inputs, and account for the normalized `Double` representation
if code later inspects the service-config object.

## Configure dynamically created child channels

Use the `ChildChannelConfigurer` API to intercept and customize child channels
created dynamically by load balancers. It can inject interceptors or modify
credentials on those children.

Do not assume customization of the top-level channel automatically reaches
dynamic children. Exercise the load-balancer path that creates each child and
verify the resulting interceptor chain and credentials on the child connection,
including replacement or re-resolution paths that create another child later.
