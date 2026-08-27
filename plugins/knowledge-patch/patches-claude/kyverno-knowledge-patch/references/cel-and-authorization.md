# CEL Libraries and Service Authorization

## Extended Kyverno Libraries

The specialized policy APIs add CEL integrations for live Kubernetes
resources, external HTTP APIs, admission-user parsing, cached
`GlobalContextEntry` data, parsed image references, and OCI registry metadata
(since 1.14.0).

Representative calls include:

```text
resource.Get("v1", "configmaps", "default", "my-config")
resource.List("apps/v1", "deployments", "default").items
http.Send("GET", "https://api.example.com/data", {}).body
http.Post("https://audit.api/log", {"kind": object.kind}, {"Content-Type": "application/json"}).logged == true
parseServiceAccount(request.userInfo.username)
globalcontext.Get("allowed-registries", "").registries
image("ghcr.io/company/app:v1.2.3").containsDigest()
imagedata.Get("nginx:1.21").config.architecture
```

These functions introduce dependencies that plain Kubernetes CEL does not
have. Account for Kyverno RBAC, network access, registry reachability, cache
contents, and the difference between admission and offline evaluation.

## Libraries in Match Conditions

Since 1.16.0, policy `matchConditions` may call Kyverno's extended CEL
libraries. This allows context-aware selection before rule execution.

Kyverno evaluates these expressions itself. It does not translate them into
admission webhook `matchConditions`, so using a custom function there does not
alter which requests Kubernetes routes to the webhook.

## Utility Functions

Kyverno 1.17.0 adds hashing, numeric rounding, X.509 decoding, random-string
generation, list-to-map conversion, JSON and YAML parsing, and time helpers:

```cel
md5(value)
sha1(value)
sha256(value)
math.round(value, precision)
x509.decode(pem)
random()
random(pattern)
listObjToMap(list1, list2, keyField, valueField)
json.unmarshal(jsonString)
yaml.parse(yamlString)
time.now()
time.truncate(timestamp, duration)
time.toCron(timestamp)
```

Kyverno 1.18.0 also provides a gzip CEL library for expressions that need to
work with gzip-compressed data.

Treat generated random values carefully in mutation or generation policies:
consider whether reevaluation must be deterministic and idempotent. Treat
parsers, certificate decoding, and decompression as error-producing operations
and define the desired failure behavior.

## Hardened HTTP Execution

Kyverno 1.18.0 hardens outbound HTTP calls from CEL:

- configurable address allowlists and blocklists constrain destinations;
- unsafe destinations such as loopback and metadata services are blocked by
  default;
- namespaced policies have HTTP disabled by default and require explicit
  configuration flags to enable it;
- outbound requests use a separately scoped token rather than a token capable
  of impersonating Kyverno controllers.

Do not assume an expression that made arbitrary HTTP calls in an earlier
configuration will continue to reach the same address. Configure only the
required destinations, preserve the namespaced default unless the call is
necessary, and test failure behavior when a destination is denied.

## Envoy and HTTP Authorization

The Kyverno Authz Server evaluates Kyverno policies at a service edge (since
1.16.0). It can run as the authorization endpoint for Envoy's External
Authorization filter or as a standalone HTTP authorization service.

The companion Go SDK can:

- load and compile policies;
- evaluate incoming requests;
- return structured allow/deny results;
- integrate optional metrics or hooks.

This supports gateways, sidecars, and application middleware without forcing
each integration to reproduce the policy evaluation engine. By 1.18.0,
`kyverno apply` and `kyverno test` also support HTTP and Envoy authorization
policies for pre-deployment evaluation.
