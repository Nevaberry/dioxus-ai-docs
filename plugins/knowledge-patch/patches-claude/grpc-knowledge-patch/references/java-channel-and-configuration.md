# Java Channel and Configuration APIs

Use this reference when constructing gRPC-Java channels, supplying name
resolvers, validating service config, or customizing load-balancer-created
child channels.

## RFC 3986 target parsing (`java-1.83.0`)

gRPC-Java enables RFC 3986 parsing by default. Target interpretation can
therefore change without an application opt-in.

Keep representative parsing tests for:

- custom schemes;
- reserved characters;
- percent escapes;
- unusual authorities; and
- path-like components.

Run those cases through the same channel-construction path used by the
application. For custom resolvers, assert both which resolver is selected and
which target components it receives.

## Per-channel name resolver registries (`java-1.83.0`)

`Grpc.newChannelBuilder` has an overload that accepts a
`NameResolverRegistry`. Use it when a channel needs an explicitly supplied
resolver registry instead of the global registry.

This supports isolation and per-channel control. Test the global-registry path
and explicit-registry path separately, and verify that two channels with
different explicit registries select their intended resolvers without relying
on process-global registration.

Combine this coverage with RFC 3986 target cases when resolver selection
depends on the target scheme or authority.

## Default service config numbers (`java-1.83.0`)

`defaultServiceConfig()` accepts numeric values represented by any `Number`,
not only `Double`. Integer-looking values such as the following no longer
cause `IllegalArgumentException` solely because of their numeric
representation:

```text
maxAttempts: 4
backoffMultiplier: 2
```

Accepted values are normalized to `Double`. Preserve tests for the original
integer-looking input and the normalized result, and retain invalid-config
cases so wider numeric representation support does not weaken unrelated
validation.

## Child-channel configuration plugins (`java-1.83.0`)

`ChildChannelConfigurer` can intercept and customize child channels created
dynamically by load balancers. It can inject interceptors or modify
credentials on those child channels.

Use this API when customization must reach dynamic children rather than only
the top-level channel. Verification should:

1. Cause the load balancer to create a child channel.
2. Confirm that the configurer runs for that child.
3. Exercise an RPC through the injected interceptor, when one is configured.
4. Inspect or exercise the effective credentials, when credentials are
   modified.
5. Create more than one child when the load-balancing behavior can do so.

Do not infer that top-level channel customization is automatically inherited
by every dynamically created child; assert the child behavior directly.

## Combined channel test matrix

| Concern | Regression case |
| --- | --- |
| Parsing default | Reserved characters, escapes, authority, and path forms |
| Resolver scope | Global registry and explicit per-channel registry |
| Resolver isolation | Two channels with different supplied registries |
| Numeric config | Integer-looking input accepted and normalized to `Double` |
| Child customization | Interceptor or credential change reaches a dynamic child |
