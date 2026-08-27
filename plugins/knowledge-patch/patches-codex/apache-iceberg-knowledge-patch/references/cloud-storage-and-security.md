# Cloud storage and security

Use this reference for object-store schemes, credentials, KMS integrations,
encryption, endpoints, proxies, and long-running `FileIO` behavior.

## Cross-provider encryption model

The table and REST specifications add encryption keys in 1.10.0. The API
represents table-metadata keys, and `KeyManagementClient` implementations are
available for AWS and GCP.

Usable table encryption expands in 1.11.0-guides:

- A Hive table property containing the table master-key ID activates
  encryption.
- Manifest lists are encrypted.
- Key-encryption keys can rotate automatically.
- `encryption.kms-type` selects AWS, Azure, or GCP KMS.
- Hive catalogs validate encrypted-table metadata integrity.

Preserve encryption metadata through catalog operations. Keep the master-key
identity, provider selection, manifest-list encryption, rotation process, and
metadata-integrity checks consistent.

## AWS

### S3 behavior

The REST specification documents the configuration for cross-region S3
access in 1.8.0.

The 1.11.0-guides batch adds:

- Configurable S3 chunked encoding.
- Proxy settings read from system properties or environment variables.
- Precedence for an explicitly configured credential provider.

Resolve proxy and credential-provider precedence explicitly in deployments
where environment settings may also be present.

### KMS

The AWS KMS client enables `RetryMode` in 1.8.0. In 1.11.0-guides, AWS adds
the `kms.endpoint` setting, allowing a non-default or controlled KMS endpoint.

Apply retry and endpoint settings to the intended KMS client, and ensure that
retries remain safe for the key-management operation.

### Credentials

AWS supports multiple storage-credential prefixes as of 1.10.0. This permits
separate credential scopes for different storage locations. Prefer an
explicitly configured provider when provided, following the later precedence
rule.

The AWS integration can write deletion vectors from 1.8.0; grant storage
permissions for vector files and their cleanup lifecycle, not only data and
manifest files.

## Azure

`ADLSFileIO` accepts WASB-scheme locations as of 1.8.0.

Azure accepts access-token authentication through `adls.token` in 1.10.0.
The 1.11.0-guides batch adds an Azure Key Vault `KeyManagementClient` and
custom token-credential providers.

Choose one effective token source and account for its lifetime. If a custom
provider is configured, test refresh and error propagation rather than
treating `adls.token` as an interchangeable static fallback.

## GCP

GCP supports multiple storage-credential prefixes in 1.10.0. That batch also
adds Google authentication and a BigQuery metastore catalog.

The 1.11.0-guides batch adds:

- BigQuery metastore service-account impersonation.
- `gcp.auth.credentials-key`.
- ETag conflict detection.

Keep the credentials key, impersonated service account, storage scope, and
metastore permissions aligned. Treat ETag conflicts as concurrent catalog
changes requiring refresh.

## Aliyun OSS

Aliyun OSS adds RRSA authentication in 1.11.0-guides. Configure the workload
identity relationship and avoid substituting long-lived static credentials
where RRSA is the intended authentication path.

## Scheduled storage-credential refresh

As of 1.11.0, long-running `S3FileIO` and `GCSFileIO` instances refresh held
storage credentials on a schedule.

Design services around refreshable credentials:

1. Keep the `FileIO` instance lifecycle long enough for scheduled refresh to
   operate where reuse is intended.
2. Ensure the underlying provider can issue replacement credentials.
3. Test refresh before expiry and behavior during provider failure.
4. Avoid caching extracted credentials separately beyond their validity.

## Provider configuration checklist

- Confirm the URI scheme and `FileIO` implementation, including WASB.
- Resolve credential-prefix routing for every storage location.
- Confirm explicit-provider, environment, and system-property precedence.
- Configure cross-region access, proxying, and S3 chunked encoding as needed.
- Select `encryption.kms-type` and the provider-specific KMS endpoint/client.
- Validate master-key identity, manifest-list encryption, and key rotation.
- Test Azure custom token refresh, GCP impersonation, and Aliyun RRSA.
- Exercise scheduled credential refresh in long-running AWS and GCP jobs.

