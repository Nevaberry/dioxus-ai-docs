# TLS and QUIC

## Contents

- [TLS negotiation and compatibility](#tls-negotiation-and-compatibility)
- [Post-quantum and specialized TLS](#post-quantum-and-specialized-tls)
- [Choosing a QUIC integration model](#choosing-a-quic-integration-model)
- [Native QUIC streams](#native-quic-streams)
- [QUIC BIO and blocking contracts](#quic-bio-and-blocking-contracts)
- [QUIC event processing and polling](#quic-event-processing-and-polling)
- [QUIC flow control and stream termination](#quic-flow-control-and-stream-termination)
- [QUIC shutdown and diagnostics](#quic-shutdown-and-diagnostics)
- [External QUIC stacks](#external-quic-stacks)

## TLS negotiation and compatibility

### Ignore optional future signature algorithms

Prefix an unknown entry with `?` in `SignatureAlgorithms`, `ClientSignatureAlgorithms`, or the corresponding `SSL` and `SSL_CTX` signature-algorithm setters to make OpenSSL ignore it (since 3.3.0). Unknown entries without `?` remain errors. Use this for optional future algorithms in a configuration intended to span deployments.

### Prefer PSK-only resumption when appropriate

Set `SSL_OP_PREFER_NO_DHE_KEX` on a TLS 1.3 server to prefer PSK-only session resumption over PSK with DHE when the client offers both (since 3.3.0). Apply the option only when loss of fresh DHE on resumed sessions matches the security policy.

### Account for renegotiation signaling

When a connection's minimum protocol version is above TLS 1.0, ClientHello carries an empty renegotiation extension instead of the empty-renegotiation SCSV (since 3.4.0). Do not reject the extension merely because renegotiation itself is unavailable at the configured versions.

### Use integrity-only TLS 1.3 suites deliberately

OpenSSL supports RFC 9150 `TLS_SHA256_SHA256` and `TLS_SHA384_SHA384` integrity-only TLS 1.3 cipher suites (since 3.4.0). These suites do not provide confidentiality; enable them only for a protocol that explicitly requires integrity-only protection.

### Use negotiated FFDHE in TLS 1.2

OpenSSL 4.0 supports RFC 7919 negotiated finite-field Diffie-Hellman ephemeral key exchange in TLS 1.2 (source batch `4.0.0`).

### Do not expect SSLv2 ClientHello or SSLv3 compatibility

OpenSSL 4.0 removes SSLv3 and the ability to receive an SSLv2-format ClientHello. No runtime compatibility option restores either handshake form.

### Re-enable deprecated EC only in compatibility builds

TLS curves deprecated by RFC 8422 and explicit EC curves are disabled at compile time by default in OpenSSL 4.0. Opt back in only for a deliberate legacy-compatibility build:

```sh
./Configure enable-tls-deprecated-ec enable-ec_explicit_curves
```

Use the `no-tls-deprecated-ec` configuration option to disable RFC 8422-deprecated TLS groups at runtime in OpenSSL 3.5 and newer.

## Post-quantum and specialized TLS

### Account for hybrid TLS defaults

The default supported-groups list includes and prefers hybrid post-quantum KEM groups and drops some practically unused groups (since 3.5.0). The default key shares are X25519MLKEM768 and X25519.

### Offer multiple key shares

OpenSSL can offer multiple TLS key shares and exposes finer control over key-establishment group configuration (since 3.5.0). Preserve the configured tuple semantics; see [security.md](security.md#tls-group-tuples-with-default-cve-2026-2673) before interpolating `DEFAULT` into a custom list.

### Use Encrypted Client Hello

OpenSSL 4.0 implements Encrypted Client Hello as standardized by RFC 9849. Treat ECH configuration, DNS publication, retry configuration, and client/server roles as one deployment unit.

### Use ShangMi and hybrid identifiers

OpenSSL 4.0 adds RFC 8998 `sm2sig_sm3` and the `curveSM2` key-exchange group, plus the post-quantum hybrid group `curveSM2MLKEM768`. Verify peer and policy support before placing them in production lists.

## Choosing a QUIC integration model

OpenSSL has two distinct QUIC integration paths:

- Use native QUIC `SSL` connection and stream objects when OpenSSL owns QUIC transport behavior.
- Use `SSL_set_quic_tls_cbs()` when an external QUIC implementation owns the record layer and packet processing while OpenSSL performs TLS handshakes.

OpenSSL 3.5's native QUIC API is not source-compatible with the BoringSSL-style callback API used by several other TLS libraries. Port the integration explicitly rather than assuming a drop-in relink.

### Server-side QUIC

OpenSSL 3.5 adds libssl support for QUIC servers, complementing the client support available earlier. The built-in client and server use the same external-stack TLS callback foundation described in source batch `3.5-guide`.

## Native QUIC streams

### Choose default or multi-stream mode before connecting

A QUIC connection begins in default-stream mode. The first `SSL_read()` waits for a peer-initiated stream, while the first `SSL_write()` creates a locally initiated stream. For new multi-stream applications, call `SSL_set_default_stream_mode()` with `SSL_DEFAULT_STREAM_MODE_NONE` before starting the connection, then use `SSL_new_stream()` and `SSL_accept_stream()`. The mode cannot change after connection initiation.

### Avoid the default-stream creation trap

Calling `SSL_new_stream()` or `SSL_accept_stream()` before a default stream is associated permanently prevents later default-stream creation. To accept extra streams while retaining default mode, also change the incoming-stream policy with `SSL_set_incoming_stream_policy()`.

### Configure method, role, and ALPN correctly

The OpenSSL 3.3 QUIC client uses `OSSL_QUIC_client_method()` or its thread-assisted variant, and ALPN is mandatory. The method fixes the endpoint role, so connect-state or accept-state setters cannot change it. Minimum and maximum protocol-version settings are ignored because the API always uses TLS 1.3.

### Work around the 3.5.0 accept edge

On OpenSSL 3.5.0, `SSL_accept()` on an object returned by `SSL_accept_connection()` does not advance the handshake and fails. Call `SSL_do_handshake()` on that object instead. Upgrade when possible rather than preserving this workaround indefinitely.

## QUIC BIO and blocking contracts

### Supply a nonblocking datagram BIO

QUIC network BIOs must have datagram semantics and always operate nonblockingly. Use `BIO_s_datagram()` for a UDP socket, `BIO_s_dgram_pair()` instead of a conventional BIO pair, or unidirectional `BIO_s_dgram_mem()`. `SSL_set_fd()` and its read/write variants automatically create a datagram BIO for a QUIC object.

### Implement custom QUIC BIOs completely

A custom QUIC BIO must implement nonblocking `BIO_sendmmsg()` and `BIO_recvmmsg()`. Also expose read and write poll descriptors if SSL-level blocking I/O is required. `BIO_f_buffer()` and `BIO_new_buffer_ssl_connect()` are incompatible with QUIC. `BIO_new_ssl_connect()` detects QUIC and selects a datagram socket automatically.

### Configure application blocking independently

The mandatory nonblocking network BIO does not determine `SSL_read()` and `SSL_write()` behavior. QUIC SSL-level I/O defaults to blocking; call `SSL_set_blocking_mode()` to choose nonblocking application behavior.

### Distinguish stream readiness from network readiness

For QUIC, `SSL_want_read()` and `SSL_ERROR_WANT_READ` mean the stream has no readable data. `SSL_want_write()` and `SSL_ERROR_WANT_WRITE` mean the stream's internal buffer is full. They do not indicate readiness of the network BIO. Poll the transport using QUIC network-interest and poll-descriptor APIs.

## QUIC event processing and polling

### Control event processing explicitly

QUIC SSL objects can disable implicit event processing so the application decides when protocol events are handled (since 3.3.0). When disabled, service events often enough to drive timers, handshakes, acknowledgements, and stream progress.

### Use limited nonblocking polling support

OpenSSL provides limited polling support for QUIC connection and stream objects without blocking (since 3.3.0). Keep network polling distinct from stream-level WANT states.

### Use thread-assisted timers carefully

`OSSL_QUIC_client_thread_method()` creates background assistance that services QUIC timeouts even when the application makes no SSL I/O calls. OpenSSL handles its internal locking, but the method does not make concurrent calls to the public SSL API safe; add application locking.

## QUIC flow control and stream termination

### Query idle timeout and stream capacity

Use the QUIC APIs added in OpenSSL 3.3 to configure the negotiated idle timeout and query how many additional streams the connection can currently create.

### Inspect write-buffer utilization

Query both the configured size and current utilization of a QUIC stream's write buffer for nonblocking flow control (since 3.3.0).

### Send data and FIN together

Use `SSL_write_ex2()` QUIC FIN support to send an end-of-stream condition together with the final data instead of issuing separate data and FIN operations (since 3.3.0).

### Half-close or reset explicitly

`SSL_stream_conclude()` sends a normal FIN for the sending half while leaving the receiving half usable. `SSL_stream_reset()` performs abnormal send-side termination. Query read and write stream state independently, inspect peer stream error codes, and use `SSL_get_conn_close_info()` for connection-close details.

## QUIC shutdown and diagnostics

### Emit qlog traces

QUIC connections can emit qlog traces for protocol-level diagnostics without an application-specific tracing layer (since 3.3.0).

### Choose strict or fast shutdown

RFC-conformant `SSL_shutdown()` can take an extended time. Use `SSL_shutdown_ex()` to attach a QUIC application error code and request faster shutdown when prompt process exit matters more than strict shutdown conformance.

### Recognize unsupported OpenSSL 3.3 features

OpenSSL 3.3 QUIC does not support libssl async operation, `SSL_MODE_AUTO_RETRY`, TLS record padding or fragmentation controls, `SSL_stateless()`, SRTP, TLS 1.3 early data, post-handshake client authentication, or CCM cipher suites. Readahead configuration is accepted only as a no-op. Check later-version documentation before assuming this exact limitation list remains current.

## External QUIC stacks

### Reuse OpenSSL TLS handshakes

Third-party QUIC implementations can replace the normal TLS record layer with QUIC-aware callbacks configured by `SSL_set_quic_tls_cbs()`. OpenSSL performs TLS handshakes while the external stack owns packet and transport processing. The built-in QUIC client and server use the same OpenSSL 3.5 API, which is covered by that release's LTS support.

### Preserve 0-RTT

The external-stack integration supports 0-RTT in OpenSSL 3.5, allowing an external QUIC implementation to retain early-data handshakes while OpenSSL supplies TLS processing.
