# Security, Identity, and Governance

## Allocation and workload identity

### Removed token-based allocation authentication

Since 1.10.0, deprecated token-based allocation authentication for Consul and
Vault has been removed. A task containing a `template` block also no longer
receives an implicit Consul identity; jobs must not rely on that side effect.

### Client introduction and identity

Since 1.11.0, clients can join with signed JWT introduction tokens that
constrain node names, node pools, and TTLs. Server enforcement levels control
introduction policy and emit violation logs and metrics.

After registration, servers automatically issue and rotate a client identity
for RPC authentication as a second layer alongside mTLS.

```shell
nomad node intro create
nomad agent -client-intro-token <token>
nomad node identity get
nomad node identity renew
```

### ACL API access with workload identities

Since 1.11.0, workload identity tokens can list or retrieve policies through
the ACL API.

### Consul workload-token metadata

Since 2.0.5, Consul tokens created through workload identity carry the issuing
Nomad client's node ID in their metadata, allowing a token to be traced to the
client that issued it.

## OIDC authentication

Since 1.10.0, OIDC auth methods support private key JWT client assertions as an
alternative to sending a client secret. PKCE works with client secrets or
assertions and is enabled with `OIDCEnablePKCE: true`. The OIDC provider must
support PKCE and may need it enabled.

## ACL policy validation

Nomad 1.10.6 rejects policy writes containing duplicate or invalid keys instead
of silently ignoring them. Existing affected policies keep working, but their
source documents must be corrected before they can be written again.

## Sentinel and quotas

### Required Sentinel scope

Since 1.10.0, `nomad sentinel apply` requires `-scope`.

### Dynamic host volume governance

Since 1.10.0, Nomad Enterprise can evaluate volume specifications with Sentinel
during creation, apply per-namespace host-volume capacity quotas, and validate
a requested node pool against the namespace's node-pool configuration.

### Enterprise quota core controls

Since 2.0.5, disabling the use of cores in an Enterprise quota no longer blocks
jobs that specify either cores or CPU resources.

## Enterprise licensing

### License utilization reporting

The `1.10-upgrade` guidance for Nomad Enterprise 1.10.6 adds detailed
product-usage information to automated license utilization reporting.

### IBM PAO licensing

The `2.0-upgrade` guidance for Nomad 2.0.0 includes license and configuration
changes that enable IBM Passport Advantage Online (PAO).
