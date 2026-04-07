# Load Balancing & Services

New load balancing strategies, health checks, and service features since Traefik v3.1.

## New Load Balancing Strategies (v3.4/v3.6)

Beyond `wrr` (weighted round-robin), new strategies are available:

```yaml
http:
  services:
    my-service:
      loadBalancer:
        strategy: p2c # Power of Two Choices (v3.4)
        # strategy: leasttime  # Lowest response time (v3.6)
        # strategy: highestRandomWeight  # Probabilistic (v3.6)
        servers:
          - url: "http://backend1:8080"
          - url: "http://backend2:8080"
```

Note: `RoundRobin` is deprecated, use `wrr` instead.

---

## TCP & Passive Health Checks (v3.6)

```yaml
http:
  services:
    my-service:
      loadBalancer:
        healthCheck:
          # Active TCP health check (for non-HTTP)
          mode: tcp
          interval: "10s"
          timeout: "5s"
        passiveHealthCheck: # Observes real traffic patterns
          maxConsecutiveFailures: 3
          interval: "30s"
```

---

## Sticky Cookie Enhancements (v3.3/v3.4)

```yaml
http:
  services:
    my-service:
      loadBalancer:
        sticky:
          cookie:
            name: "my_cookie"
            path: "/api" # Custom cookie path (v3.3)
            domain: ".example.com" # Cookie domain (v3.4)
```

---

## Redis Rate Limiter (v3.4)

Distributed rate limiting backed by Redis, replacing the in-memory-only approach for multi-instance deployments.

```yaml
http:
  middlewares:
    rate-limit:
      rateLimit:
        average: 100
        burst: 50
        redis:
          endpoints:
            - "redis:6379"
```

---

## Fast Proxy Mode (v3.2)

Improves HTTP/1.1 performance with backends. Enabled at the `serversTransport` level:

```yaml
http:
  serversTransports:
    fast:
      fastProxy: {}
```
