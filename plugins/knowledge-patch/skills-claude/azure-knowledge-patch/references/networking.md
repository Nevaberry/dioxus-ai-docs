# Networking

## Private virtual-network defaults

### New VNets become private (`network-defaults-and-sku-retirements`)

With the API version released after March 31, 2026, subnets in newly created
VNets default `defaultOutboundAccess` to false. VMs need NAT Gateway, Standard
Load Balancer outbound rules, Standard public IP, or a firewall/NVA reached by
UDR for outbound internet and public Azure endpoints. The portal already uses
the private default. Older explicitly selected APIs leave an omitted property
null and permit implicit outbound access.

Existing VNets and VMs on existing nonprivate subnets do not change. A new
subnet may explicitly opt back into default outbound access for compatibility.

### Changing privacy requires deallocation

After enabling or disabling subnet default outbound access, stop and deallocate
existing VMs so their NICs receive the change.

```azurecli
az network vnet subnet update --resource-group rgname --vnet-name vnetname \
  --name subnetname --default-outbound false
```

A VM on a nonprivate subnet can retain an implicit default outbound IP and
Advisor alert even when NAT Gateway or UDR egress takes precedence. Fully
remove them with both a private subnet and VM deallocation.

### Routing exceptions

On a private subnet, a UDR with `Internet` next hop does not itself provide
egress. Service-tag routes that bypass an NVA also fail without another
explicit outbound method; service endpoints are unaffected. Same-region
Storage remains reachable and should be constrained with NSGs. The setting
does not apply to delegated or managed PaaS subnets.

A known issue gives default outbound access to IP-address-based Load Balancer
backend pools. Attach NAT Gateway to the VM subnet for deterministic egress.

## Load Balancer and Public IP retirement

### Basic Load Balancer

Basic Load Balancer retired September 30, 2025. Existing instances remain
operational but unsupported and without SLA; Cloud Services Extended Support
is exempt and can create/use Basic.

Plan downtime. Before disassociation, make every frontend and backend-VM public
IP static or its address can be lost. All IPs and load balancers must have
matching SKUs. Standard public IP needs an inbound NSG allow rule. A public
Standard LB needs an outbound rule; a private LB needs NAT Gateway or instance
public IPs.

### Basic Public IP

Basic Public IP retired the same day and has the same unsupported/no-SLA state;
Cloud Services Extended Support remains exempt. Upgrade a disassociated address
only if zone redundancy is unnecessary; zone redundancy requires a new
Standard address. An address attached to an LB must match its regional/global
tier.

Associated addresses follow the owner migration: replace Basic LB, migrate
gateways, and replace rather than upgrade uniform-VMSS per-instance public IP
configurations. Basic IPs on Application Gateway v1 remain exempt until that
gateway SKU retires.

## Virtual networks, IPAM, NICs, and NAT

### VNet and subnet controls

- `2.68.0` VNet create/update adds `--ipam-pool-prefix-allocations`; VNet
  Gateway create/update adds `--resiliency-model`.
- `2.70.0` NIC IP-config create/update adds
  `--private-ip-address-prefix-length`.
- `2.75.0` VNet subnet create/update can allocate address space from IPAM.
- `2.77.0` VNet show/list adds `defaultPublicNatGateway`.
- `2.87.0` VNet create/update adds `--summarized-gateway-prefixes`.
- `2.88.0` VNet list without resource group returns all VNets; update scripts
  that assumed group-scoped output.

### Standard V2 NAT, public IP, and prefixes

`2.75.0` adds Standard V2 support to NAT Gateway, public IP, and public IP
prefix. `2.77.0` Standard V2 NAT supports IPv6 public IPs/prefixes. `2.89.0`
adds `az network nat gateway --nat64` to enable or disable NAT64.

## Gateways, VPN, ExpressRoute, and route servers

- `2.69.0` Load Balancer create accepts multiple frontend zones; route-server
  create/update adds autoscale configuration.
- `2.71.0` network virtual-appliance boot diagnostics are retrievable;
  VNet-gateway create adds misspelled `--enable-high-bandwith-vpn-gateway`.
- `2.74.0` adds VNet Gateway migration and new VPN-connection show properties.
- `2.77.0` VNet Gateway adds insights and failover.
- `2.78.0` VNet Gateway create no longer requires a public IP.
- `2.83.0` VNet Gateway adds identity parameters/group; VPN connection adds
  `--auth-type` and `--cert-auth`.
- `2.86.0` ExpressRoute gateway supports Virtual WAN resiliency; route-table
  create/update adds `--disable-peering-route`.
- `2.88.0` VPN connection create does not require `--shared-key` for
  certificate authentication.

## Application Gateway and WAF

- `2.72.0` WAF managed rules accept `Microsoft_DefaultRuleSet`.
- `2.76.0` WAF output adds read-only `computedDisabledRules`; custom-rule
  grouping adds `GeoLocationXffHeader`/`ClientAddrXffHeader`.
- `2.79.0` Application Gateway create/update adds FIPS.
- `2.80.0` HTTP settings support dedicated backend connections and certificate
  validation. WAF supports `Microsoft_HTTPDDoSRuleSet`; rule sensitivity no
  longer accepts `None`.
- `2.82.0` settings expose L4 client-IP preservation, probes expose proxy-
  protocol headers, and managed-rule sets support disabled rules by default.
- `2.84.0` SSL certificates support dedicated backend connections.
- `2.87.0` SSL-certificate create/update accepts `--hsm` for Managed HSM.

## Private endpoints and Private Link

### Multiple IPs and IPv6

`2.76.0` Private Link service creation supports multiple IP configurations.
`2.85.0` private-endpoint create/update adds `--ip-version-type` for IPv6.

### Newly recognized providers

- `2.69.0`: `Microsoft.HealthDataAiservices/deidservices`
- `2.74.0`: `Microsoft.FluidRelay/fluidRelayServers` and
  `Microsoft.VideoIndexer/accounts`
- `2.80.0`: `Microsoft.Security/privateLinks`
- `2.82.0`: `Microsoft.Maps/accounts`
- `2.85.0`: `Microsoft.DurableTask/schedulers`
- `2.88.0`: `Microsoft.HorizonDB/clusters`
- `2.89.0`: `Microsoft.HardwareSecurityModules/cloudHsmClusters`

## Network virtual appliances, DDoS, and diagnostics

- `2.69.0` network virtual appliances can reimage associated VMs.
- `2.74.0` Network Watcher packet capture supports a ring buffer.
- `2.82.0` NVA accepts interface configurations; flow-log accepts record types.
- `2.83.0` adds `az network virtual-network-appliance` and
  `ddos-custom-policy` groups.
- `2.87.0` virtual-appliance create/update accepts private-IP address version.
- `2.88.0` DDoS custom policy supports frontend-IP associations; Traffic
  Manager create/update accepts record-type filtering.
- `2.89.0` virtual-appliance migration can move an NVA to internal-LB
  architecture.

## Other networked service controls

- `2.70.0` IoT Hub minimum TLS is covered in the compute/app reference.
- `2.76.0` Event Hubs namespace `nsp-configuration show/list` exposes Network
  Security Perimeter configuration.
- `2.82.0` Azure Maps private-endpoint recognition is listed above.
- `2.83.0` storage IPv6 endpoints/network rules are in the data reference.
