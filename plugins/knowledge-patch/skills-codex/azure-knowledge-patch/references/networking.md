# Networking

Use this reference for current compatibility details and exact command or schema changes.

## Application Gateway and WAF

### Application Gateway and private-endpoint values (2.80.0)

`az network application-gateway http-settings` now supports dedicated backend
connections and certificate validation. WAF managed rules accept
`Microsoft_HTTPDDoSRuleSet`, while WAF rule sensitivity no longer accepts
`None`; `az network private-endpoint-connection` recognizes
`Microsoft.Security/privateLinks`.

### Application Gateway dedicated-backend certificates (2.84.0)

The `az network application-gateway ssl-cert` command group now supports
dedicated backend connections.

### Application Gateway FIPS (2.79.0)

`az network application-gateway create` and `update` accept `--enable-fips`
to enable FIPS mode.

### Application Gateway transport and WAF controls (2.82.0)

`az network application-gateway settings` exposes
`enableL4ClientIpPreservation` through `--enable-l4-client-ip`, while probe
commands expose `enableProbeProxyProtocolHeader` through
`--enable-proxy-header`. WAF managed-rule rule-set commands also support
disabled rules by default.

### Application Gateway WAF and private-link networking (2.76.0)

Application Gateway WAF policy output includes the read-only
`computedDisabledRules` property, and custom-rule `groupByVariables` accepts
`GeoLocationXffHeader` and `ClientAddrXffHeader`. Private Link service creation
now supports multiple IP configurations.

### Microsoft default WAF ruleset (2.72.0)

Application Gateway WAF policy managed-rule ruleset commands now accept the
`Microsoft_DefaultRuleSet` ruleset type.

## Gateways and VPN

### NAT64 on Standard V2 NAT gateways (2.89.0)

`az network nat gateway` accepts `--nat64` to enable or disable NAT64 on a
Standard V2 NAT gateway.

### Network appliance diagnostics and high-bandwidth gateways (2.71.0)

`az network virtual-appliance get-boot-diagnostic-log` retrieves boot
diagnostic logs. `az network vnet-gateway create` accepts
`--enable-high-bandwith-vpn-gateway`; the CLI spelling is `bandwith`.

### Network gateway resiliency and peering routes (2.86.0)

`az network express-route gateway` supports Virtual WAN gateway resiliency
APIs. Route-table create/update also accepts `--disable-peering-route` to
disable peering routes.

### Standard V2 NAT Gateway IPv6 and VNet output (2.77.0)

Standard V2 NAT gateways now support IPv6 public IP addresses and prefixes.
`az network vnet show` and `list` output also exposes
`defaultPublicNatGateway`.

### VNet gateway identity and VPN authentication (2.83.0)

`az network vnet-gateway` adds identity-related parameters and a subgroup.
`az network vpn-connection` adds `--auth-type` and `--cert-auth`.

### VNet Gateway insights and failover (2.77.0)

The `az network vnet-gateway` command group now supports VNet Gateway
insights and failover.

### VNet gateways without a public IP (2.78.0)

`az network vnet-gateway create` no longer requires a public IP.

### VPN gateway migration and output (2.74.0)

The `az network vnet-gateway migration` command group supports VPN gateway
migration. `az network vpn-connection show` also returns new virtual-network
gateway properties.

## Network appliances and observability

### Network appliance, flow-log, and Maps endpoint support (2.82.0)

`az network virtual-appliance` accepts `--nva-interface-configurations`, and
`az network watcher flow-log` accepts `--record-types`. Private-endpoint
connections now recognize provider `Microsoft.Maps/accounts`.

### Packet-capture ring buffers (2.74.0)

`az network network-watcher packet-capture` now supports packet captures that
include a ring buffer.

### Virtual appliance migration to ILB architecture (2.89.0)

`az network virtual-appliance migration` now supports migrating a network
virtual appliance to internal-load-balancer architecture.

### Virtual network appliance and custom DDoS policy commands (2.83.0)

The new `az network virtual-network-appliance` and
`az network ddos-custom-policy` groups expose Virtual Network Appliance and
DDoS policy customization operations.

## Network defaults and SKU retirements

### Basic Load Balancer is retired but still operating (network-defaults-and-sku-retirements)

Basic Load Balancer retired on September 30, 2025. Existing instances remain
operational but are unsupported and have no SLA; Cloud Services Extended
Support deployments are exempt and can still create and use Basic load
balancers.

Plan downtime because migration to Standard is not a simple mixed-SKU
transition. Make every frontend and backend-VM public IP static before
disassociating it or its address can be lost; all public IPs and load
balancers involved must use matching SKUs. A Standard public IP also needs an
NSG allow rule for inbound traffic. A public Standard load balancer needs an
outbound rule for its backend, while a private load balancer needs a NAT
gateway or instance-level public IPs.

### Basic public IP is retired with resource-specific upgrade paths (network-defaults-and-sku-retirements)

Basic public IP retired on September 30, 2025, but existing addresses likewise
continue without support or an SLA. Cloud Services Extended Support can still
create Basic addresses through non-portal tools and continue using them.

A disassociated address can be upgraded when zone redundancy is not required;
zone redundancy requires creating a new Standard address, and an address used
by a load balancer must match its regional or global tier. Associated
addresses require the owning resource's migration path: a Basic load balancer
must be replaced, gateways must be migrated, and per-instance public-IP
configurations on a uniform VM scale set are not Public IP resources and must
be replaced rather than upgraded. Basic addresses attached to Application
Gateway v1 are exempt until that gateway SKU retires.

### Changing subnet privacy requires VM deallocation (network-defaults-and-sku-retirements)

Make a subnet private by disabling default outbound access, then stop and
deallocate its existing VMs so the change reaches their NICs; the same
deallocation is required when changing back to a nonprivate subnet.

```azurecli
az network vnet subnet update --resource-group rgname --vnet-name vnetname \
  --name subnetname --default-outbound false
```

A default outbound IP can remain assigned, and its portal or Advisor alert can
remain visible, when a VM on a nonprivate subnet also has NAT gateway or
UDR-based egress. The explicit path takes precedence, but fully removing the
implicit IP and alert requires both a private subnet and VM deallocation.
Use a NAT gateway, a Standard load balancer outbound rule, a Standard public
IP, or a firewall/NVA reached through a UDR for explicit egress.

### New virtual networks become private by default (network-defaults-and-sku-retirements)

With the API version released after March 31, 2026, subnets in newly created
virtual networks default `defaultOutboundAccess` to `false`, so VMs need an
explicit outbound method to reach public Azure endpoints and the internet.
The portal already uses this private default, while older API
versions—including templates or Terraform configurations that deliberately
select one—continue to leave an omitted property null and implicitly permit
default outbound access.

Existing virtual networks are unchanged, including new VMs added to their
existing nonprivate subnets. A new subnet can still explicitly opt into
default outbound access when compatibility requires it.

### Private-subnet routing has exceptions (network-defaults-and-sku-retirements)

In a private subnet, a UDR whose next hop is `Internet` does not itself provide
outbound access. This includes service-tag exception routes intended to bypass
an NVA; they fail without another explicit outbound method, whereas service
endpoints are unaffected. Same-region Azure Storage remains reachable, and
should be constrained with NSGs; the private-subnet setting does not apply to
delegated or managed PaaS subnets.

An IP-address-based load-balancer backend pool still receives default outbound
access because of a known issue. Attach a NAT gateway to its VM subnet when
secure, deterministic outbound behavior is required.

## Network service controls

### Network listing and certificate authentication (2.88.0)

`az network vnet list` without `--resource-group` now returns all virtual
networks. `az network vpn-connection create` no longer requires
`--shared-key` when `--auth-type Certificate` is used.

### Network provisioning controls (2.87.0)

Virtual-network create/update operations accept
`--summarized-gateway-prefixes`. Application Gateway SSL-certificate
create/update accepts `--hsm` for Managed HSM, and virtual network appliance
create/update accepts `--private-ip-address-version`.

### Network resource coverage (2.88.0)

`az network ddos-custom-policy` now supports frontend IP configuration
associations, and Traffic Manager profile create/update accepts
`--record-type` for record-type filtering. Private-endpoint connections now
recognize `Microsoft.HorizonDB/clusters`.

### Network service controls (2.69.0)

Load-balancer creation accepts multiple zones through `--frontend-ip-zone`,
and route-server create/update gains `--auto-scale-config`. Network virtual
appliances can reimage associated VMs, and private endpoint connections now
recognize `Microsoft.HealthDataAiservices/deidservices`.

### NIC private-address prefix length (2.70.0)

`az network nic ip-config create` and `az network nic ip-config update` accept
`--private-ip-address-prefix-length`.

### Standard V2 network resources (2.75.0)

NAT gateways, public IPs, and public IP prefixes created or managed through
`az network` now support the Standard V2 SKU.

## Private Link and private endpoints

### Additional private-endpoint providers (2.74.0)

`az network private-endpoint-connection` now recognizes
`Microsoft.FluidRelay/fluidRelayServers` and
`Microsoft.VideoIndexer/accounts`.

### Private endpoints for IPv6 and Durable Task (2.85.0)

Private-endpoint create/update accepts `--ip-version-type` for IPv6, and
private-endpoint connections now recognize the
`Microsoft.DurableTask/schedulers` provider.

## Virtual networks, subnets, and IPAM

### Subnet IPAM pool allocation (2.75.0)

`az network vnet subnet create` and `az network vnet subnet update` now
support allocating subnet address space from an IPAM pool.

### Virtual-network resilience and IPAM allocation (2.68.0)

Virtual network gateway create/update commands gain `--resiliency-model`,
while virtual network create/update commands gain
`--ipam-pool-prefix-allocations` for IPAM pool prefix allocations.
