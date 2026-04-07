# Providers & Observability

New providers and observability features since Traefik v3.1.

## Knative Provider (v3.6, experimental)

```yaml
experimental:
  knative: true
providers:
  knative:
    namespaces:
      - "serverless-apps"
```

---

## NGINX Ingress Provider (v3.5+)

Lets you use existing `ingress-nginx` annotations directly in Traefik for migration. No longer experimental as of v3.6.2.

```yaml
providers:
  kubernetesIngressNGINX: {}
```

---

## OTLP Logs (v3.3, experimental)

```yaml
experimental:
  otlpLogs: true
log:
  otlp: {}
accessLog:
  otlp: {}
```

---

## Trace Verbosity (v3.5)

Controls tracing span detail. Default changed to `minimal` (fewer spans).

```yaml
entryPoints:
  websecure:
    address: ":443"
    observability:
      traceVerbosity: detailed # or "minimal" (default)
```

Routers can override their entrypoint's verbosity.

---

## API & Dashboard Base Path (v3.3)

```yaml
api:
  dashboard: true
  basePath: "/custom-dashboard"
```

---

## Post-Quantum TLS (v3.5)

X25519MLKEM768 curve available for post-quantum-secure TLS:

```yaml
tls:
  options:
    default:
      curvePreferences:
        - X25519MLKEM768
        - X25519
```
