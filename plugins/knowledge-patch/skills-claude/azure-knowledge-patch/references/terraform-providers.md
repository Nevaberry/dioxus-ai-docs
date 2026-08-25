# Terraform providers

## AzureRM 4.x provider configuration

### Subscription and resource-provider registration (`azurerm-4.0.0`)

Every provider instance needs `subscription_id` or `ARM_SUBSCRIPTION_ID`;
Azure CLI authentication no longer infers the active subscription. Automatic
registration uses `resource_provider_registrations` with `core`, `extended`,
`all`, `none`, or temporary `legacy`. Add exact namespaces with
`resource_providers_to_register`. `none` replaces
`skip_provider_registration = true`.

```hcl
provider "azurerm" {
  subscription_id                 = var.subscription_id
  resource_provider_registrations = "core"
  resource_providers_to_register  = ["Microsoft.ContainerService", "Microsoft.KeyVault"]
  features {}
}
```

### Resource-ID functions

With Terraform 1.8+, use
`provider::azurerm::normalise_resource_id(id)` to correct Azure-controlled ID
segment casing without changing user names. `parse_resource_id(id)` returns
`subscription_id`, `resource_group_name`, `resource_provider`,
`full_resource_type`, `parent_resources`, and `resource_name`.

```hcl
locals {
  name = provider::azurerm::parse_resource_id(
    provider::azurerm::normalise_resource_id(var.resource_id)
  )["resource_name"]
}
```

### Inline VNet subnets

The `azurerm_virtual_network.subnet` block adds
`default_outbound_access_enabled`, `delegation`,
`private_endpoint_network_policies`,
`private_link_service_network_policies_enabled`, `route_table_id`,
`service_endpoints`, and `service_endpoint_policy_ids`. Replace singular
`address_prefix` with set-like `address_prefixes` for multiple IPv4/IPv6
CIDRs. The upgrade can warn about replacement, but this migration should
update in place.

### AKS stable-API boundary

AzureRM 4.x removes preview-only AKS fields:
`custom_ca_trust_enabled`, `custom_ca_trust_certificates_base64`,
`api_server_access_profile.vnet_integration_enabled`,
`api_server_access_profile.subnet_id`, `storage_profile.disk_driver_version`,
and `message_of_the_day`, plus applicable node-pool equivalents.
`workload_runtime` no longer accepts `KataMshvVMIsolation`. Use AzAPI when a
preview feature is indispensable, but do not casually let AzAPI and AzureRM
manage the same AKS properties: it can cause diffs or recreation.

## AzureRM resource migrations

### Removed service families

- Replace legacy `azurerm_sql_*` resources/data sources with their
  `azurerm_mssql_*` equivalents.
- MariaDB and MySQL Single Server are removed. Use
  `azurerm_mysql_flexible_server`, `_database`, `_configuration`,
  `_firewall_rule`, and `_active_directory_administrator`; configure CMK on
  the flexible server.
- Provider resources for Disk Pool/iSCSI, Time Series Insights, Lab Services,
  Logz, Media Services, and Video Analyzer are removed.
- App Service Environment, Integration Service Environment,
  `azurerm_cosmosdb_notebook_workspace`, `azurerm_databox_edge_order`, and
  `azurerm_monitor_log_profile` are removed.

### Exact replacements

| Old surface | Replacement |
| --- | --- |
| `azurerm_dashboard` | `azurerm_portal_dashboard` |
| `azurerm_graph_account` | `azurerm_graph_services_account` |
| monitor action rules | monitor alert processing rules |
| `azurerm_template_deployment` | `azurerm_resource_group_template_deployment` |
| hybrid-compute-machine data source | `azurerm_arc_machine` |
| `azurerm_cdn_frontdoor_route_disable_link_to_default_domain` | route `link_to_default_domain` |
| `azurerm_databricks_workspace_customer_managed_key` | `azurerm_databricks_workspace_root_dbfs_customer_managed_key` |
| `azurerm_data_factory_integration_runtime_managed` | `azurerm_data_factory_integration_runtime_azure_ssis` |
| `azurerm_security_center_server_vulnerability_assessment` | `_virtual_machine` replacement |

API Management policy, Service Bus namespace network rules, Synapse Entra
administrators, Container App custom domains, and NGINX configuration move to
their documented dedicated resource or embedded block.

### High-impact field changes

- AKS: `automatic_channel_upgrade` becomes `automatic_upgrade_channel`;
  `node_os_channel_upgrade` becomes `node_os_upgrade_channel`; cluster and
  node-pool `enable_auto_scaling`, `enable_node_public_ip`, and
  `enable_host_encryption` become `*_enabled`. Authorized IP ranges move into
  `api_server_access_profile`; web-app routing uses `dns_zone_ids`;
  `AvailabilitySet` is not a valid default-node-pool type.
- Diagnostics: replace `log` with `enabled_log`; move log/metric retention to
  `azurerm_storage_management_policy`.
- Cosmos DB: use protocol-specific connection strings, `*_enabled` names, and
  SQL container `partition_key_paths` instead of the generic old forms.
- Container App Job: use singular `secret` and `registry` blocks. Cognitive
  Deployment uses `sku`, not `scale`; Container Group uses `subnet_ids`, not
  `network_profile_id`.
- Service Bus queues/topics/subscriptions replace `enable_*` with
  `*_enabled`; data sources identify parents with `namespace_id` or `topic_id`.
- Storage share directories and table entities identify parents with
  `storage_share_id` or `storage_table_id`.
- NICs use `accelerated_networking_enabled` and `ip_forwarding_enabled`;
  route tables use positive `bgp_route_propagation_enabled`; subnets use
  `private_endpoint_network_policies` and
  `private_link_service_network_policies_enabled`.
- ACR removes `encryption.enabled` because block presence controls encryption;
  use `retention_policy_in_days` and `trust_policy_enabled`, and remove the
  nested VNet rule block.
- Linux/Windows VMSS use singular `gallery_application`,
  `termination_notification`, and `scale_in` blocks.

### Required values and collection semantics

Now required are Grafana `grafana_major_version`, image OS/data-disk
`storage_type`, activity-log-alert `location`, DCR syslog `streams`, AKS
service-mesh `revisions`, Spring gateway-route `protocol`, CDN custom-domain
`user_managed_https.key_vault_secret_id`, and VNet gateway connection
`shared_key`.

NGINX scaling needs `capacity` or `auto_scale_profiles`. Function/Web App
health-check path and eviction time must be set together. Function Apps in an
App Service Environment need `vnet_image_pull_enabled = true`.

`azurerm_virtual_network.address_space` and `azurerm_subnet.actions` are sets,
not lists; remove positional indexing. Cosmos DB `ip_range_filter` is a CIDR-
validated set. A private DNS resolver inbound endpoint permits at most one
`ip_configurations` block. `azurerm_api_management_api_tag` is recreated so
its revision can enter the resource ID.

### Defaults and drift

Changed defaults include TLS 1.2 for Application Gateway SSL profiles, Cosmos
DB, Event Hubs, and Service Bus; Standard Load Balancer/Public IP; Databricks
`no_public_ip = true`; ML compute SSH disabled; Storage cross-tenant
replication disabled; subnet private-endpoint policies `Disabled`; private-
link-service policies enabled; and AKS `node_os_upgrade_channel = NodeImage`.
ML Workspace public network access remains enabled by default.

Formerly computed values can drift for CDN paths/compression, Databricks NSG
rules, Elastic logs, AKS outbound IDs, VMSS `scale_in`, ML datastore
`authority_url`, NetApp schedules, Connection Monitor workspaces, NIC DNS,
Sentinel display-name filters, and SignalR CORS. Configure them explicitly or
ignore only service-owned paths. Storage `large_file_share_enabled` no longer
universally defaults to true.

## AzAPI 2.0 migration (`azapi-2.0.0`)

### Native HCL bodies and outputs

`body` and `output` are native HCL objects; remove `jsonencode` and
`jsondecode`. `enable_hcl_output_for_data_source` and `ignore_body_changes`
are removed. Use precise Terraform lifecycle paths.

```hcl
resource "azapi_resource" "subnet" {
  type      = "Microsoft.Network/virtualNetworks/subnets@2022-07-01"
  parent_id = azapi_resource.vnet.id
  name      = var.name
  body = { properties = { addressPrefix = "10.0.2.0/24", delegations = [] } }
  lifecycle { ignore_changes = [body.properties.delegations] }
}
```

### Resource-ID functions

Terraform 1.8+ provides `build_resource_id(parent_id, type, name)` and
`parse_resource_id(type, id)`, plus:

- `subscription_resource_id(subscription_id, type, names)`
- `tenant_resource_id(type, names)`
- `management_group_resource_id(group_name, type, names)`
- `resource_group_resource_id(subscription_id, group_name, type, names)`
- `extension_resource_id(base_id, type, names)`

The `names` list follows resource-type segment order.

### Requests, projections, and replacement

- Resources/data sources accept a `retry` object matching error messages by
  `error_message_regex`, with `interval_seconds`, `max_interval_seconds`,
  `multiplier`, and `randomization_factor` backoff controls. Later 2.x
  deprecates the last two; see the current-state section below.
- Data sources accept list-valued `query_parameters`. Resources have per-
  operation `create_query_parameters`, `update_query_parameters`,
  `read_query_parameters`, and `delete_query_parameters`, plus matching
  `create_headers`, `update_headers`, `read_headers`, and `delete_headers`.
- `replace_triggers_external_values` replaces on changed non-null values;
  `replace_triggers_refs` names paths whose change requires replacement.
- A map-valued `response_export_values` maps output names to JMESPath queries,
  yielding directly addressable HCL.
- `enable_preflight = true` validates during `terraform plan`.

### Removed naming and output behavior

Provider `default_naming_prefix`/`default_naming_suffix` and resource
`removing_special_chars` are removed; sanitize and compose names in HCL.
Managed identity no longer activates implicitly: set `use_msi = true`.
Without `response_export_values`, resource/update output defaults to read-only
fields and resource-list output to the full response. Refresh after upgrade,
or set `disable_default_output = true` to suppress computed default output.

## Current AzAPI 2.x capabilities (`azapi-provider-2.x`)

### State moves, import, and discovery

`azapi_resource` supports Terraform moves from AzureRM resources. Later 2.x
translates AzureRM data-plane IDs for storage containers/shares and Key Vault
keys/secrets into ARM IDs.

Import can use ID alone, ID plus API version, or ID plus resource type. If no
API version is supplied and 2.11 gets HTTP 400/404, it tries up to three recent
indexed versions. ListResource can enumerate a group, including all resources
when `type` is omitted. `azapi_data_plane_resource` supports import from 2.9.

### Ephemeral actions and sensitive values

AzAPI 2.3 adds ephemeral `azapi_resource_action`; 2.8 adds stateless actions
for Terraform action triggers; 2.9 allows action API-version changes without
recreation.

`azapi_resource` and `azapi_update_resource` accept `sensitive_body`;
`sensitive_body_version` manually versions it. Data-plane resources later get
both, and 2.11 actions get sensitive request bodies. Actions/data sources use
`sensitive_response_export_values`, exposing `sensitive_output`.

### Validation and absence-aware reads

Embedded schemas validate `azapi_resource` during `terraform validate`.
Preflight covers nested resources and, from 2.10, updates using only read
permission. Data-source `ignore_not_found` reports absence through `exists`;
resource actions gain the same pattern in 2.9.

### Reconciliation controls

`ignore_null_property` omits null body properties from comparison;
`identity_ids` ordering is irrelevant; body/API-version edits produce no diff
when the configured body still matches remote state. For lists,
`list_unique_id_property` provides stable identity and
`ignore_other_items_in_list` preserves extra remote entries. These apply to
resource and update-resource; 2.9 extends external replacement triggers to
update-resource.

### Data plane and custom clouds

The data-plane resource customization layer covers nonstandard CRUD. Built-in
coverage includes Purview scanning managed VNets, Key Vault keys/secrets,
Search data sources/indexers/indexes/skillsets/synonym maps, and
`Microsoft.Foundry/agents`; HTTP 204 is accepted.

For a custom environment, set `environment = "custom"` and all endpoints.
Disable instance discovery with `disable_instance_discovery` or
`ARM_DISABLE_INSTANCE_DISCOVERY`. Azure Government has the Key Vault ARM
audience. Environment equivalents include `ARM_ENABLE_PREFLIGHT`,
`ARM_DISABLE_DEFAULT_OUTPUT`, and Azure DevOps OIDC connection IDs via
`ARM_ADO_PIPELINE_SERVICE_CONNECTION_ID` or
`ARM_OIDC_AZURE_SERVICE_CONNECTION_ID`.

### Authentication, requests, and current retry guidance

AKS workload identity accepts `AZURE_CLIENT_ID` and `AZURE_TENANT_ID`;
auxiliary tenants support cross-tenant ARM auth; 2.11 supports modern encrypted
PFX client certificates. Resources/data sources append a configured
`User-Agent` to the provider UA.

Post-create GET retries HTTP 404 by default; custom retry replaces that policy,
and exhaustion returns the last retryable error. From 2.6,
`retry.multiplier`, `retry.randomization_factor`, and provider
`maximum_busy_retry_attempts` are deprecated: remove them and use defaults.

`azapi_client_config.object_id` exposes the principal object ID, and
`parse_resource_id` also returns `resource_group_id`.
