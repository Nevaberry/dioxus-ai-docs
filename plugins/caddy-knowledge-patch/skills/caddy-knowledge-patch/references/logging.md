# Logging

Logging configuration changes since Caddy 2.8.0.

## `log_append` Handler (2.8.0)

Adds custom fields to structured access logs. Replaces old `skip_log` for more flexible log control:

```
log_append X-Request-ID {header.X-Request-ID}
```

### Logging Request/Response Bodies (2.11.1)

Debug by logging request and response bodies:

```
log_append request_body {http.request.body_base64}
log_append response_body {http.response.body}
```

## Log Sampling (2.9.0)

Sample access logs to reduce volume in high-traffic environments:

```
{
    log {
        sampling {
            interval 1000
            first 100
            thereafter 100
        }
    }
}
```

- `interval` — sample window size (number of log entries)
- `first` — log the first N entries in each interval
- `thereafter` — log every Nth entry after `first` is exhausted

## Time-Rolling Logs (2.11.1)

Log rolling switched from lumberjack to timberjack library. New time-based rolling option:

```
log {
    output file /var/log/caddy/access.log {
        roll_time 24h
    }
}
```

## Log Rolling `zstd` Compression (2.11.2)

`roll_gzip` is deprecated. Use `roll_compression` with the compression algorithm:

```
log {
    output file /var/log/caddy/access.log {
        roll_compression zstd
    }
}
```
