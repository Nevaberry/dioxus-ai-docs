# CEL and Policy Exceptions

## Extended CEL data sources

The specialized policy types can call Kyverno CEL libraries for live
Kubernetes resources, external HTTP APIs, admission-user parsing, cached
`GlobalContextEntry` data, parsed image references, and OCI registry metadata
(since 1.14.0).

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

Use these facilities for policy evaluation data. Apply the HTTP security
controls described in
[image-and-http-security.md](image-and-http-security.md) before enabling
outbound calls.

## Utility functions

The additional CEL utility surface added in 1.17.0 includes:

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

Use the hashing functions for MD5, SHA-1, or SHA-256 values; `math.round` for
numeric precision; `x509.decode` for PEM certificates; `random` for random
strings; `listObjToMap` for list transformation; the JSON and YAML functions
for parsing; and the time functions for current time, truncation, and cron
conversion.

CEL policies can also use the gzip library to work with gzip-compressed data
(since 1.18.0).

## Match conditions

Policy `matchConditions` can call Kyverno's extended CEL libraries (since
1.16.0). Kyverno evaluates these expressions itself. They are not translated
into admission webhook `matchConditions`, so their use does not change webhook
routing.

Use `matchConstraints` for Kubernetes resource selection and
`matchConditions` for contextual CEL selection before rule execution.

## Basic policy exceptions

CEL-first policy kinds can be exempted with
`policies.kyverno.io/PolicyException` (since 1.14.0). `policyRefs` identifies
the target policy, while `matchConditions` uses CEL to select exempt
resources:

```yaml
apiVersion: policies.kyverno.io/v1
kind: PolicyException
metadata:
  name: exclude-skipped-deployment
spec:
  policyRefs:
    - name: ivpol-report-background-sample
      kind: ImageValidatingPolicy
  matchConditions:
    - name: check-name
      expression: object.metadata.name == 'skipped-deployment'
```

## Exception-provided images and values

`PolicyException` can provide image patterns in `spec.images` and arbitrary
values in `spec.allowedValues` (since 1.16.0). A referenced policy consumes
the resolved data through `exceptions.allowedImages` or
`exceptions.allowedValues`.

```yaml
apiVersion: policies.kyverno.io/v1
kind: PolicyException
metadata:
  name: allow-ci-latest-images
  namespace: ci
spec:
  policyRefs:
    - name: restrict-image-tag
      kind: ValidatingPolicy
  images:
    - ghcr.io/kyverno/*:latest
  matchConditions:
    - expression: >-
        has(object.metadata.labels.team) &&
        object.metadata.labels.team == 'platform'
```

The corresponding policy expressions can test the supplied exception data:

```cel
string(container.image) in exceptions.allowedImages
capability in exceptions.allowedValues
```

This design bypasses only the listed image or value instead of exempting the
entire resource.

## Exception report results

`PolicyException.spec.reportResult` controls the result recorded when an
exception matches (since 1.16.0). The default result is `skip`; set `pass` to
record a pass:

```yaml
spec:
  reportResult: pass
```
