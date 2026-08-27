# QUIC, HTTP, and Networking

## QUIC handshake rules

Since 3.1.0, `quic-initial` rules run before the QUIC handshake completes.
Supported actions are `reject`, `accept`, `dgram-drop` for a silent drop, and
`send-retry`. Apply them to source filtering and early abuse prevention.

```haproxy
quic-initial dgram-drop if { src 192.0.2.0/24 }
```

## QUIC pacing and memory

In 3.2.0, choosing `quic-cc-algo` automatically enables transmit pacing and
`bbr` no longer needs experimental directives. Disable pacing with
`tune.quic.disable-tx-pacing` only after measurement.

QUIC upload streams may consume 90% of connection memory by default. Adjust
that share with `tune.quic.frontend.stream-data-ratio`, and optionally bound
global transmit-buffer memory with `tune.quic.frontend.max-tx-mem`.
`haproxy -vv` reports socket-owner and UDP GSO support needed for diagnosis.

HAProxy 3.4.0 also permits `quic-cc-algo` on `server`, so frontend and backend
congestion control may differ; that change was backported to 3.3. The newer
`tune.quic.fe.stream.max-total` caps requests over one connection, sends an
HTTP/3 GOAWAY at the limit, and closes after remaining transfers finish.

## Experimental HTTP/3 backends

HAProxy 3.3.0 can reach backend servers over HTTP/3 and QUIC by prefixing the
server address with `quic4@`. This is experimental, requires
`expose-experimental-directives`, and still requires normal backend TLS
verification.

```haproxy
global
    expose-experimental-directives

backend webservers
    server web1 quic4@172.16.0.11:443 check ssl verify required ca-file /etc/haproxy/ssl/myca.pem
```

Backend controls live under `tune.quic.be.*` for congestion control, idle
timeouts, glitch limits, streams, pacing, and UDP GSO. Bound process-wide
transmit memory with `tune.quic.mem.tx-max`.

## Experimental QMux over TCP

QMux in 3.4.0 carries QUIC frames over an ordered, reliable byte stream. It
allows HTTP/3 between HAProxy endpoints where UDP is unavailable. Enable
experimental directives and advertise `alpn h3` on the relevant TCP `bind` or
`server` line.

```haproxy
global
    expose-experimental-directives

backend webservers
    server web1 127.0.0.1:443 ssl verify none alpn h3,h2
```

## HTTP/2 overload controls

HAProxy 3.4.0 adds:

- `tune.h2.fe.max-frames-at-once` and
  `tune.h2.be.max-frames-at-once` to cap each processing batch;
- `tune.h2.fe.max-rst-at-once` to limit RST_STREAM work, where values 1–10
  mitigate attacks but very low values can hurt interactive and gRPC latency;
- `tune.h2.fe.max-total-streams` to recycle a connection after its lifetime
  stream count;
- `tune.streams-elasticity` to lower per-connection concurrency as frontend
  `maxconn` pressure rises;
- `rq-load` on `tune.h2.fe.max-concurrent-streams` for run-queue-based
  adjustment, plus `min` as its advertised concurrency floor.

The 3.4.0 `tune.h2.log-errors` chooses stream-scope, connection-only, or no
HTTP/2 error logs. The default is the most verbose `stream` scope.

## HTTP/1 glitch handling

Glitch detection covers the HTTP/1 multiplexer in 3.4.0. Configure
`tune.h1.fe.glitches-threshold` and `tune.h1.be.glitches-threshold` separately.
When threshold termination is enabled, HAProxy starts graceful close at 75%
of the threshold.

The earlier 3.2.0 global `tune.glitches.kill.cpu-usage` delays killing a
connection over its glitch threshold until CPU reaches a configured 0–100
percentage. Its default `0` kills at the threshold regardless of CPU load. A
nonzero value requires either `tune.h2.fe.glitches-threshold` or
`tune.quic.frontend.glitches-threshold`.

## Relaxed WebSocket parsing

Since 3.2.0, backend
`accept-unsafe-violations-in-http-request` and
`accept-unsafe-violations-in-http-response` also tolerate missing expected
WebSocket headers. Keep these compatibility relaxations scoped to backends
that require them.

## Retrying misdirected requests

The 3.2.0 `retry-on` directive accepts status `421`. Use it when a request can
be misdirected to an upstream that cannot serve the requested authority.

## Process-wide DNS family selection

`dns-accept-family` was introduced in 3.2.0 with `ipv4`, `ipv6`, and `auto`.
The `auto` mode probes IPv6 connectivity at boot and every 30 seconds. In
3.3.0, `auto` became the default, so IPv4 stays enabled while IPv6 is enabled
or disabled according to those probes. Set a family explicitly when network
policy must not change dynamically.

## Per-socket congestion control and TCP MD5

Since 3.3.0, the `cc` argument on `bind` and `server` selects the TCP
congestion-control algorithm for that listener or upstream. The `tcp-md5sig`
argument on both lines enables the TCP MD5 Signature Option used by many BGP
peers.

## Directional byte counts

HAProxy 3.3.0 defines byte direction precisely:

- `req.bytes_in` aliases `bytes_in` for client-to-HAProxy bytes;
- `req.bytes_out` counts HAProxy-to-server bytes;
- `res.bytes_in` aliases `bytes_out` for server-to-HAProxy bytes;
- `res.bytes_out` counts HAProxy-to-client bytes.

Do not infer direction from the request/response prefix alone.

## Uniform HTTP version fetches

In 3.4.0, `req.ver` and `res.ver` consistently return `major.minor` for
HTTP/1, HTTP/2, and HTTP/3. `capture.req.ver` and `capture.res.ver` return
`HTTP/major.minor` for all three.
