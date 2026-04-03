# Server Options

Global server configuration options added since Caddy 2.8.0.

## Custom `Server` Header (2.11.1)

Customize the `Server` response header value:

```
{
    servers {
        name myserver
    }
}
```

## `keepalive_idle` and `keepalive_count` (2.11.1)

Control TCP keepalive behavior:

```
{
    servers {
        keepalive_idle 60s
        keepalive_count 4
    }
}
```

- `keepalive_idle` — time before first keepalive probe
- `keepalive_count` — number of probes before dropping connection

## `trusted_proxies_unix` (2.11.1)

Trust `X-Forwarded-*` headers from unix socket connections:

```
{
    servers {
        trusted_proxies_unix
    }
}
```

## `observe_catchall_hosts` Metrics (2.11.1)

Include catchall (`:80`, `:443`) hosts in per-host metrics:

```
{
    metrics {
        per_host
        observe_catchall_hosts
    }
}
```
