# Terraform and AzAPI

Use this reference for current compatibility details and exact command or schema changes.

## AzAPI 2.0 migration

### Authentication and default-output changes (azapi-2.0.0)

Managed identity no longer activates implicitly: `use_msi` defaults to
`false` and must be set to `true`. Without `response_export_values`, outputs
from `azapi_resource` and `azapi_update_resource` now default to read-only
fields, while `azapi_resource_list.output` defaults to the full response;
refresh state after upgrading, or set `disable_default_output = true` on the
provider to suppress this computed output.

### Azure resource-ID provider functions (azapi-2.0.0)

With Terraform 1.8+, AzAPI exposes `build_resource_id(parent_id, type, name)`
and `parse_resource_id(type, id)`. Scope-specific builders are
`subscription_resource_id(subscription_id, type, names)`,
`tenant_resource_id(type, names)`,
`management_group_resource_id(group_name, type, names)`,
`resource_group_resource_id(subscription_id, group_name, type, names)`, and
`extension_resource_id(base_id, type, names)`; each `names` argument is a
list ordered to match the resource-type segments.

```hcl
output "subnet_id" {
  value = provider::azapi::resource_group_resource_id(
    var.subscription_id, var.resource_group_name,
    "Microsoft.Network/virtualNetworks/subnets", ["vnet1", "subnet1"]
  )
}
```

### Custom API retry policy (azapi-2.0.0)

Resources and data sources can retry errors whose messages match configured
regular expressions, using exponential backoff controls in a `retry` object.

```hcl
retry = {
  error_message_regex  = ["ResourceGroupNotFound"]
  interval_seconds     = 5
  max_interval_seconds = 30
  multiplier           = 1.5
  randomization_factor = 0.5
}
```

### Named JMESPath response projections (azapi-2.0.0)

`response_export_values` can be a map from output names to JMESPath queries,
producing a directly addressable HCL object rather than requiring callers to
decode and traverse the entire response.

```hcl
response_export_values = {
  login_server      = "properties.loginServer"
  quarantine_status = "properties.policies.quarantinePolicy.status"
}

output "login_server" {
  value = data.azapi_resource.registry.output.login_server
}
```

### Native HCL bodies and outputs (azapi-2.0.0)

AzAPI 2.0 requires `body` to be an HCL object and returns `output` as an HCL
object, so remove `jsonencode`/`jsondecode` calls. The provider setting
`enable_hcl_output_for_data_source` is removed, as is `ignore_body_changes`;
use a native `lifecycle.ignore_changes` path instead.

```hcl
resource "azapi_resource" "subnet" {
  type      = "Microsoft.Network/virtualNetworks/subnets@2022-07-01"
  parent_id = azapi_resource.vnet.id
  name      = var.name
  body = {
    properties = {
      addressPrefix = "10.0.2.0/24"
      delegations   = []
    }
  }

  lifecycle {
    ignore_changes = [body.properties.delegations]
  }
}

output "subnet_prefix" {
  value = azapi_resource.subnet.output.properties.addressPrefix
}
```

### Plan-time preflight validation (azapi-2.0.0)

Set `enable_preflight = true` on the provider to validate resource
configuration during `terraform plan`; invalid Azure values such as malformed
CIDR prefixes then fail the plan before deployment.

```hcl
provider "azapi" {
  enable_preflight = true
}
```

### Provider-controlled replacement triggers (azapi-2.0.0)

`replace_triggers_external_values` forces replacement when a listed non-null
value changes. `replace_triggers_refs` instead names paths within the AzAPI
resource whose changes require replacement.

```hcl
replace_triggers_external_values = [var.sku, var.zones]
replace_triggers_refs            = ["properties.sku", "properties.zones"]
```

### Removed naming behavior (azapi-2.0.0)

Provider-level `default_naming_prefix` and `default_naming_suffix` are removed;
build them into each resource's `name`. `azapi_resource.removing_special_chars`
is also removed, so names must be sanitized by configuration instead.

### Request headers and query parameters (azapi-2.0.0)

Data sources accept `query_parameters`, whose values are string lists.
Managed resources can set operation-specific `create_query_parameters`,
`update_query_parameters`, `read_query_parameters`, and
`delete_query_parameters`, plus matching `create_headers`, `update_headers`,
`read_headers`, and `delete_headers` maps.

```hcl
data "azapi_resource_list" "builtins" {
  type      = "Microsoft.Authorization/policyDefinitions@2021-06-01"
  parent_id = "/subscriptions/${var.subscription_id}"
  query_parameters = {
    "$filter" = ["policyType eq 'BuiltIn'"]
  }
}
```

## AzAPI 2.x capabilities

### Absence-aware reads and actions (azapi-provider-2.x)

The `azapi_resource` data source accepts `ignore_not_found`; a missing
resource then avoids a 404 failure and is reported through its computed
`exists` field. Resource actions gain the same `ignore_not_found` and
existence pattern in 2.9.

### Additional identity and resource-ID outputs (azapi-provider-2.x)

`azapi_client_config.object_id` exposes the authenticated principal's object
ID. The `parse_resource_id` provider function now also returns
`resource_group_id`.

### Authentication compatibility (azapi-provider-2.x)

AKS workload identity accepts `AZURE_CLIENT_ID` and `AZURE_TENANT_ID`, and
auxiliary tenant IDs are propagated for cross-tenant ARM authentication.
Client-certificate authentication supports modern encrypted PFX files in
2.11.

### Body and collection reconciliation (azapi-provider-2.x)

`azapi_resource.ignore_null_property` excludes null-valued body properties
from comparison, and the order of `identity_ids` no longer matters. A body or
API-version edit also produces no change when the configured body still
matches the remote resource.

For lists, `list_unique_id_property` identifies items by a stable property and
`ignore_other_items_in_list` permits additional remote items to remain
unmanaged; both are available on `azapi_resource` and
`azapi_update_resource`. Version 2.9 also extends
`replace_triggers_external_values` to `azapi_update_resource`.

### Broader schema and preflight validation (azapi-provider-2.x)

Embedded schema checks for `azapi_resource` now run during
`terraform validate`, and preflight validation covers nested resources. From
2.10, preflight also validates update operations and requires only read
permission rather than write permission.

### Cross-provider state moves (azapi-provider-2.x)

`azapi_resource` supports Terraform resource moves from AzureRM resources
instead of requiring destroy and recreate. Later 2.x releases also translate
the data-plane-style IDs used by AzureRM storage containers, storage shares,
Key Vault keys, and Key Vault secrets into the ARM IDs AzAPI needs.

### Ephemeral and triggered resource actions (azapi-provider-2.x)

AzAPI 2.3 adds an ephemeral `azapi_resource_action`. Version 2.8 also adds a
stateless `azapi_resource_action` for Terraform action triggers, and 2.9 lets
resource actions change API version without recreation.

### Expanded data-plane coverage (azapi-provider-2.x)

`azapi_data_plane_resource` gains a customization layer for services whose
CRUD operations do not follow the standard pattern. Built-in coverage expands
to Purview scanning managed virtual networks, Key Vault keys and secrets,
Search data sources, indexers, indexes, skillsets, and synonym maps, plus
`Microsoft.Foundry/agents`; data-plane HTTP 204 responses are accepted as
successful operations.

### Identity-based import and bulk discovery (azapi-provider-2.x)

`azapi_resource` can import through provider identity using an ID alone, an ID
with an API version, or an ID with a resource type. When no API version is
explicit and import receives HTTP 400 or 404, 2.11 falls back through as many
as three recent indexed API versions.

The provider also implements the ListResource protocol for `azapi_resource`;
omitting `type` can enumerate every resource in a resource group.
`azapi_data_plane_resource` supports normal Terraform import as of 2.9.

### Provider environment and custom-cloud controls (azapi-provider-2.x)

The provider accepts `environment = "custom"` when all endpoints are supplied
manually. Instance discovery can be disabled with
`disable_instance_discovery` or `ARM_DISABLE_INSTANCE_DISCOVERY`; 2.x also
adds the Key Vault resource-manager audience for Azure Government.

`enable_preflight` and `disable_default_output` can be sourced from
`ARM_ENABLE_PREFLIGHT` and `ARM_DISABLE_DEFAULT_OUTPUT`, while
`oidc_azure_service_connection_id` can come from
`ARM_ADO_PIPELINE_SERVICE_CONNECTION_ID` or
`ARM_OIDC_AZURE_SERVICE_CONNECTION_ID`.

### Request and retry behavior (azapi-provider-2.x)

Resources and data sources accept a `User-Agent` header that is appended to
the provider's default user agent. Post-create GET requests retry HTTP 404 by
default, custom retry configuration overrides that policy, and an exhausted
retry sequence now returns its last retryable error instead of only
`context deadline exceeded`.

The `retry.multiplier` and `retry.randomization_factor` fields are deprecated
from 2.6, superseding the earlier custom-retry example in this stream.
Provider-level `maximum_busy_retry_attempts` is also deprecated; remove all
three before the next major release and allow the provider defaults to apply.

### Sensitive request and response payloads (azapi-provider-2.x)

`azapi_resource` and `azapi_update_resource` accept `sensitive_body` for
write-only request properties. `azapi_resource` adds
`sensitive_body_version` to manually control that payload's version;
`azapi_data_plane_resource` later receives both fields, and resource actions
receive sensitive request-body support in 2.11.

For action resources and data sources, `sensitive_response_export_values`
selects secret response fields and `sensitive_output` exposes the resulting
value as sensitive.

## AzureRM 4 migration

### AKS switches from preview to stable APIs (azurerm-4.0.0)

AzureRM 4.x removes preview-only AKS fields: `custom_ca_trust_enabled`,
`custom_ca_trust_certificates_base64`,
`api_server_access_profile.vnet_integration_enabled`,
`api_server_access_profile.subnet_id`, `storage_profile.disk_driver_version`,
and `message_of_the_day`; node-pool equivalents are also removed where
applicable, and `workload_runtime` no longer accepts
`KataMshvVMIsolation`. Use AzAPI for required preview features, but mixing
AzAPI changes into an AzureRM-managed AKS resource can cause diffs or
recreation.

### Azure resource-ID provider functions (azurerm-4.0.0)

With Terraform 1.8+, `provider::azurerm::normalise_resource_id(id)` fixes the
casing of Azure-controlled ID segments without changing user-supplied names,
and `provider::azurerm::parse_resource_id(id)` returns components such as
`subscription_id`, `resource_group_name`, `resource_provider`,
`full_resource_type`, `parent_resources`, and `resource_name`.

```hcl
locals {
  canonical_name = provider::azurerm::parse_resource_id(
    provider::azurerm::normalise_resource_id(var.resource_id)
  )["resource_name"]
}
```

### Changed defaults and upgrade-time drift (azurerm-4.0.0)

Security/network defaults now include TLS 1.2 for Application Gateway SSL
profiles and Cosmos DB, Event Hubs, and Service Bus; Standard SKU for Load
Balancers and Public IPs; Databricks `no_public_ip = true`; ML compute-cluster
`ssh_public_access_enabled = false`; Storage Account
`cross_tenant_replication_enabled = false`; subnet private-endpoint policies
`Disabled`; and private-link-service network policies enabled. AKS
`node_os_upgrade_channel` defaults to `NodeImage`, while ML Workspace public
network access still defaults to `true`.

Several formerly computed values can now produce configuration drift:
CDN endpoint paths/compression types, Databricks NSG rules, Elastic logs, AKS
load-balancer outbound IDs, VMSS `scale_in`, ML datastore `authority_url`,
NetApp snapshot schedules, Network Connection Monitor output workspaces, NIC
DNS servers, Sentinel display-name filters, and SignalR CORS. Configure them
explicitly or, where the service owns them, use `lifecycle.ignore_changes`;
Storage Account `large_file_share_enabled` also no longer universally
defaults to `true`.

### High-impact field migrations (azurerm-4.0.0)

AKS renames `automatic_channel_upgrade` to `automatic_upgrade_channel`,
`node_os_channel_upgrade` to `node_os_upgrade_channel`, and the cluster and
node-pool `enable_auto_scaling`, `enable_node_public_ip`, and
`enable_host_encryption` fields to their `*_enabled` forms. The API-server
authorized ranges move under `api_server_access_profile`, web-app-routing
uses `dns_zone_ids`, and `AvailabilitySet` is no longer a valid default-node
pool type.

Diagnostic settings replace `log` with `enabled_log` and move log/metric
retention policies to `azurerm_storage_management_policy`. Cosmos DB replaces
the generic `connection_strings` and `enable_*` fields with protocol-specific
connection strings and `*_enabled` fields; SQL containers use
`partition_key_paths`. Container App Job uses singular `secret` and
`registry` blocks, Cognitive Deployment replaces `scale` with `sku`, and
Container Group replaces `network_profile_id` with `subnet_ids`.

Service Bus queue/topic/subscription resources replace `enable_*` with
`*_enabled`; their data sources now identify parents by `namespace_id` or
`topic_id` instead of resource-group and entity names. Storage share
directories and table entities likewise use `storage_share_id` or
`storage_table_id`. Network interfaces use
`accelerated_networking_enabled`/`ip_forwarding_enabled`, route tables use the
positive `bgp_route_propagation_enabled`, and subnets use
`private_endpoint_network_policies` plus
`private_link_service_network_policies_enabled`.

Container Registry removes `encryption.enabled` (block presence now controls
encryption), replaces retention/trust blocks with
`retention_policy_in_days`/`trust_policy_enabled`, and drops the nested
virtual-network rule block. Linux and Windows VM scale sets rename
`gallery_applications`, `terminate_notification`, and `scale_in_policy` to
`gallery_application`, `termination_notification`, and `scale_in`.

### Inline virtual-network subnets (azurerm-4.0.0)

The `azurerm_virtual_network` inline `subnet` block gains
`default_outbound_access_enabled`, `delegation`,
`private_endpoint_network_policies`,
`private_link_service_network_policies_enabled`, `route_table_id`,
`service_endpoints`, and `service_endpoint_policy_ids`. Replace its singular
`address_prefix` with `address_prefixes`, which accepts multiple IPv4/IPv6
CIDRs; an upgrade may warn about replacement, but this migration should update
in place.

### Newly required values and collection changes (azurerm-4.0.0)

New required configuration includes Grafana `grafana_major_version`, image
OS/data-disk `storage_type`, activity-log-alert `location`, data-collection
rule syslog `streams`, AKS service-mesh `revisions`, Spring gateway-route
`protocol`, CDN custom-domain `user_managed_https.key_vault_secret_id`, and
virtual-network-gateway-connection `shared_key`. NGINX SKUs that scale need
either `capacity` or `auto_scale_profiles`; Function/Web App health-check path
and eviction time must be set together, and Function Apps in an App Service
Environment require `vnet_image_pull_enabled = true`.

`azurerm_virtual_network.address_space` and `azurerm_subnet.actions` change
from lists to sets, so positional indexing must be removed. Cosmos DB
`ip_range_filter` is now a set accepting only valid CIDRs, and a private DNS
resolver inbound endpoint permits at most one `ip_configurations` block.
`azurerm_api_management_api_tag` is recreated on upgrade so its revision can
enter the resource ID.

### Provider setup and resource-provider registration (azurerm-4.0.0)

Every provider instance now needs an explicit `subscription_id` or
`ARM_SUBSCRIPTION_ID`; Azure CLI authentication no longer infers the active
subscription. Automatic RP registration is controlled by
`resource_provider_registrations` (`core`, `extended`, `all`, `none`, or the
temporary `legacy` set), while `resource_providers_to_register` adds an exact
custom list; `none` is equivalent to the old `skip_provider_registration =
true`.

```hcl
provider "azurerm" {
  subscription_id                 = var.subscription_id
  resource_provider_registrations = "core"
  resource_providers_to_register  = ["Microsoft.ContainerService", "Microsoft.KeyVault"]
  features {}
}
```

### Removed resources and data sources (azurerm-4.0.0)

The legacy `azurerm_sql_*` resources and data sources listed by the provider
are gone in favor of their `azurerm_mssql_*` replacements. MariaDB and MySQL
Single Server resources/data sources are removed; migrate to the matching
MySQL Flexible Server resources (`azurerm_mysql_flexible_server`,
`_database`, `_configuration`, `_firewall_rule`, and
`_active_directory_administrator`), with customer-managed keys configured in
the flexible-server resource.

All provider resources for Disk Pool/iSCSI, Time Series Insights, Lab
Services, Logz, Azure Media Services, and Video Analyzer are removed, as are
App Service Environment, Integration Service Environment,
`azurerm_cosmosdb_notebook_workspace`, `azurerm_databox_edge_order`, and
`azurerm_monitor_log_profile`. Other direct migrations include
`azurerm_dashboard` to `azurerm_portal_dashboard`, `azurerm_graph_account` to
`azurerm_graph_services_account`, monitor action rules to monitor alert
processing rules, `azurerm_template_deployment` to
`azurerm_resource_group_template_deployment`, and the hybrid-compute-machine
data source to `azurerm_arc_machine`.

Other exact migrations are
`azurerm_cdn_frontdoor_route_disable_link_to_default_domain` to
`azurerm_cdn_frontdoor_route.link_to_default_domain`,
`azurerm_databricks_workspace_customer_managed_key` to
`azurerm_databricks_workspace_root_dbfs_customer_managed_key`,
`azurerm_data_factory_integration_runtime_managed` to
`azurerm_data_factory_integration_runtime_azure_ssis`, and
`azurerm_security_center_server_vulnerability_assessment` to its
`_virtual_machine` replacement. API Management policy, Service Bus namespace
network rules, Synapse AAD administrators, Container App custom domains, and
NGINX configuration move out to their documented dedicated resource or
embedded block.
