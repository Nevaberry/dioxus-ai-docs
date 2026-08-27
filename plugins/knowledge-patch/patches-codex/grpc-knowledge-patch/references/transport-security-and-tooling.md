# Transport Security, HTTP/2 Limits, and Tooling

## Post-quantum TLS key exchange is the Core default

New gRPC Core TLS connections use post-quantum cryptography for key exchange by
default. This changes negotiated security behavior without requiring an
application opt-in.

When updating Core or its TLS dependencies:

- exercise handshakes against each deployed peer, proxy, inspection device, and
  policy engine;
- compare negotiation and latency behavior rather than assuming unchanged
  application configuration means unchanged transport behavior; and
- retain deliberate compatibility overrides until interoperability tests show
  that every required peer accepts the default exchange.

## gRPC-Go control-frame flood protection

A gRPC-Go server stops reading from a connection when HTTP/2 frames fill the
control-buffer throttle. The default limit is 100 frames. DATA and HEADERS do
not count toward that limit.

Override the threshold with the environment variable below only after testing
both legitimate high-control-frame traffic and flood behavior:

```sh
export GRPC_GO_EXPERIMENTAL_CONTROL_BUFFER_THROTTLE_LIMIT=200
```

Do not treat a higher value as a general throughput setting: observe connection
read behavior, resource pressure, and recovery under the workload that requires
the override.

## Java Netty client-initiated stream limits

Since java-1.83.1, the Netty server enforces its client-initiated stream limit
proactively from connection startup instead of waiting for `SETTINGS_ACK`.
Clients can no longer use the setup window to bypass the configured limit.

Regression-test clients that create streams immediately after connecting as
well as clients that wait for settings acknowledgment. Both paths must respect
the same server limit, and tests should make any connection-setup timing
assumptions explicit.

## Android server TLS 1.3

The gRPC Java OkHttp transport enables TLS 1.3 for servers on Android. Client
support was already enabled in 1.82.0, so review server and client policy
separately instead of assuming TLS 1.3 is client-only on Android.

Test Android server handshakes with the application's enabled protocol and
cipher policy, all required peers, and any intermediary that observes or
terminates TLS.

## Linux ARM64 `Grpc.Tools` packaging

The C# `Grpc.Tools` package aligns the maximum page size for its bundled
`protoc`, fixing an ARM64 crash, and uses a `manylinux_2_28` packaging baseline.
An upgrade can therefore change build-image compatibility even when the `.proto`
inputs and generated source stay the same.

Run the packaged `protoc` in the actual Linux ARM64 build image. Check both that
the executable starts successfully and that the image satisfies the new
packaging baseline before promoting the toolchain update.
