# Data, marketplace, and customer-facing services

## Data platforms and analytics

### DataZone Snowflake connections

DataZone `CreateConnection` accepts `SNOWFLAKE` connections through `snowflakeProperties` (since `2026-06`). The properties cover Snowflake connection details, a Secrets Manager secret, an Athena spill bucket, and identity mapping. Supply all required cross-service permissions with the connection.

### Clean Rooms

Clean Rooms collaborations support intermediate tables (since `2026-06`). Workflows can persist and reuse intermediate results within the collaboration instead of forcing every analysis into one terminal query.

### OpenSearch

- Saved Object Migration APIs move dashboards, visualizations, index patterns, and other saved objects into an application workspace (since `2026-07`). Exports can be filtered, and imports expose conflict-resolution strategies.
- Creating a Mustang domain requires `EngineMode` set to `OPTIMIZED` and `UseCase` set to `OBSERVABILITY` or `MIXED` (since `2026-07`). Omitting `EngineMode` creates a regular `GENERAL` domain.
- OpenSearch also exposes an Insights Feedback API (since `2026-07`).

### QuickSight

QuickSight supports `FileSource` physical tables, allowing datasets to use file-backed sources (since `2026-07`). Handle `FileSource` as an additional physical-table variant in schema visitors and serializers.

## Application configuration

AppConfig supports A/B tests, multivariate tests, and gradual feature rollouts across an application stack (since `2026-06`). In `2026-07`, `ExperimentRun` APIs also began returning `ConflictException`; handle conflicts as an expected concurrent-operation failure rather than treating them as an unrecognized service error.

## Amazon Connect and Customer Profiles

### Contact content and privacy

- Connect Health input validation accepts Unicode and Markdown table syntax (since `2026-06`). Do not strip these inputs solely for compatibility with the older validator.
- `DeleteContactData` can delete personally identifiable information from a customer endpoint, additional email recipients, and an email subject (since `2026-07`). Select the intended data locations rather than assuming the operation only clears the original endpoint fields.

### Authorization, sessions, and notifications

- Amazon Connect adds `CreateAuthCode` and `DeleteSession` (since `2026-07`). Incorporate both into integrations that create authorization codes and explicitly terminate sessions.
- `SendOutboundWebNotification` delivers notifications to end-customer chat-widget sessions (since `2026-07`). Only the Amazon Connect Outbound Campaigns service principal can call it; ordinary application principals cannot invoke it directly.

### Customer Profiles recommendations

Customer Profiles adds `diversityConfig` under `recommenderConfig` and supports trained recommender version rollback (since `2026-07`). Preserve the diversity settings with version metadata when promoting or reverting a trained recommender.

## Location and IoT

### Places V2

Places V2 request and response shapes add `AddressNamesMode`, `AddressNameTranslations`, `MobilityMode`, `PostalCodeMode`, `SecondaryAddresses`, and `DriveThrough` (since `2026-07`). These fields support formatted and translated names, travel-aware search, postal codes spanning multiple cities, unit-level secondary addresses, and drive-through attributes.

### IoT Wireless multicast

Multicast Group APIs support default session downlink transmission parameters (since `2026-07`). A FUOTA workflow can start a multicast session without resupplying transmission parameters when defaults are configured.

## Partner, Marketplace, and billing APIs

### Partner Central

- PartnerCentral Selling can associate or disassociate `AwsMarketplaceSolutions` and `AwsMarketplaceProducts` with opportunities (since `2026-06`). `GetOpportunity` returns the associations, and `ListSolutions` includes `AwsMarketplaceSolutionArn`.
- Partner Central Revenue Measurement is a new API for creating, managing, and tracking revenue attributions and Marketplace revenue-share allocations (since `2026-07`).

### Marketplace

- `BatchMeterUsage` accepts records for up to 24 hours after a metered event instead of six hours (since `2026-07`). The existing six-hour end-of-billing-cycle grace period remains unchanged.
- Marketplace Catalog `ListEntities` supports a `ResellerRole` filter for `ResaleAuthorization` entities (since `2026-07`).

### Billing

The Billing client can retrieve credit details and monthly allocation history, redeem promotional codes, configure credit sharing, and manage billing preferences (since `2026-07`). Treat these as distinct permission surfaces in least-privilege policies.

### Cognito provisioned limits

Cognito User Pools adds `GetProvisionedLimit` and `UpdateProvisionedLimit` for reading and changing provisioned API rate limits (since `2026-07`). Distinguish provisioned limits from ordinary quota-inspection APIs.

## Media and streaming

- IVS ad configuration resources accept `postRollConfiguration` (since `2026-07`). Preserve it in read-modify-write updates.
- MediaTailor SSAI and Channel Assembly responses include separate IPv4 and IPv6 endpoint fields (since `2026-07`). Do not assume a single endpoint field covers both network families.
- MediaConvert supports integer-second duration normalization and an option to disable explicit weighted prediction (since `2026-07`).
- GameLift Streams `CreateStreamSessionAdminShell` establishes a secure terminal connection to the live runtime environment of a streaming session for troubleshooting (since `2026-07`). Restrict it to operational workflows that require live shell access.
