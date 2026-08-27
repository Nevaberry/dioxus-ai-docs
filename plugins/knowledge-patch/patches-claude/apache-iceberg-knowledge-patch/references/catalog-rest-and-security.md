# Catalogs, REST, Security, and Cloud Integrations

## REST route and error contracts

### Default routes

Since 1.9.0, default REST routes do not include namespace, table, or view
`HEAD` endpoints. A client or server extension may provide them, but callers
must not assume they are registered.

In the `1.11.0-guides` contract, `/v1/config` returns 404 when the requested
warehouse does not exist. Servers can advertise a namespace separator so
clients do not need to hard-code one.

### Retry semantics

The 1.10.0 REST retry policy:

- Marks HTTP 503 as non-retryable.
- Stops retrying on 502 and 504.
- Allows selected status-code retries for idempotent requests.

Do not replace this with a blanket retry rule. Determine both the response
status and whether the operation can safely be repeated.

The `1.11.0-guides` protocol adds an `Idempotency-Key` header for mutating
catalog operations. Use it when retrying commits, creates, or drops so the
operation is not executed twice.

## Cache freshness and concurrency

REST clients can revalidate cached table metadata with ETags and handle
`304 Not Modified` in the `1.11.0-guides` behavior. `CommitTableResponse`
carries an ETag that clients can use for concurrent-change detection.

GCP BigQuery metastore integration also adds ETag conflict detection. Preserve
the relevant ETag through read-modify-write flows rather than silently
overwriting a newer state.

## Scan planning

Iceberg 1.10.0 adds REST scan-planning request/response models and their
parsers.

The `1.11.0-guides` protocol expands remote planning:

- REST catalogs can plan incremental scans.
- They can plan metadata-table scans.
- A per-table override can opt out of catalog-level planning.
- `LoadTableResult` can advertise `scan-planning-mode`.
- A planning response can include storage credentials when
  `include-credentials` is requested.

Keep credential-bearing responses within the authorization and lifetime of the
planned scan.

## Table and view operations

Catalogs add a view-override property in 1.9.0 for controlling view behavior.

The `1.11.0-guides` REST protocol adds optional view registration that attaches
existing view metadata. The separately authorizable `/register-view` endpoint
allows registration to have its own authorization policy. REST catalogs can
also inject custom `TableOperations` and `ViewOperations` implementations.

For Hive catalogs in the same guidance:

- Replacing a view updates its query in the Hive Metastore.
- Registering a table fails if a view already occupies the requested name;
  registration does not overwrite the view.

In 1.10.0, listing a nonexistent Hive namespace throws
`NoSuchNamespaceException`; code written for an empty-list result must handle
the exception.

Catalogs can enable unique table locations with a catalog property in 1.11.0.
Use this when derived locations must not be reused across repeated table
creations.

Table registration can explicitly overwrite under the
`1.11.0-guides` APIs. Make overwrite intent explicit rather than assuming it
from registration alone.

## REST metadata and protocol additions

The `1.11.0-guides` protocol makes S3 signing part of the main OpenAPI
specification and adds the following contracts:

- `TableUpdate` includes `SetPartitionStatisticsUpdate` and
  `RemovePartitionStatisticsUpdate`.
- `loadTable` can return a `referenced-by` dependency list.
- Servers can advertise the namespace separator.
- `/v1/config` distinguishes a missing warehouse with 404.

The table and REST specifications add encryption keys in 1.10.0, and the API
adds table-metadata keys.

## Authentication and HTTP client configuration

Core enables the Auth Manager API for authentication integrations in 1.9.0.

The 1.10.0 REST client adds configuration for:

- HTTP user agent
- TLS
- HTTP proxy
- Disabling token exchange during authentication refresh

The 1.8.0 REST specification documents configuration for cross-region S3
access.

## Encryption and key management

### Core and cloud KMS support

The 1.10.0 encryption-key specification is backed by
`KeyManagementClient` implementations for AWS and GCP.

The `1.11.0-guides` behavior makes table encryption usable across more paths:

- A Hive table can activate encryption with a table property containing the
  table master-key ID.
- Manifest lists are encrypted.
- Key-encryption keys can rotate automatically.
- `encryption.kms-type` selects AWS, Azure, or GCP KMS.
- Hive catalogs validate encrypted-table metadata integrity.
- Azure supplies an Azure Key Vault `KeyManagementClient`.

AWS KMS enables `RetryMode` as of 1.8.0. AWS also accepts the `kms.endpoint`
setting in the `1.11.0-guides` behavior.

## Cloud credentials and endpoints

### AWS

- Multiple storage-credential prefixes are supported in 1.10.0.
- The `1.11.0-guides` behavior adds configurable S3 chunked encoding.
- Proxy settings can come from system properties or environment variables.
- An explicitly configured credential provider takes precedence.

### Azure

- Access-token authentication is available through `adls.token` in 1.10.0.
- Custom token-credential providers are available in the
  `1.11.0-guides` behavior.
- Azure Key Vault can provide key management for encrypted tables.

### GCP

- Multiple storage-credential prefixes, Google authentication, and a BigQuery
  metastore catalog are available in 1.10.0.
- BigQuery metastore service-account impersonation,
  `gcp.auth.credentials-key`, and ETag conflict detection are available in the
  `1.11.0-guides` behavior.

### Aliyun OSS

RRSA authentication is available in the `1.11.0-guides` behavior.

### Credential refresh

Long-running `S3FileIO` and `GCSFileIO` instances refresh held storage
credentials on a schedule in 1.11.0. A custom provider must support repeated
refresh throughout the process lifetime.
