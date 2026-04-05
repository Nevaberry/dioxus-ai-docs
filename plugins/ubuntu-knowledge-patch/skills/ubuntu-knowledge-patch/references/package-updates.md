# Package Updates — Ubuntu 25.10

## Valkey / Redis Compatibility Break

Redis is updated to 8.0. The `valkey-redis-compat` compatibility package is **removed** — Valkey is no longer a transparent drop-in for Redis.

### Migration Path

Swap from Redis to Valkey **before** upgrading to 25.10. After the upgrade, the compatibility shim is gone and applications using Redis client libraries will not automatically connect to Valkey.

Choose one:
1. **Migrate to Valkey fully** — update connection strings, client libraries, and configs to use Valkey natively
2. **Stay on Redis 8.0** — use the updated Redis packages directly (note: Redis 8.0 has its own breaking changes)

## Nginx 1.28

Key improvements:
- **HTTP/3 and QUIC** enhancements — improved performance for HTTP/3 connections
- **SSL certificate caching** — reduced overhead for TLS handshakes on high-traffic servers

## Container Runtimes

| Package | Version |
|---------|---------|
| Containerd | 2.1.3 |
| Docker | 28.2 |

## Zig 0.14.1

Zig is available in Ubuntu repositories for the first time:

```bash
apt install zig
zig version # 0.14.1
```
