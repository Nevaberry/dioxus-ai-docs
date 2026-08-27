# Issuers and External Providers

## Vault issuers

### TLS server-name validation `(1.18)`

Configure the server name used to validate the certificate presented by the Vault server when it differs from the connection address.

### Service-account token audiences `(1.20)`

Service-account tokens generated for Vault issuers include the Vault server address among their default audiences.

### AWS IAM authentication `(1.21)`

Vault issuers can authenticate with AWS identity from IRSA, EKS Pod Identity, or ambient EC2/ECS credentials instead of a long-lived AWS Secret.

### Path traversal rejection `(1.21)`

Validation rejects `..` segments in `spec.vault.path` and authentication mount paths. Do not depend on path joining to resolve parent traversal.

## Venafi issuers

### Custom client IDs `(1.17)`

Venafi username/password authentication can use a customized client ID instead of the fixed default.

### Layered custom fields `(1.20)`

The `venafi.cert-manager.io/custom-fields` annotation on an Issuer or ClusterIssuer supplies base custom fields. Certificate-level values can override or append to that base.

### Authentication conditions and backends `(1.21)`

Venafi issuers use condition reason `AuthFailed` to distinguish invalid OAuth credentials from transient failures. PANW NGTS is supported as a backend.

## Azure DNS issuers

### Managed-identity tenant selection `(1.17)`

The AzureDNS provider accepts `tenantID` when managed identities are used with service principals, allowing explicit tenant choice in multi-tenant environments.

### Private zones `(1.20)`

The Azure DNS-01 solver supports private zones through `zoneType: AzurePrivateZone`.

## DNS issuer readiness

### Validate Secrets before Ready `(1.21)`

DNS issuer credentials are validated before an issuer is marked ready, surfacing Secret misconfiguration rather than accepting it silently.

### Recover after a missing Secret `(1.21.1)`

When a referenced ACME DNS-01 solver Secret is initially missing, 1.21.1 lets an Issuer or ClusterIssuer recover from `Ready=False` with reason `InvalidSolver` after the Secret is created. Version 1.21.0 can stay stuck.

## Issuer API ergonomics

### Short names `(1.18)`

Issuer and ClusterIssuer have short names `iss` and `ciss`:

```console
kubectl get iss
kubectl get ciss
```

### Field-selectable references `(1.20)`

CRDs expose `.spec.issuerRef.group`, `.spec.issuerRef.kind`, and `.spec.issuerRef.name` as selectable fields:

```console
kubectl get certificates --field-selector spec.issuerRef.name=example-issuer
```

### Type-safe apply clients `(1.19)`

Generated apply-configuration types let clients construct type-safe server-side apply requests for cert-manager resources instead of unstructured payloads.

### Removed ObjectReference `(1.21)`

The deprecated `ObjectReference` API type is removed. Migrate integrations that still compile against or emit it before upgrading.
