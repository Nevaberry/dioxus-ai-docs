# Identity and Policy

## Client introduction and identity

Nomad clients can join with signed JWT introduction tokens (since 1.11.0). Token
claims can constrain node names, node pools, and TTLs. Server enforcement levels
control the introduction policy and emit violation logs and metrics. After a client
registers, servers issue and rotate a client identity used for RPC authentication
alongside mTLS.

```shell
nomad node intro create
nomad agent -client-intro-token
nomad node identity get
nomad node identity renew
```

## ACL behavior and policy validation

The `/v1/acl/token/self` response changed in the 1.10-upgrade batch. With ACLs
disabled it returns `200` and a body saying ACLs are disabled. With ACLs enabled
but no valid token it returns `403`. Code that expected `404` in both cases must
distinguish the new responses.

Policy writes are strict starting in 1.10.6: duplicate or invalid keys are rejected
instead of ignored. Existing affected policies continue to operate, but correct
their source documents before trying to write them again.

Workload identity tokens can list and retrieve policies through the ACL API (since
1.11.0).

## OIDC assertions and PKCE

OIDC auth methods support private-key JWT client assertions instead of a client
secret (batch 1.10.0). PKCE works with either client secrets or assertions when
`OIDCEnablePKCE: true` is set. Confirm that the identity provider also supports
PKCE and enable it there when required.

## Workload identity replaces allocation tokens

Token-based Consul and Vault allocation authentication has been removed. A task
with a `template` block no longer receives a Consul identity as a side effect.
Declare the identity that the job needs rather than relying on either legacy
behavior.

Consul tokens issued through workload identity carry the issuing Nomad client's
node ID in their metadata (since 2.0.5), which can be used to trace the token to
the client.

## Job specification secrets

The `secret` block fetches values from Nomad, Vault, or a custom secret-provider
plugin for jobspec interpolation (since 1.11.0). Reference a fetched value as
`${secret.secret_name.key}`. As of 2.0.5, task secrets
also interpolate in service check `Header` and `Args` fields and service `Tags`.

## Sentinel and namespace governance

Nomad Enterprise can evaluate dynamic host-volume specifications with Sentinel
during creation, enforce per-namespace host-volume capacity quotas, and validate
the requested node pool against the namespace's node-pool configuration (batch
1.10.0).

`nomad sentinel apply` requires an explicit `-scope` option. Update automation
that previously relied on an implicit scope.

## Quota API migration

The quota `variables_limit` field and Go API `QuotaSpec.VariablesLimit` are
deprecated for removal in 1.12. Use `region_limit.storage.variables` and
`QuotaSpec.RegionLimit.Storage.Variables`. In the 1.10.0 API, the type of
`QuotaSpec.RegionLimit` also changes from `Resources` to `QuotaResources`.

In Nomad Enterprise 2.0.5, disabling the use of cores in a quota no longer blocks
jobs that specify either core or CPU resources.

## Server-join authorization

Unauthenticated `nomad server join` and Join Agent API calls are deprecated in
2.0.4 and require a token with `agent:write` in 2.1.0 (batch 2.0-upgrade). Direct
the command to the region leader when adding a node and to the authoritative
region when federating. For a new cluster, prefer `server_join` with gossip
encryption and mTLS.

## Enterprise licensing

Automated Enterprise license utilization reports contain detailed product-usage
information starting in 1.10.6. Nomad Enterprise 2.0.0 also adds license and
configuration changes for IBM Passport Advantage Online (PAO).

Before an Enterprise server upgrade to 1.6.0 or later, follow the
upgrade-procedure guidance and validate the license with the target binary:

```shell
nomad license inspect
```
