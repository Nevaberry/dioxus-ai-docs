# Application platform

Use this reference for current compatibility details and exact command or schema changes.

## AI Foundry and Cognitive Services

### AI Foundry command groups (2.80.0)

The `az cognitiveservices account connection`,
`az cognitiveservices account project`, and
`az cognitiveservices account project connection` groups manage AI Foundry
resources, and `az cognitiveservice agent` is a new command group.

### Cognitive Services compute clusters (2.89.0)

The new `az cognitiveservices account compute` command group manages compute
cluster resources.

### Cognitive Services project management and kind changes (2.78.0)

`az cognitiveservices account create` accepts `--allow-project-management`,
and `account update --kind` supports OpenAI-to-AIServices kind changes and back.

### Hosted AI Foundry agents (2.82.0)

`az cognitiveservices agent create` can create and deploy a hosted agent in
AI Foundry.

## API Management

### API Management backends (2.85.0)

The new `az apim backend` command group supports API Management backend
services.

## API Management retirements

### ADAL-based developer-portal identity providers are retired (api-management-retirements)

On September 30, 2025, API Management's provided developer portal stopped
supporting ADAL-based Microsoft Entra ID and Azure AD B2C identity providers;
without migration, user sign-in and sign-up stop working even though the API
Management service remains available. Change the application's redirect URI
to the single-page application platform, select `MSAL` as the identity
provider's client library, update the configuration, and republish the
developer portal; the replacement uses authorization code flow with PKCE.

### The direct management API is retired (api-management-retirements)

The optional direct management API, disabled by default but previously
available in the Premium, Standard, Basic, and Developer tiers, retired on
March 15, 2025. Replace tools that call
`https://<service-name>.management.azure-api.net` with equivalent operations
in the standard Azure Resource Manager-based API Management REST API, and
disable the direct API if it is still enabled; the API Management instance
itself is otherwise unaffected.

## App Configuration

### Anonymous App Configuration access (2.83.0)

App Configuration commands now accept `anonymous` for `--auth-mode`.

### App Configuration custom token audiences (2.70.0)

`az appconfig` operations using `--auth-mode login` can now use a custom token
audience.

### App Configuration feature-management schema and timestamps (2.69.0)

Key-value import/export and feature show/list commands now understand the
Microsoft feature-management schema. File exports can set
`AZURE_APPCONFIG_FM_COMPATIBILE` for backward compatibility, and datetime
inputs for key-value restore/show/list and revision list accept timezone
offsets.

### App Configuration network security perimeters (2.87.0)

App Configuration store create/update operations and the
`network-security-perimeter-configuration` command now support Network
Security Perimeter configuration.

### App Configuration retention and feature tag filters (2.76.0)

`az appconfig create/update` can set the key-value revision retention period.
Feature `list`, `delete`, and `set` operations now support tag filters.

### App Configuration serialization (2.78.0)

`az appconfig kv export` escapes keys only for properties-file output.
`az appconfig kv set` and `import` now accept JSON comments.

### App Configuration snapshot references (2.87.0)

`az appconfig kv set-snapshot-reference` creates a snapshot-reference
key-value, and `az appconfig kv list` can list key-values from a snapshot
reference.

### App Configuration tag filters and dry runs (2.75.0)

Tag filtering is now supported by App Configuration key-value
export/import/list/delete, restore, and revision-list operations.
`az appconfig kv import`, `export`, and `restore` also accept `--dry-run`.

### App Configuration telemetry (2.85.0)

App Configuration store create/update can link an Application Insights
resource, and `az appconfig feature set` can enable telemetry for a feature
flag.

### New App Configuration and App Service SKUs (2.72.0)

`az appconfig create` and `az appconfig update` support the Developer SKU.
`az appservice plan create` supports the Pv4 and Pmv4 App Service Plan
families.

## App Service and Web Apps

### App Service asynchronous scaling (2.78.0)

`az appservice plan create` and `update` accept `--async-scaling-enabled`.

### App Service command changes (2.69.0)

`az functionapp deployment slot create` gains `--https-only`. On Linux,
`az webapp list-runtimes` no longer returns JBoss `_byol` entries, so scripts
that select those runtime identifiers must be updated.

### App Service deployment diagnostics and conversion (2.86.0)

`az webapp up` and `az webapp deploy` accept `--enriched-errors` to return
detailed deployment-failure logs. `az webapp sitecontainers convert` can now
convert Docker Compose multi-container apps to Sitecontainers mode.

### App Service domain-label scope and container conversion (2.76.0)

`az webapp create` accepts `--domain-name-scope` for DNL scope selection, and
`az webapp sitecontainers convert` switches an app between sitecontainers and
classic configuration.

### App Service hostname scope and release channels (2.85.0)

`az logicapp create` and `az webapp up` accept `--domain-name-scope` to
select the uniqueness scope for the default hostname. `az webapp update`
accepts `--platform-release-channel` to set the app's platform release
channel.

### App Service lifecycle and zoning (2.73.0)

App Service Environment create/update/delete no longer supports ASEv2.
`az functionapp plan update` can now update zone redundancy for Flex plans.

### App Service output and runtime discovery (2.84.0)

`az webapp config access-restriction show` now always returns values in camel
case, so consumers of its output must use that casing. `az webapp list
runtimes` no longer relies on hardcoded runtime lists and includes previously
missing Java versions.

### App Service plan operating-system default (2.88.0)

Without an explicit `--hyper-v`, `az appservice plan create` now defaults to
Linux. Pass `--is-linux false` when creating a Windows App Service plan.

### App Service VNet routing behavior (2.84.0)

For API version `2024-11-01`, Web App create/configuration and Web App or
Function App VNet-integration commands now use the site-level outbound VNet
routing property.

### Latest Web App startup status (2.89.0)

`az webapp troubleshoot status` now returns data for the latest application
startup attempt.

### Linux App Service plan default (2.86.0)

When `--sku` is omitted for a Linux web app, `az appservice plan create` now
defaults to `P0V3`. The command also recognizes the `PREMIUM0V3` tier for
elastic scale, so automation that depends on another plan size must pass it
explicitly.

### Linux Web App site containers and Kudu warm-up (2.70.0)

Linux web apps gain the `az webapp sitecontainers` command group. Deployment
through `az webapp up`, `az webapp deploy`, or
`az webapp deployment source config-zip` can use `--enable-kudu-warmup` to
warm Kudu before deploying.

### Managed-instance App Service plans (2.89.0)

Managed-instance App Service plans are now stable rather than preview, and
plan operations support the Premium V3 SKUs `P0V3`, `P1-3V3`, and `P1-5MV3`.

### Managed-instance-aware App Service locations (2.82.0)

`az appservice list-locations` accepts `--managed-instance-enabled` when
discovering locations that support managed instances.

### Site-scoped Web App certificates (2.87.0)

`az webapp create --site-scoped-certs` controls whether site-scoped
certificates are enabled for a new app.

### Structured Web App runtime discovery (2.87.0)

In a breaking output change, `az webapp list-runtimes` now returns objects
with `os`, `runtime`, `version`, `config`, `support`, and `end_of_life`
fields instead of a flat string list. Use the new `--runtime` and `--support`
filters; `--linux` and `--show-runtime-details` have been removed.

### Web App transport encryption (2.84.0)

`az webapp create` and `az webapp update` accept
`--end-to-end-encryption-enabled` for encryption between the front end and
workers. Creation also accepts `--min-tls-version` and
`--min-tls-cipher-suite`.

### Web App worker-count validation (2.74.0)

`az webapp config set` no longer performs CLI validation of the number of
workers, so that check no longer rejects the request before it reaches Azure.

## Application platform operations

### Deployment-slot VNet inheritance (2.71.0)

`az webapp deployment slot create` now gives a new slot the same VNet
integration settings as its source slot, matching Portal-created slots.

### Flex Consumption certificates (2.88.0)

`az functionapp config ssl` now supports site-scoped certificates for Flex
Consumption. `az functionapp flex-migration` can also migrate Linux
Consumption apps that have certificates.

### Flexible Consumption location discovery (2.71.0)

`az functionapp list-flexconsumption-locations` accepts `--details` to return
more location information and `--runtime` to select a runtime.

### Hosted-agent log streaming (2.83.0)

`az cognitiveservices agent logs show` streams console logs for hosted agents.
Agent `create` and `start` accept `--show-logs`, and `start` also accepts
`--timeout`.

### Linux container startup logs (2.87.0)

The new `az webapp log startup` commands list and display Linux container
startup logs.

### Registry inspection without a configured server (2.79.0)

`az containerapp registry show` now handles container apps that have no
registry server instead of failing with a `NoneType` error.

## Azure Functions

### Consumption-to-Flex function migration (2.77.0)

The new `az functionapp flex-migration` command group supports migrating CV1
function apps to Flex.

### Function App update strategies (2.87.0)

`az functionapp update-strategy config set` sets or updates a Function App's
update-strategy configuration, while `config show` retrieves it.

### Zone-redundant Elastic Premium Functions (2.80.0)

`az functionapp plan create` now supports zone redundancy for Elastic Premium
SKUs.

## Container Apps

### Container App Compose environment parsing (2.69.0)

`az containerapp compose create` splits an environment assignment only at
its first `=`, so values can themselves contain equal signs.

### Container App job listing and zero execution limits (2.77.0)

`az containerapp job list` no longer stops after 20 items. `az containerapp
job update` now accepts `0` for both `--min-executions` and
`--max-executions`.

### Container Apps environment routing and premium ingress (2.79.0)

The new `az containerapp env http-route-config` and
`az containerapp env premium-ingress` groups manage environment-level HTTP
routing and premium ingress settings.

### Container Apps infrastructure resource groups (2.82.0)

`az containerapp env create --infrastructure-resource-group` selects the
resource-group name used for the environment's infrastructure resources.

### Default Container Apps workload-profile name (2.85.0)

`az containerapp env workload-profile add` now supplies a default profile
name when one is not specified.

### New Container Apps and Maps defaults (2.84.0)

`az containerapp job create` now supplies defaults for `--parallelism` and
`--replica-completion-count`. `az maps account create` likewise supplies a
default for `--sku`; pass these options explicitly when automation must not
depend on CLI defaults.

### Premium-ingress replica arguments removed (2.80.0)

`az containerapp env premium-ingress` operations no longer accept
`--min-replicas` or `--max-replicas`.

## HDInsight

### HDInsight credential operations (2.79.0)

`az hdinsight credentials show` retrieves current cluster credentials, and
`az hdinsight credentials update` changes them.

### HDInsight Entra and managed-identity storage (2.79.0)

`az hdinsight create` can create Entra-enabled clusters and clusters using
WASB with a managed identity.

## Service Connector

### Neon Postgres Service Connector (2.71.0)

Service Connector's workload-specific `connection create neon-postgres`
commands can create connections to Neon Postgres Serverless.

### Service Connector identity and Fabric targeting (2.70.0)

`az containerapp connection create redis` accepts `--system-identity`.
`az webapp connection create fabric-sql` gains `--fabric-workspace-uuid` and
`--fabric-sql-db-uuid` for selecting the Fabric workspace and SQL database.

## Service Fabric

### Service Fabric cluster names from parameter files (2.77.0)

When a parameters file supplies `cluster_name`, `az sf cluster create` now
uses that value.

### Service Fabric managed-cluster controls (2.76.0)

Managed-cluster network security rules accept `--source-addr-prefix`,
`--dest-addr-prefix`, `--source-port-range`, and `--dest-port-range`.
`az sf managed-node-type update` can also change `--vm-size` and `--tags`.

### Service Fabric update argument removals (2.80.0)

`az sf managed-application update` drops `--service-type-policy`,
`--upgrade-replica-set-check-timeout`, `--max-porcent-unhealthy-partitions`,
`--max-porcent-unhealthy-replicas`, `--max-porcent-unhealthy-services`, and
`--max-porcent-unhealthy-apps`. `az sf application update` drops
`--service-type-policy`, `--upgrade-replica-set-check-timeout`,
`--instance-close-duration`, `--consider-warning-as-error`,
`--max-percent-unhealthy-partitions`, `--max-percent-unhealthy-replicas`, and
`--max-percent-unhealthy-deployed-applications`.
