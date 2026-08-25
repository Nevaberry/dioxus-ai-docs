# Certificates and Issuance

## Private keys, history, and renewal

### Rotation and history defaults

The private-key rotation default is `Always`; set
`spec.privateKey.rotationPolicy: Never` on a Certificate only when key
retention is required. The former `DefaultPrivateKeyRotationPolicyAlways`
feature gate is GA and cannot be disabled (`1.20`).

An omitted `spec.revisionHistoryLimit` defaults to `1`. Configure a larger
value when more historical CertificateRequests must be retained.

### Renewal calculations and policy

The 1.17 correction to `renewBeforePercentage` can move the renewal time for
existing Certificates. In 1.21, percentage renewal also works correctly for
durations longer than roughly three years; earlier calculations could reject
such Certificates or select the wrong time.

The Certificate API supports `renewalPolicies` alongside `renewBefore` and
`renewBeforePercentage` for more expressive scheduling (`1.21`). Avoid 1.21.0
when disabled renewal is used: `spec.renewal.policy: Disabled` can panic the
controller, and 1.21.1 fixes it.

Failed CertificateRequests use exponential backoff with a 32-hour default
maximum. Change it with
`--certificate-request-maximum-backoff-duration`, controller configuration, or:

```yaml
config:
  certificateRequestMaximumBackoffDuration: 8h
```

### ACME Renewal Information

Experimental RFC 9773 support behind `ACMEUseARI` queries an ACME server's
`renewalInfo` endpoint. This lets the CA recommend renewal windows, including
for mass revocation or CA key rollover.

## Keystores, output, and algorithms

### Literal keystore passwords

A Certificate can set `spec.keystores.jks.password` or
`spec.keystores.pkcs12.password` directly (`1.17`). Each is mutually exclusive
with its corresponding `passwordSecretRef`. A literal password satisfies
software compatibility requirements; it does not add keystore security.

```yaml
spec:
  secretName: example-tls
  issuerRef:
    name: example-issuer
  keystores:
    jks:
      create: true
      password: changeit
```

### Output and signature choices

Signature algorithms are selectable to meet a CA or consumer requirement
(`1.18`). `AdditionalCertificateOutputFormats` is GA and additional formats no
longer require a gate.

The `Modern2026` PKCS#12 profile uses AES-256 and SHA-256 KDFs rather than
legacy 3DES or RC2 and is compatible with FIPS 140-3 requirements (`1.21`).

RSA certificates with 3072-bit keys use SHA-384 and 4096-bit keys use SHA-512.
Verify consumer support if a large-key rotation begins failing.

### Large PEM inputs

From 1.18.3, larger PEM certificates and chains can be parsed, including leaf
certificates with many DNS names or other identities. Operators can also
configure PEM decoder size limits for certificates or keys beyond normal
limits (`1.20`).

## Names and constraints

`NameConstraints` became beta and enabled by default in 1.17. Use 1.17.4 or
later for URI constraints because earlier 1.17 releases copied permitted URI
domains into excluded URI domains in the CSR.

When `commonName` is an IP address, cert-manager places it in `ipAddresses`
rather than a DNS SAN (`1.18`). Trailing-dot DNS SANs rejected by 1.19.0 work
again from 1.19.1.

`OtherNames` is beta and enabled by default in 1.20. Ingress-like shim
controllers in 1.21 also convert `cert-manager.io/alt-names` and
`cert-manager.io/ip-sans` annotations into the generated Certificate.

## Issuance integrity and reconciliation

- While a Certificate is being deleted, its controller does not create a new
  CertificateRequest or Secret (`1.17`).
- From 1.18.5, an issuer response whose public key does not match the CSR is
  rejected before storage; issuance fails with backoff instead of looping.
- If an issuer returns a certificate that is already expired, the controller
  stops rather than entering an infinite reissuance loop (`1.21`).
- Changing Duration or `RenewBefore` on an Ingress or Gateway immediately
  updates its generated Certificate (`1.20`).
- The domain-qualified finalizer behavior is beta and enabled by default under
  `UseDomainQualifiedFinalizer` from 1.17, avoiding Kubernetes warnings.

## Querying Certificates by issuer

The CRDs expose `spec.issuerRef.group`, `spec.issuerRef.kind`, and
`spec.issuerRef.name` as selectable fields (`1.20`):

```console
kubectl get certificates --field-selector spec.issuerRef.name=example-issuer
```

Do not remain on 1.19.0: its CRD-level defaults for Certificate and
CertificateRequest issuer-reference group and kind can persist defaults and
cause unnecessary reissuance. Version 1.19.1 restores the earlier runtime
defaulting behavior.
