# Routing and Health Checks

## SPOP-native backends

HAProxy 3.1.0 implements SPOE as a mux and adds `mode spop`. SPOP backends can
use any load-balancing algorithm and share idle connections between threads;
existing SPOA agents remain compatible.

```haproxy
backend spoa_agents
    mode spop
    balance roundrobin
    server agent1 127.0.0.1:12345
```

## Dynamic retry counts

The `set-retries` action is available in `tcp-request` and `http-request`
rules since 3.1.0. It chooses a retry count for the current traffic rather than
fixing one value for the entire proxy.

```haproxy
http-request set-retries 0 if METH_POST
```

In 3.4.3, custom maximum retry counts and stream timeouts are initialized
correctly after backend selection. Rules that set them no longer lose their
values when the backend is assigned.

## HTTP health-check Host headers

Since 3.1.0, `option httpchk` supports a Host header directly. Stop encoding
the header through fake strings in the `httpchk` line.

## Health-gated server initialization

The 3.1.0 server `init-state` setting can hold a server down at startup or
after it leaves maintenance until its first health check succeeds. Use it to
avoid a window where an unverified server receives production traffic.

## Checks over pooled connections

Since 3.2.0, the server argument `check-reuse-pool` runs health checks over
idle pooled connections instead of creating a connection for each check. This
reduces connect and TLS handshake cost and supports reverse-HTTP permanent
connections. Ensure the application protocol can safely distinguish health
traffic on a reused connection.

## Reusable health-check sections

HAProxy 3.4.0 adds named `healthcheck` sections. A section can contain any
supported check type and its `http-check` or `tcp-check` actions. Servers in
one backend may select different definitions, and one definition can be reused
across backends.

```haproxy
healthcheck mycheck
    type httpchk
    http-check connect alpn h2
    http-check send meth HEAD uri /health ver HTTP/2 hdr Host www.example.com

backend webservers
    server web1 10.0.0.1:80 check healthcheck mycheck
```

## Strict connection caps

The 3.2.0 server argument `strict-maxconn` makes `maxconn` count open TCP
connections, not concurrent HTTP requests. Enable it for an upstream whose
contract imposes a hard connection limit, especially when multiplexing would
otherwise hide open connections.

## Default balancing changed

In 3.3.0, a backend without `balance` uses `random` instead of `roundrobin`.
The random policy samples two servers and chooses the less-loaded one. Add an
explicit `balance roundrobin` when the previous behavior is required.

Since 3.4.0, equal-concurrency candidates under `random` are also compared by
recent HTTP request rate. Large pools with many equally loaded servers may
therefore distribute traffic differently after a patch upgrade.

## Abort-on-close defaults

Backends in `mode http` enable `option abortonclose` by default from 3.3.0.
This stops work before an abandoned client request is sent upstream. The
option is also valid in frontends. State the opposite explicitly if upstream
processing must continue after the client disconnects.
