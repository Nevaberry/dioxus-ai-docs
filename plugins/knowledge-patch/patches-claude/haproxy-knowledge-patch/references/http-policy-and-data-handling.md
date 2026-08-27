# HTTP Policy and Data Handling

## Compression thresholds and filters

### Minimum body sizes (since 3.2.0)

Request and response compression can skip bodies below a configured byte
size. The response form introduced with the shared filter was:

```haproxy
filter compression
compression direction response
compression minsize-res 256
```

### Split request and response filters (since 3.4.0)

Request and response compression use separate `filter comp-req` and
`filter comp-res` filters instead of the shared compression filter and its
direction setting. The old `compression-direction` directive is deprecated.

```haproxy
backend webservers
    filter comp-res
    compression algo gzip
    compression type text/html text/plain application/json
```

`filter-sequence` controls execution order independently of declaration order.
Any configured filter omitted from the sequence is skipped, allowing
order-sensitive combinations such as compression and bandwidth limiting to be
reordered or temporarily disabled without removing their declarations.

## Request and response actions

### Delaying processing (since 3.2.0)

The `pause` policy action delays request or response processing by either a
fixed millisecond timeout or a sample expression. It can, for example, slow
rate-limit offenders.

```haproxy
http-request pause 250
http-response pause 250
```

### Relaxed WebSocket parsing (since 3.2.0)

The backend directives `accept-unsafe-violations-in-http-request` and
`accept-unsafe-violations-in-http-response` also tolerate missing expected
WebSocket headers.

## HTTP/2 and HTTP/1 limits

### Frame, reset, and stream controls (since 3.4.0)

- `tune.h2.fe.max-frames-at-once` and `tune.h2.be.max-frames-at-once` cap how
  many incoming frames are processed together.
- `tune.h2.fe.max-rst-at-once` separately limits RST_STREAM processing.
  Values from 1 to 10 mitigate RST attacks, although very low values can add
  latency to interactive or gRPC traffic.
- `tune.h2.fe.max-total-streams` recycles an incoming connection after a
  lifetime stream limit.
- `tune.streams-elasticity` reduces per-connection stream concurrency as the
  frontend approaches `maxconn`.
- `tune.h2.fe.max-concurrent-streams` accepts `rq-load` for run-queue-based
  adjustment and `min` for its advertised concurrency floor.

### HTTP/1 glitch handling (since 3.4.0)

Glitch detection covers the HTTP/1 multiplexer. Configure frontend and backend
thresholds with `tune.h1.fe.glitches-threshold` and
`tune.h1.be.glitches-threshold`. When threshold-based termination is enabled,
HAProxy begins a graceful close at 75% of the threshold instead of waiting for
the connection to reach the limit.

## HTTP validation changes

### Restricted server-name headers (since 3.3.0)

`http-send-name-header` cannot target `connection`, `content-length`, `host`,
or `transfer-encoding`, because replacing those fields would produce an
invalid HTTP request.

### Strict ACL match types (since 3.3.0)

An ACL cannot specify multiple match types after `-m`. Where HAProxy
previously used the final type silently, configuration now fails. Ambiguous
combinations such as `path_beg -m reg` also warn.

## Samples and converters

### Connection, TLS, counter, and date samples (since 3.2.0)

- `bc_reused` reports whether a transfer reused a backend connection.
- `req.ssl_cipherlist`, `req.ssl_keyshare_groups`, `req.ssl_sigalgs`, and
  `req.ssl_supported_groups` expose binary TLS ClientHello capabilities.
- `sc_key(<ctr>)` returns a tracked-counter key.
- `table_clr_gpc(<idx>[,<table>])` and
  `table_inc_gpc(<idx>[,<table>])` mutate a general-purpose counter and return
  its previous or new value, respectively.
- `accept_date` and `request_date` fall back to the session date when no stream
  exists, including during an early TLS-handshake failure.

### Directional byte counts (since 3.3.0)

- `req.bytes_in` aliases `bytes_in` and counts bytes received from the client.
- `req.bytes_out` counts bytes sent to the server.
- `res.bytes_in` aliases `bytes_out` and counts bytes received from the server.
- `res.bytes_out` counts bytes sent to the client.

### Binary and authenticated-encryption converters (since 3.3.0)

`base2` renders every input byte as eight binary digits. `le2dec` renders
little-endian binary chunks as unsigned decimal integers. `aes_gcm_enc` and
`aes_gcm_dec` accept an optional AAD argument for authenticated additional
data.

### Uniform HTTP versions (since 3.4.0)

`req.ver` and `res.ver` consistently return `major.minor` for HTTP/1, HTTP/2,
and HTTP/3. `capture.req.ver` and `capture.res.ver` consistently return
`HTTP/major.minor`.

### Timeout, TLS, and thread samples (since 3.4.0)

- `cur_connect_timeout`, `cur_queue_timeout`, and `cur_tarpit_timeout` expose
  active stream timeouts in milliseconds.
- `fe_tarpit_timeout` exposes the configured frontend tarpit timeout.
- `ssl_fc_crtname` returns the selected incoming certificate name.
- `tgroup` returns the calling thread group's zero-based position.

### Cryptographic and existence converters (since 3.4.0)

`jwt_decrypt_cert`, `jwt_decrypt_secret`, and `jwt_decrypt_jwk` decrypt JWT
input with a certificate, a base64-encoded secret, or a JSON Web Key,
respectively. `aes_cbc_enc` and `aes_cbc_dec` encrypt or decrypt raw bytes with
AES-128/192/256-CBC according to their bits argument. `fe_exists` reports
whether its input names a configured frontend.

### Stricter Protobuf decoding (since 3.4.3)

Protobuf field lookup no longer permits nested-path bypasses, and deprecated
Protobuf group wire types are rejected. Inputs that relied on either behavior
fail conversion instead of being accepted ambiguously.
