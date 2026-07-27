# Transport Security, HTTP/2 Limits, and Tooling

Use this reference for TLS behavior, gRPC-Go server flood protection, Android
server transport support, or Linux ARM64 generated-code tooling.

## Post-quantum TLS key exchange by default

From `core-1.83.0`, gRPC Core defaults to post-quantum cryptography for TLS key
exchange. New connections therefore change security behavior without an
application opt-in.

When upgrading:

- Re-test handshakes against every supported peer, proxy, service mesh, TLS
  inspector, and policy-enforcement point.
- Treat transport-policy and performance differences as possible consequences
  of the default change even when certificates and application configuration
  stay the same.
- Keep explicit compatibility settings until interoperability tests establish
  that all deployed endpoints accept the new negotiation behavior.

Do not infer a specific algorithm or opt-out mechanism from this patch; inspect
the project's gRPC Core and TLS configuration when either detail matters.

## gRPC-Go HTTP/2 frame-flood protection

From `go-1.82.1`, the gRPC-Go server stops reading from a connection when an
HTTP/2 frame flood fills its control buffer. The default throttle limit is 100
frames. DATA and HEADERS frames are excluded from the count.

Change the threshold with:

```sh
export GRPC_GO_EXPERIMENTAL_CONTROL_BUFFER_THROTTLE_LIMIT=200
```

Operational guidance:

- Test the default against legitimate workloads that produce many control
  frames before increasing it.
- Test excessive-frame behavior separately so a tuning change does not undo
  the protection.
- Set the variable in the server's real launch environment and verify that
  deployment manifests preserve the intended value.
- Diagnose an apparently stalled connection with the throttle behavior in mind;
  the server may have deliberately stopped reading.

## Android server TLS 1.3

From `java-1.83.0`, the gRPC-Java OkHttp transport enables TLS 1.3 for servers
on Android. Android clients already had TLS 1.3 enabled in 1.82.0.

Test the two roles independently:

- Exercise Android server handshakes with the actual client and network path.
- Review protocol-version allowlists or tests that assumed TLS 1.3 applied only
  to Android clients.
- Keep server-side cipher, interception, and certificate tests distinct from
  client-side coverage.

## Linux ARM64 `Grpc.Tools` packaging

From `core-1.83.0`, the C# `Grpc.Tools` build fixes an ARM64 `protoc` crash by
aligning the maximum page size. Its Linux ARM64 packaging also moves to the
`manylinux_2_28` baseline.

When consuming the package on Linux ARM64:

- Run the bundled `protoc` inside the actual build image rather than validating
  only on an x86_64 workstation.
- Check that the image satisfies the `manylinux_2_28` packaging baseline.
- Distinguish a tool-execution or image-compatibility failure from an error in
  the generated source or `.proto` schema.
- Retest code generation after changing the SDK image, package cache, or build
  architecture.

## Review checklist

- Treat the post-quantum TLS behavior as a default change.
- Count only the HTTP/2 frame classes included by the Go throttle.
- Verify TLS 1.3 for Android servers, not just clients.
- Validate ARM64 tooling on an ARM64 environment with the required packaging
  baseline.
