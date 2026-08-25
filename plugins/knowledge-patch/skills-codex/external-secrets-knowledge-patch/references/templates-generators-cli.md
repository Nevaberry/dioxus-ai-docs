# Templates, generators, and CLI

Read this reference when rendering templates, choosing generators, using
dynamic targets, or debugging `esoctl` output.

## Template evaluation and values

### Custom delimiters

Templates can use non-standard delimiters (since 0.15.0). Change delimiters
when secret content or an embedded template language collides with the default
Go-template delimiters, and keep the chosen delimiters consistent across
inline templates and imported fragments.

### Native values

Value-scoped processing preserves native values rather than always coercing
them to strings (since 0.19.0). Convert deliberately at the boundary required by
the target, template function, or serialized Kubernetes Secret.

### Dynamic JSONPath

`result.jsonpath` is templatable in `dataFrom` calls (since 0.18.0). Treat both
the rendered path and the selected data as inputs: validate the path after
template expansion and define behavior for an empty or missing match.

### Certificate SANs

The `certSANs` template function extracts subject alternative names from
certificates (since 2.2.0). It complements certificate-only PKCS#12 support;
do not assume a private key is present merely because certificate data parsed.

### Hexadecimal conversion

`hexdec` converts hexadecimal input to decimal during rendering (since 2.7.0).
Use it only after confirming whether the input includes prefixes, signs, or
values outside the consumer's integer range.

### Slice notation and generic target paths

The parser resolves slice notation correctly (since 2.7.0). Generic target
paths also preserve mixed-case components instead of changing their case
(since 2.7.0). Keep case-sensitive API field paths exactly as required by the
target resource.

### Removed DNS lookup

`getHostByName` was removed in 2.3.0. Templates must not perform DNS lookup
through that function; provide resolved data explicitly or move lookup logic to
an authorized component outside the template renderer.

## Template data sources and output metadata

### Decoded templateFrom values

Values loaded with `templateFrom` are decoded before template use (since
2.7.0). Avoid a second unconditional decode step in templates migrated from
older behavior.

### Template metadata

Defining labels or annotations under `target.template.metadata` replaces
implicit copying from the `ExternalSecret`. Empty maps intentionally suppress
copying:

```yaml
spec:
  target:
    template:
      metadata:
        labels: {}
        annotations: {}
```

Templates may add finalizers to generated Secrets (since 0.20.0). Target
`objectMeta` and `ownerReferences` propagate to generated target resources
(since 2.3.0); review the combined ownership and deletion behavior.

### Dynamic targets

ExternalSecret sources can select their targets dynamically (since 1.0.0).
Validate the final target path, resource type, namespace, ownership, and RBAC
after all template and dynamic-target processing.

## Credential and token generators

### MFA token generator

An MFA token generator is available (since 0.18.0). Its length option is
optional, and length handling was corrected in that release. Set a length only
when the consuming system requires a specific value.

### SSH key generator

The SSH key generator was added in 0.19.0 and supports ECDSA keys since 1.1.0.
Choose the algorithm and parameters to match the client and server policy.

### Grafana service-account generator

Grafana service-account credential generation is available since 0.14.0.
In-cluster operation and requested-role pass-through improved in 0.15.0.
`SecondsToLive` is optional since 2.8.0.

### Registry credential generators

- Quay is available as a generator source (since 0.13.0).
- Cloudsmith can generate container-registry authentication credentials (since
  0.20.0).
- `ECRAuthorizationToken` can use custom ECR endpoints (since 0.18.0) and
  resolves credentials through the AWS credential chain (restored in 0.19.0).

### GitLab deploy tokens

A GitLab deploy-token generator is available (since 2.8.0). Scope its generated
token to the repositories, registries, and actions actually required.

### STS session-token authentication removal

The `STSSessionToken` generator removed JWT-token authentication in 0.19.0.
Migrate generator resources to another supported authentication path.

### Generator validation

`generatorRef` validates `externalsecret_type` (since 1.0.0). Invalid references
that previously reached reconciliation may now be rejected at admission.

## CLI rendering and bootstrap

### Template renderer

The CLI renderer for template data and secrets is named `esoctl`, not `render`
(since 0.13.0). Use `esoctl` when testing how data and secrets render, and avoid
documenting `render` as the executable name.

### Bootstrap generators

`esoctl` includes commands for bootstrap generators (since 1.0.0). Use CLI
rendering and bootstrap commands to inspect generated material before applying
resources, while keeping sensitive output out of shell history and logs.

## Review checklist

- Confirm delimiters, decode steps, value types, case, and slice expressions.
- Validate every dynamic JSONPath and target after rendering.
- Check generator authentication separately from provider authentication.
- Treat rendered secret values, bootstrap output, tokens, and private keys as
  sensitive even in local tests.
- Re-run admission validation after changing generator references or API
  versions.
