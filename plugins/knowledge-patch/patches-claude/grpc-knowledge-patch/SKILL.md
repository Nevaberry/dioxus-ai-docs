---
name: grpc-knowledge-patch
description: gRPC
version: null
license: MIT
metadata:
  author: Nevaberry
---


# gRPC Knowledge Patch

Apply this skill when changing gRPC transports, generated tooling, Python
servers, Go authorization, Java channels, xDS, or load-balancing behavior.

## Working method

1. Identify the implementation, package versions, transport, and deployment
   platform involved in the task.
2. Read the matching reference before relying on a security default,
   dependency bound, xDS matcher, or dynamically created channel.
3. Treat default changes as behavior changes even when application code did
   not opt in explicitly.
4. Preserve intentional compatibility overrides until integration and
   interoperability tests show that they are no longer needed.
5. Exercise success and failure paths for interceptors, name resolution,
   authorization, connection setup, and control-plane resource loading.
6. Prefer project manifests, lockfiles, code, tests, and observed runtime
   behavior when they conflict with general assumptions.

## Reference index

| Reference | Topics |
| --- | --- |
| [transport-security-and-tooling.md](references/transport-security-and-tooling.md) | Post-quantum TLS, HTTP/2 flood protection, Netty stream limits, Android TLS, Linux ARM64 tooling |
| [python-apis-runtime-and-dependencies.md](references/python-apis-runtime-and-dependencies.md) | Async status aborts, interceptor failures, protobuf bounds, Python runtime support |
| [authorization-and-xds.md](references/authorization-and-xds.md) | Go RBAC matchers, header hardening, deprecated principals, ORCA/LRS, aggregate labels, control-plane connections |
| [java-channel-and-configuration.md](references/java-channel-and-configuration.md) | RFC 3986 parsing, resolver registries, service-config numbers, child-channel customization |

## Breaking changes, defaults, and compatibility risks

### TLS negotiation changes without an opt-in

- Expect new gRPC Core TLS connections to use post-quantum cryptography in key
  exchange by default.
- Recheck TLS inspection, policy enforcement, interoperability, and latency
  assumptions even when application TLS configuration is unchanged.
- On Android, account for TLS 1.3 on OkHttp-based gRPC Java servers as well as
  clients.
- Read [transport security and tooling](references/transport-security-and-tooling.md)
  before changing TLS policy or transport dependencies.

### Java URI parsing follows RFC 3986 by default

- Re-test targets containing reserved characters, percent escapes, unusual
  authorities, or path-like components.
- Keep target-parsing tests close to custom resolvers and channel construction.
- Do not infer legacy parsing behavior from the absence of an application
  opt-in.

### gRPC-Go throttles HTTP/2 control-frame floods

- Expect the server to stop reading from a connection when the control-frame
  limit is reached.
- The default limit is 100 frames; DATA and HEADERS frames do not count.
- Change the limit only through
  `GRPC_GO_EXPERIMENTAL_CONTROL_BUFFER_THROTTLE_LIMIT`, then validate legitimate
  high-control-frame traffic as well as abusive traffic.

```sh
export GRPC_GO_EXPERIMENTAL_CONTROL_BUFFER_THROTTLE_LIMIT=200
```

### Go xDS authorization closes fail-open paths

- Treat `Metadata` and `RequestedServerName` as enforced permission fields in
  gRPC-Go xDS RBAC rules, including DENY rules.
- Validate and canonicalize header names in nested `Principal` and `Permission`
  rules; non-lowercase names are covered by the same handling.
- Reject `:scheme` and `grpc-`-prefixed matchers, and map `host` to
  `:authority`.
- Re-test mixed-case header matchers so they cannot silently match nothing and
  let a DENY rule fail open.
- Continue accepting deprecated `source_ip` principals as equivalent to
  `direct_remote_ip`, but emit the current spelling in new configuration.

### Netty enforces stream limits during connection setup

- Expect the gRPC-Java Netty server to enforce its client-initiated stream
  limit from startup, before `SETTINGS_ACK` arrives.
- Test connection startup as well as steady-state multiplexing when clients
  approach or exceed the configured limit.

### Java xDS control-plane connections are channel-scoped

- Do not assume that xDS control-plane connections are reused across channels.
- With many targets, compare channel resolution progress with the control
  plane's `MAX_CONCURRENT_STREAMS`; exhausted streams can leave new channels
  waiting for resources.
- Capacity-test the production-like number of channels and targets.

### Python protobuf compatibility has two paths

- Treat 7.35.1 as the lower bound for the main Python protobuf dependency.
- Do not apply that bound to the separate v1.83.x `grpc-status` backport; its
  relaxed bound retains protobuf 6.x compatibility.
- Identify which package constrains protobuf before changing a lockfile.

### Aggregate-cluster metric labels identify the leaf

- Expect gRPC-Java xDS metrics for aggregate clusters to use the leaf cluster
  name as the backend-service label.
- Update dashboards, alerts, joins, and cardinality expectations that grouped
  these metrics by aggregate cluster name.

## New APIs and capability quick reference

### Abort async Python RPCs with a status object

Use the status-based abort method directly from `grpc.aio.ServicerContext`:

```python
async def handle(request, context):
    await context.abort_with_status(status)
```

The method is part of the abstract async context interface. Keep custom
context implementations compatible and verify that awaited aborts end handler
control flow as expected.

### Isolate Java name resolution per channel

Use the `Grpc.newChannelBuilder` overload that accepts a
`NameResolverRegistry` when a channel should use an explicitly supplied
registry instead of process-global resolver state.

### Customize dynamically created Java child channels

Use `ChildChannelConfigurer` to intercept child channels created by load
balancers. Apply channel-specific interceptors or credential changes there,
then verify the resulting dynamic channels.

### Accept ordinary Java numeric service-config values

Pass integer-looking values such as `maxAttempts: 4` and
`backoffMultiplier: 2` to `defaultServiceConfig()` without first converting
them to decimal literals. Validation accepts any `Number` and normalizes
accepted values to `Double`.

### Select ORCA metrics for LRS propagation

Expect ORCA-to-LRS propagation to be enabled by default in gRPC Java. Under
gRFC A85, use xDS configuration to select which fields from backend ORCA
metric reports are propagated into LRS load reports.

### Use current Python and Linux ARM64 support

- Include Python 3.15 in supported-runtime testing when the application adopts
  that interpreter.
- On Linux ARM64, account for the `Grpc.Tools` move to `manylinux_2_28` and the
  maximum-page-size alignment fix for its bundled `protoc`.
- Re-evaluate the build-image baseline when upgrading tooling, even if the
  generated source does not change.

## Implementation checklists

### Transport and packaging

- Read [transport-security-and-tooling.md](references/transport-security-and-tooling.md).
- Exercise TLS handshakes against every relevant peer and intermediary.
- Load-test the HTTP/2 control-frame threshold before overriding it.
- Test Netty's client-initiated stream limit during connection setup.
- Run the packaged `protoc` on the actual Linux ARM64 build image.
- Verify Android server and client TLS expectations separately.

### Python

- Read [python-apis-runtime-and-dependencies.md](references/python-apis-runtime-and-dependencies.md).
- Inspect both the main gRPC and `grpc-status` dependency paths before
  resolving protobuf constraints.
- Await status-based aborts and update custom async contexts.
- Test interceptor exceptions for every unary or streaming call shape in use.
- Add Python 3.15 to CI only after native and generated dependencies agree.

### Go authorization and server protection

- Read [authorization-and-xds.md](references/authorization-and-xds.md) and the
  Go section of [transport-security-and-tooling.md](references/transport-security-and-tooling.md).
- Re-run DENY-policy tests for metadata and requested server names.
- Test valid, remapped, mixed-case, and forbidden header names in nested rules.
- Accept legacy `source_ip` input while emitting `direct_remote_ip` in new xDS
  configuration.
- Observe behavior at the default flood threshold before tuning it.

### Java channels, xDS, and load balancing

- Read [java-channel-and-configuration.md](references/java-channel-and-configuration.md)
  for channel construction and parsing.
- Read [authorization-and-xds.md](references/authorization-and-xds.md) for xDS
  telemetry, labels, and control-plane connection behavior.
- Test custom targets under RFC 3986 parsing.
- Supply a channel-local resolver registry where global state is inappropriate.
- Verify interceptors and credentials on dynamically created child channels.
- Update metric queries to use leaf-cluster backend-service labels.
- Stress resource loading with a production-like number of channels and targets.
- Exercise Netty stream limits before and after connection setup completes.

## Validation matrix

| Area | Minimum regression case |
| --- | --- |
| Core TLS | Connect through each deployed TLS policy and intermediary |
| Go HTTP/2 | Send legitimate and excessive non-DATA, non-HEADERS frames |
| Go RBAC fields | Match and miss DENY rules for metadata and requested server names |
| Go RBAC headers | Cover canonical, remapped, mixed-case, and forbidden header names |
| Python aborts | Await a status abort through stock and custom contexts |
| Python interceptors | Raise from every custom interceptor call shape in use |
| Python dependencies | Resolve the main protobuf path and the `grpc-status` backport path |
| Java targets | Parse representative schemes, authorities, escapes, and paths |
| Java resolvers | Construct channels with global and explicit registries |
| Java xDS | Load many targets while observing resources and stream progress |
| Java metrics | Confirm LRS selection and leaf-cluster label dimensions |
| Java child channels | Confirm injected interceptors or credentials on dynamic children |
| Java Netty | Exceed the stream limit before `SETTINGS_ACK` and after startup |

Load only the indexed references relevant to the implementation, then retain
their implementation-specific checks in code review and regression tests.
