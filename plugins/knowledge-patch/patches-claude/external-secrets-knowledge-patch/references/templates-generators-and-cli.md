# Templates, Generators, and CLI

Use this reference for template evaluation, helper functions, certificate data,
credential generators, and local rendering workflows.

## Template evaluation and values

### Rendering template data and secrets (since 0.13.0)

A renderer for template data and secrets is available through `esoctl`; the
release action names the command `esoctl` rather than `render`. Use it to validate
rendered output without depending on an older command name.

### Non-standard delimiters (since 0.15.0)

Templates can select non-default delimiters. Use them when secret content or an
embedded template language conflicts with the ordinary delimiters.

### Native values (since 0.19.0)

Value-scoped processing preserves the original value instead of coercing it to a
string. Convert explicitly only where a downstream template operation requires a
string.

### Templated JSONPath (since 0.18.0)

`result.jsonpath` in `dataFrom` can itself be templated, so the extraction path can
be selected dynamically.

### Decoded templateFrom data (since 2.7.0)

Values loaded through `templateFrom` are decoded before use in templates. Avoid a
second decode that would corrupt already-decoded input.

### Mixed case and slice notation (since 2.7.0)

Generic target paths preserve mixed-case path components. The template parser also
resolves slice notation correctly.

## Template functions

### Certificate SAN extraction (since 2.2.0)

Use `certSANs` to extract subject alternative names from certificate input.

### Hexadecimal conversion (since 2.7.0)

Use `hexdec` to convert hexadecimal input to decimal during template rendering.

### Removed DNS lookup (since 2.3.0)

`getHostByName` is no longer available. Replace templates that depend on DNS
lookups with data supplied through an explicit, controlled input.

## Template output details

- Certificate-only PKCS#12 bundles, without a private key, are accepted from
  0.20.0.
- Secret templates can add finalizers to generated Secrets from 0.20.0.
- Source null-byte policy is configurable from 2.3.0.
- Environment is considered when selecting group variables from 0.18.0.

## Credential generators

### Quay (since 0.13.0)

Quay is available as a generator source.

### Grafana service accounts

The Grafana service-account generator arrived in 0.14.0. In-cluster integration
improved in 0.15.0, including passing the requested role through during account
creation. `SecondsToLive` became optional in 2.8.0, so callers need not provide an
explicit token lifetime.

### MFA tokens (since 0.18.0)

The MFA token generator has an optional length setting, and its length handling is
corrected. Omit length to use generator defaults.

### SSH keys

The SSH key generator arrived in 0.19.0 and gained ECDSA output in 1.1.0.

### Registry credentials

- ECR authorization-token generation accepts custom endpoints from 0.18.0 and
  resolves credentials through the AWS chain from 0.19.0.
- Cloudsmith registry credentials can be generated from 0.20.0.
- GitLab deploy-token generation is available from 2.8.0.

### STS session tokens

The `STSSessionToken` generator no longer supports JWT-token authentication from
0.19.0. Move generator configurations to another supported authentication route.

## Generator validation and bootstrap

- `generatorRef` validates `externalsecret_type` from 1.0.0; invalid references
  that previously passed admission are rejected.
- `esoctl` includes bootstrap-generator commands from 1.0.0.
- Cluster-generator processing is controlled by the Helm
  `processClusterGenerator` boolean from 0.20.0.

## Push templating

A `PushSecret` can use `template` and `templateFrom` to construct outgoing values
before `data[].match` or `dataTo` mappings run. For bulk expansion, the template is
applied first, followed by key conversion, matching, and rewriting. Consult the
PushSecret reference for conflict and bundle semantics.
