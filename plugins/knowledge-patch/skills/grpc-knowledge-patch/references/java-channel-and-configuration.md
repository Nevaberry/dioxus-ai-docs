# Java Channel and Configuration APIs

Use this reference when parsing Java targets, scoping name resolvers, validating
default service config, or customizing dynamically created child channels.

All changes in this reference come from `java-1.83.0`.

## RFC 3986 parsing is the default

gRPC-Java enables RFC 3986 parsing by default. Parsing behavior can therefore
change without an application opt-in.

Retest target strings that contain:

- Custom schemes or authorities.
- Reserved characters or percent escapes.
- Empty, relative-looking, or path-like components.
- Values transformed by a custom `NameResolver` or target factory.

Do not normalize a failing target blindly. First compare the intended target
semantics with RFC 3986 parsing and the custom resolver's accepted form. Keep
regression cases for every nontrivial target syntax the application emits.

## Per-channel name resolver registries

`Grpc.newChannelBuilder` has an overload that accepts a
`NameResolverRegistry`. Use it when a channel should use an explicitly supplied
registry instead of the global registry.

This enables:

- Isolation between channels that need different resolver sets.
- Tests that do not mutate process-global resolver state.
- Embedded applications that host independent channel configurations.
- Explicit control over which resolver providers a channel can select.

When migrating, construct representative channels with the supplied registry
and verify target resolution. Do not assume a provider registered only in the
global registry is visible to a channel using an explicit registry.

## Default service config accepts any `Number`

`defaultServiceConfig()` validation accepts numeric values represented by any
Java `Number`, not only `Double`. Integer-looking JSON values such as
`maxAttempts: 4` and `backoffMultiplier: 2` no longer cause
`IllegalArgumentException` merely because of their numeric representation.

Accepted values are normalized to `Double`:

```json
{
  "methodConfig": [{
    "retryPolicy": {
      "maxAttempts": 4,
      "backoffMultiplier": 2
    }
  }]
}
```

Keep semantic validation separate from representation validation. Acceptance
of an integer-valued `Number` does not make an otherwise invalid service config
valid. In tests, pass the same shapes produced by the application's actual JSON
or map decoder.

## Child-channel configuration plugins

The `ChildChannelConfigurer` API can intercept and customize child channels
created dynamically by load balancers. Use it for changes such as injecting
interceptors or modifying credentials on those children.

Apply it with these checks:

1. Trigger the load balancer to create a child dynamically.
2. Confirm the configurer runs for that child.
3. Verify the intended interceptor ordering or credential selection on the
   resulting RPC.
4. Exercise replacement and teardown if the load balancer rotates children.
5. Keep child-specific customization from depending accidentally on mutable
   global state.

Do not assume top-level channel configuration reaches every load-balancer child
unless a test verifies that behavior.

## Review checklist

- Parse real application targets with the RFC 3986 default.
- Use an explicit resolver registry for channel-local isolation.
- Allow integer-looking `Number` values while retaining semantic service-config
  validation.
- Test customization on dynamically created children, not only the parent
  channel.
