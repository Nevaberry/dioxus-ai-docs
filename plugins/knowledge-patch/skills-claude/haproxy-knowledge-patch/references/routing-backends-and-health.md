# Routing, Backends, and Health

## Backend protocols and balancing

### SPOP-native backends (since 3.1.0)

SPOE is implemented as a mux and adds the `mode spop` backend mode. SPOP
backends can use any load-balancing algorithm and share idle connections
between threads. Existing SPOA agents remain compatible.

```haproxy
backend spoa_agents
    mode spop
    balance roundrobin
    server agent1 127.0.0.1:12345
```

### Random is the default (since 3.3.0)

A backend without an explicit `balance` directive uses `random` instead of
`roundrobin`. The random policy uses a power-of-two choice: it samples two
servers and selects the less-loaded one. Configure `balance roundrobin` to
retain the former behavior.

### Random tie-breaking (since 3.4.0)

When the two random candidates have equal concurrent-connection counts,
HAProxy also compares their recent HTTP request rates. This changes
distribution in large pools where many servers previously appeared equally
loaded.

## Retry and stream behavior

### Dynamic retry counts (since 3.1.0)

The `set-retries` action is available in `tcp-request` and `http-request`
rules, allowing runtime selection of the retry count for a particular
application path or client.

```haproxy
http-request set-retries 0 if METH_POST
```

### Retrying status 421 (since 3.2.0)

`retry-on` accepts HTTP status `421`, allowing a request misdirected to an
incapable backend server to be retried.

### Abort-on-close defaults (since 3.3.0)

Backends in `mode http` enable `option abortonclose` by default. This allows
work to stop before an abandoned client request is sent to a server. The
option is also valid in a frontend.

### Stream settings after backend selection (since 3.4.3)

Custom stream timeouts and maximum retry counts are initialized correctly
when selecting a backend. Rules that set those values no longer lose their
intended behavior during backend assignment.

## Server limits and pools

### Strict connection caps (since 3.2.0)

The server argument `strict-maxconn` makes `maxconn` count open TCP
connections rather than concurrent HTTP requests. Use it when a backend has a
hard connection limit.

### Health checks on pooled connections (since 3.2.0)

The server argument `check-reuse-pool` performs health checks over idle pooled
connections rather than opening new ones. This reduces connection and TLS
handshake overhead and supports reverse-HTTP permanent connections.

### Shared idle pools (since 3.4.0)

The global `tune.idle-pool.shared` setting controls cross-thread sharing of
idle server connections:

- `on` shares within a thread group.
- `full` shares across all threads.
- `off` disables sharing for debugging.

It supersedes and deprecates `tune.takeover-other-tg-connections`.

## Health checks

### Host headers in legacy HTTP checks (since 3.1.0)

`option httpchk` supports a Host header directly. A fake string in the
`httpchk` line is no longer needed to encode that header.

### Health-gated server initialization (since 3.1.0)

The server `init-state` setting can keep a server down at startup or after it
leaves maintenance until its first health check succeeds.

### Reusable health-check sections (since 3.4.0)

A named `healthcheck` section can hold any supported check type and its
`http-check` or `tcp-check` actions. A server selects it with the
`healthcheck` argument. Different servers in one backend can therefore use
different checks, and definitions can be reused across backends.

```haproxy
healthcheck mycheck
    type httpchk
    http-check connect alpn h2
    http-check send meth HEAD uri /health ver HTTP/2 hdr Host www.example.com

backend webservers
    server web1 10.0.0.1:80 check healthcheck mycheck
```

## Runtime-created backends

### Creation and publication (since 3.4.0)

The Runtime API can add, publish, unpublish, and delete complete backends
without a reload. A backend is unavailable for routing until published.
Disabled or unpublished backends selected by `use_backend` or
`default_backend` are skipped unless `force-be-switch` is set.

```text
add backend test-backend from mydefaults mode http
add server test-backend/server1 127.0.0.1:3000 check
enable server test-backend/server1
enable health test-backend/server1
publish backend test-backend
```

For safe removal, put each server into maintenance, wait for `srv-removable`,
and delete it. Then unpublish the backend, wait for `be-removable`, and delete
the backend.

Named `defaults` sections remain in memory for dynamic creation. A deployment
that does not use dynamic backends can release that memory with the global
`tune.defaults.purge` directive.
