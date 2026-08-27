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
2. Read the matching reference before relying on a default, dependency bound,
   xDS matcher, server limit, or dynamically created channel.
3. Treat security-related defaults as behavior changes even when application
   code did not opt in explicitly.
4. Preserve intentional compatibility overrides until integration and
   interoperability tests show they are no longer needed.
5. Test both success and failure paths for interceptors, name resolution,
   authorization, connection setup, and control-plane resource loading.
6. Prefer the project's manifests, lockfiles, code, and observed runtime
   behavior when they conflict with assumptions outside this patch.

## Reference index

| Reference | Topics |
| --- | --- |
| [transport-security-and-tooling.md](references/transport-security-and-tooling.md) | Post-quantum TLS, HTTP/2 frame-flood and stream limits, Android server TLS 1.3, Linux ARM64 `Grpc.Tools` packaging |
| [python-apis-runtime-and-dependencies.md](references/python-apis-runtime-and-dependencies.md) | Async status aborts, custom interceptor failures, protobuf bounds, Python 3.15 |
| [authorization-and-xds.md](references/authorization-and-xds.md) | Go RBAC matchers and header validation, deprecated `source_ip`, ORCA-to-LRS propagation, aggregate-cluster labels, control-plane connections |
| [java-channel-and-configuration.md](references/java-channel-and-configuration.md) | RFC 3986 parsing, per-channel resolver registries, numeric service config, child-channel configuration |

## Breaking changes, defaults, and compatibility risks

### TLS negotiation changes without an opt-in

- Expect new gRPC Core TLS connections to use post-quantum cryptography in key
  exchange by default.
- Recheck TLS inspection, policy enforcement, interoperability, and latency
  assumptions when transport behavior changes despite unchanged application
  configuration.
- On Android, account for TLS 1.3 on OkHttp-based gRPC Java servers as well as
  clients. Do not retain a server-only assumption that TLS 1.3 is unavailable.
- Read [transport security and tooling](references/transport-security-and-tooling.md)
  before changing TLS policy or transport dependencies.

### Java URI parsing now follows RFC 3986 by default

- Re-test targets containing reserved characters, percent escapes, unusual
  authorities, or path-like components.
- Do not assume parser behavior remains legacy-compatible merely because no
  parsing option was enabled by the application.
- Keep target parsing tests close to custom resolvers and channel construction.

### gRPC-Go throttles HTTP/2 control-frame floods

- Expect a server to stop reading from a connection after the control-buffer
  throttle reaches its limit.
- The default threshold is 100 frames; DATA and HEADERS frames do not count
  toward it.
- Override the threshold only through
  `GRPC_GO_EXPERIMENTAL_CONTROL_BUFFER_THROTTLE_LIMIT`, and validate the chosen
  value under legitimate high-control-frame workloads as well as abusive ones.

```sh
export GRPC_GO_EXPERIMENTAL_CONTROL_BUFFER_THROTTLE_LIMIT=200
```

### Java Netty servers enforce stream limits during setup

- Expect the client-initiated stream limit to apply proactively from connection
  startup rather than only after `SETTINGS_ACK`.
- Re-test clients that open streams aggressively during connection setup; the
  earlier timing window no longer permits them to bypass the configured limit.
- Include pre- and post-acknowledgment cases in transport-limit regression tests.

### xDS DENY rules enforce more matchers and validate header names

- Treat `Metadata` and `RequestedServerName` as enforced gRPC-Go xDS RBAC
  permission fields. The prior ignored behavior could let DENY rules fail open.
- Expect nested `Principal` and `Permission` header matchers, including
  non-lowercase names, to be validated and canonicalized.
- Reject `:scheme` and `grpc-`-prefixed matchers, and treat `host` as
  `:authority`.
- Re-test mixed-case names that previously matched nothing and could let a DENY
  rule fail open.
- Continue accepting deprecated `source_ip` principals as equivalent to
  `direct_remote_ip`, but generate the current spelling in new configuration.

### Java xDS control-plane connections are channel-scoped again

- Do not assume xDS control-plane connections are reused across channels.
- Reuse across many targets could exhaust the control plane's
  `MAX_CONCURRENT_STREAMS`, leaving new channels stuck in name resolution while
  waiting for resources.
- Capacity-test many-channel deployments and diagnose stalled resolution with
  both channel state and control-plane stream limits in view.

### Python protobuf compatibility has two distinct paths

- Treat 7.35.1 as the lower bound for the main Python protobuf dependency.
- Do not apply that bound indiscriminately to the separate v1.83.x
  `grpc-status` backport, whose relaxed constraint retains protobuf 6.x
  compatibility.
- Resolve the package actually constraining protobuf before changing a lockfile.

### Aggregate-cluster metric labels identify the leaf

- Expect gRPC Java xDS metrics for aggregate clusters to use the leaf cluster
  name as the backend-service label.
- Update dashboards, alerts, joins, and cardinality expectations that grouped
  these metrics by the aggregate cluster name.

## New APIs and capability quick reference

### Abort async Python RPCs with a status object

Use the status-based abort method directly from `grpc.aio.ServicerContext`:

```python
async def handle(request, context):
    await context.abort_with_status(status)
```

The method is part of the abstract async context interface. Keep custom context
implementations compatible with that interface, and test that control flow ends
as expected after the awaited abort.

### Isolate Java name resolution per channel

Use the `Grpc.newChannelBuilder` overload that accepts a
`NameResolverRegistry` when a channel must not depend on the process-global
registry. This supports isolated tests, embedded runtimes, and applications
whose channels require different resolver sets.

### Customize dynamically created Java child channels

Use `ChildChannelConfigurer` to intercept child channels created by load
balancers. Apply channel-specific interceptors or credential changes there
instead of assuming top-level channel customization reaches every dynamic child.

### Accept ordinary Java numeric service-config values

Pass integer-looking values such as `maxAttempts: 4` and
`backoffMultiplier: 2` to `defaultServiceConfig()` without converting them to
decimal literals first. Validation accepts any `Number` and normalizes accepted
values to `Double`.

### Select ORCA metrics for LRS propagation

Expect ORCA-to-LRS propagation to be enabled by default in gRPC Java. Under
gRFC A85, use xDS configuration to select which fields from backend ORCA metric
reports are copied into LRS load reports.

### Use current Python and Linux ARM64 support

- Include Python 3.15 in supported-runtime testing where the application adopts
  that interpreter.
- On Linux ARM64, account for the `Grpc.Tools` move to `manylinux_2_28` and the
  maximum-page-size alignment fix for its bundled `protoc` executable.
- Re-evaluate base-image compatibility when upgrading build tooling, even when
  generated source is unchanged.

## Implementation checklists

### Transport and packaging

- Read [transport-security-and-tooling.md](references/transport-security-and-tooling.md).
- Exercise TLS handshakes against every relevant peer and middlebox.
- Load-test the HTTP/2 control-frame threshold before overriding it.
- Test the Java Netty stream limit during connection startup.
- Run the packaged `protoc` on the actual Linux ARM64 build image.
- Verify Android server and client TLS expectations separately.

### Python

- Read [python-apis-runtime-and-dependencies.md](references/python-apis-runtime-and-dependencies.md).
- Inspect both the gRPC and `grpc-status` dependency paths before resolving
  protobuf constraints.
- Await status-based aborts and update custom async contexts.
- Test interceptor exceptions for every unary and streaming call shape in use.
- Add Python 3.15 to CI only after native and generated dependencies agree.

### Go authorization and server protection

- Read [authorization-and-xds.md](references/authorization-and-xds.md) and the
  Go section of [transport-security-and-tooling.md](references/transport-security-and-tooling.md).
- Re-run DENY-policy tests for metadata, requested server names, nested headers,
  case normalization, reserved prefixes, and `host` mapping.
- Accept legacy `source_ip` input while emitting `direct_remote_ip` in new xDS
  configuration.
- Observe connection behavior at the default flood threshold before tuning it.

### Java channels, xDS, and load balancing

- Read [java-channel-and-configuration.md](references/java-channel-and-configuration.md)
  for channel construction and parsing.
- Read [authorization-and-xds.md](references/authorization-and-xds.md) for xDS
  telemetry, labels, and control-plane connection behavior.
- Test custom target strings under RFC 3986 parsing.
- Supply a channel-local resolver registry where global state is inappropriate.
- Verify child-channel interceptors and credentials on dynamic children.
- Update metric queries to use leaf-cluster backend-service labels.
- Stress resource loading with the production-like number of channels and targets.

## Validation matrix

| Area | Minimum regression case |
| --- | --- |
| Core TLS | Connect through each deployed TLS policy and intermediary |
| Go HTTP/2 | Send legitimate and excessive non-DATA, non-HEADERS frames |
| Go RBAC | Exercise matching and non-matching DENY rules, header canonicalization, and rejected names |
| Python aborts | Await a status abort through the stock and any custom context |
| Python interceptors | Raise from each custom interceptor shape in use |
| Python dependencies | Resolve both the main protobuf path and `grpc-status` backport path |
| Java transport | Open streams before and after `SETTINGS_ACK` and confirm the client-initiated limit |
| Java targets | Parse representative custom schemes, authorities, escapes, and paths |
| Java resolvers | Construct channels with global and explicit registries |
| Java xDS | Load many targets while observing resource and stream progress |
| Java metrics | Confirm LRS selection and leaf-cluster label dimensions |
| Java child channels | Confirm injected interceptors or credentials on dynamic children |

Load only the indexed reference relevant to the implementation and task, then
retain its implementation-specific checks in code review and regression tests.
