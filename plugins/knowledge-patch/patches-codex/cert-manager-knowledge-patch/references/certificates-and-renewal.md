# Certificates and Renewal

## Private keys and signing

### Rotation defaults to `Always` `(upgrade-1.18)`

`Certificate.spec.privateKey.rotationPolicy` defaults to `Always` rather than `Never`. Before upgrading, explicitly set `Never` on Certificates whose consumers cannot tolerate key rotation:

```yaml
spec:
  privateKey:
    rotationPolicy: Never
```

### Rotation feature gate is gone `(1.20)`

`DefaultPrivateKeyRotationPolicyAlways` is GA and cannot be disabled. Control behavior with each Certificate's `rotationPolicy`.

### RSA hash selection `(upgrade-1.17)`

RSA certificates with 3072-bit keys use SHA-384, and those with 4096-bit keys use SHA-512. If rotation breaks a consumer, verify its support for the stronger hash.

### Signature algorithm selection `(1.18)`

Select a signature algorithm when a CA or relying consumer requires a particular algorithm.

## Renewal scheduling and retries

### Corrected percentage calculations `(1.17)`

The `renewBeforePercentage` calculation follows its specification, so an upgrade can change renewal time for Certificates that use it.

### Long-duration percentages `(1.21)`

`renewBeforePercentage` works correctly for durations longer than approximately three years. Earlier behavior could reject such Certificates or compute the wrong renewal time.

### Renewal policies `(1.21)`

The Certificate API adds `renewalPolicies` for expressive scheduling alongside `renewBefore` and `renewBeforePercentage`.

### Disabled renewal correction `(1.21.1)`

In 1.21.0, `spec.renewal.policy: Disabled` can panic the controller. Upgrade to 1.21.1 or later when using disabled renewal.

### CertificateRequest retry ceiling `(1.21)`

Failed CertificateRequests use exponential backoff capped at 32 hours by default. Change the maximum with `--certificate-request-maximum-backoff-duration`, controller configuration, or Helm:

```yaml
config:
  certificateRequestMaximumBackoffDuration: 8h
```

### Revision history `(upgrade-1.18)`

`Certificate.spec.revisionHistoryLimit` defaults to `1` rather than `nil`; omitted fields adopt the new limit after upgrade.

## Keystores and output formats

### Literal keystore passwords `(1.17)`

`spec.keystores.jks.password` and `spec.keystores.pkcs12.password` accept literals. Each is mutually exclusive with its corresponding `passwordSecretRef`. A literal supports software that insists on a password but does not strengthen keystore security.

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: example
spec:
  secretName: example-tls
  issuerRef:
    name: example-issuer
  keystores:
    jks:
      create: true
      password: changeit
  dnsNames:
    - example.com
```

### Additional outputs are GA `(1.18)`

Additional certificate output formats are always enabled and no longer need the `AdditionalCertificateOutputFormats` feature gate.

### FIPS-compatible PKCS#12 `(1.21)`

The `Modern2026` PKCS#12 profile uses AES-256 and SHA-256 KDFs instead of legacy 3DES or RC2 and is compatible with FIPS 140-3 requirements.

## Names, constraints, and validity

### Name constraints defaults `(1.17)`

`NameConstraints` is beta and enabled by default, enabling CA certificate name constraints. Require 1.17.4 or later on that minor branch: earlier 1.17 releases copied permitted URI domains into excluded URI domains in CSRs.

### IP common names `(1.18)`

When `commonName` is an IP address, cert-manager places it in `ipAddresses` instead of the DNS SAN list.

### OtherNames `(1.20)`

The `OtherNames` feature is beta and enabled by default.

### Large PEM objects `(1.18)` `(1.20)`

Since 1.18.3, cert-manager parses larger PEM certificates and chains, including leaf certificates with many identities. Operators can also configure PEM decoding size limits when certificates or keys exceed normal decoder limits.

## Issuance safety

### No new children during deletion `(1.17)`

While a Certificate is being deleted, its controller does not create new CertificateRequest or Secret objects.

### Mismatched issuer responses `(1.18)`

Since 1.18.5, a certificate whose public key does not match its CSR is rejected before storage. Issuance backs off instead of entering an infinite reissuance loop.

### Already-expired issuer responses `(1.21)`

An issuer response containing an already-expired certificate stops without entering an infinite reissuance loop.

### Issuer-reference default regression `(1.19)`

CRD defaults added in 1.19.0 for Certificate and CertificateRequest issuer-reference group and kind could force unnecessary reissuance. They were reverted in 1.19.1; use 1.19.1 or later so omitted fields retain the earlier runtime-default behavior instead of being persisted as API defaults.

### Trailing-dot DNS SANs `(1.19)`

Version 1.19.0 rejected trailing-dot DNS names in X.509 SANs after a dependency change. Version 1.19.1 restores them.
