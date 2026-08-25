# Issuers, Integrations, and API Clients

## Cainjector and CA bundle rotation

The CA bundle merge behavior evolved by release:

- In 1.17, opt in with `CAInjectorMerging` to append a new CA certificate
  instead of replacing the bundle, preserving overlap during rotation.
- In 1.19, the gate is beta and enabled by default; explicitly disable it only
  when replacement semantics are required.
- In 1.21, merging is GA and unconditional. The gate can no longer restore
  replacement semantics. Cainjector also always uses server-side apply, and
  the `ServerSideApply` feature gate is deprecated.

Cainjector's `--ignore-namespaces` flag excludes named namespaces while
watching Secrets for CA injection (`1.21`).

## Vault issuers

Vault issuers can set the TLS server name used to validate the Vault server's
certificate (`1.18`). From 1.20, generated ServiceAccount tokens include the
Vault server address in their default audiences.

In 1.21, Vault can authenticate through IRSA, EKS Pod Identity, or ambient
EC2/ECS credentials instead of a long-lived AWS Secret.

Issuer validation rejects `..` parent-traversal segments in `spec.vault.path`
and authentication mount paths rather than letting path joining resolve them
(`1.21`).

## Venafi issuers

Username/password authentication can use a custom client ID instead of the
fixed default (`1.17`). In 1.20, the
`venafi.cert-manager.io/custom-fields` annotation on an Issuer or ClusterIssuer
provides base custom fields; Certificate values can override or append them.

From 1.21, invalid OAuth credentials use the `AuthFailed` condition reason so
they can be distinguished from transient failures, and PANW NGTS is supported
as a backend.

## Azure DNS issuers

AzureDNS supports explicit `tenantID` selection when managed identities are
used with service principals (`1.17`). For private zones, set the 1.20
`zoneType` field to `AzurePrivateZone`.

## Issuer readiness

DNS issuer credential Secrets are validated before an issuer becomes Ready
(`1.21`). Secret misconfiguration is therefore surfaced instead of silently
accepted. Version 1.21.1 also requeues an ACME DNS-01 issuer after a previously
missing referenced Secret is created; 1.21.0 can remain stuck at
`Ready=False`, reason `InvalidSolver`.

## Kubernetes API ergonomics

`Issuer` and `ClusterIssuer` have the short names `iss` and `ciss` (`1.18`):

```console
kubectl get iss
kubectl get ciss
```

Generated apply-configuration types allow clients to build type-safe
server-side apply requests for cert-manager resources instead of unstructured
payloads (`1.19`).

The 1.20 CRDs make `spec.issuerRef.group`, `spec.issuerRef.kind`, and
`spec.issuerRef.name` field-selectable. The deprecated `ObjectReference` API
type is removed in 1.21; migrate integrations that still import or emit it.
