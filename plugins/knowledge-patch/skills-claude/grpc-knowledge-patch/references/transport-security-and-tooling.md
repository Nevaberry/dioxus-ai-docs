# Transport Security, HTTP/2 Limits, and Tooling

Use this reference when upgrading a transport, changing server connection
limits, validating TLS policy, or generating code on Linux ARM64.

## Post-quantum TLS key exchange (`core-1.83.0`)

gRPC Core uses post-quantum cryptography for TLS key exchange by default on
new connections. This is a default-level security behavior change; application
code does not need to request it.

When upgrading:

- exercise handshakes with every supported peer, proxy, inspection device, and
  policy-enforcement point;
- compare negotiation and latency observations with the previous deployment;
- verify that connection policy does not depend on an older key-exchange
  assumption; and
- retain any compatibility override until interoperability tests demonstrate
  that it can be removed.

## Linux ARM64 `Grpc.Tools` packaging (`core-1.83.0`)

The C# `Grpc.Tools` build aligns the maximum page size to fix an ARM64
`protoc` crash and moves the package to `manylinux_2_28`.

Treat the packaging baseline as part of the toolchain upgrade:

1. Run the bundled `protoc` on the same Linux ARM64 image used in CI or
   production builds.
2. Confirm that the image supports the new manylinux baseline.
3. Regenerate a representative source set and compare the build result.
4. Diagnose executable startup failures as packaging compatibility issues
   before changing `.proto` inputs.

## gRPC-Go HTTP/2 frame-flood limit (`go-1.82.1`)

The gRPC-Go server stops reading from a connection when HTTP/2 frame traffic
reaches its control-buffer throttle limit. The default is 100 frames. DATA and
HEADERS frames are excluded from this count.

Change the threshold with the environment variable below only when a measured
legitimate workload needs a different value:

```sh
export GRPC_GO_EXPERIMENTAL_CONTROL_BUFFER_THROTTLE_LIMIT=200
```

Test at least three cases:

- ordinary traffic stays below the threshold and continues normally;
- a legitimate control-frame-heavy workload behaves as intended at the chosen
  threshold; and
- an excessive sequence reaches the threshold and causes the server to stop
  reading from that connection.

Do not count DATA or HEADERS frames when constructing the threshold case.

## Android server TLS 1.3 (`java-1.83.0`)

The gRPC-Java OkHttp transport enables TLS 1.3 for servers on Android. Android
clients already had TLS 1.3 enabled.

Validate client and server roles separately. In particular, revisit tests or
policy checks that assumed an Android server could not negotiate TLS 1.3, and
exercise every supported peer combination after the transport upgrade.

## Netty server stream-limit enforcement (`java-1.83.1`)

The gRPC-Java Netty server proactively enforces its client-initiated stream
limit from connection startup. Enforcement no longer waits for
`SETTINGS_ACK`, closing the setup window in which a client could exceed the
limit.

Regression coverage should:

- open enough client-initiated streams to reach the configured limit before
  `SETTINGS_ACK`;
- confirm that additional streams cannot bypass the limit during setup;
- repeat the boundary test after connection setup; and
- preserve an under-limit case to show normal startup still succeeds.
