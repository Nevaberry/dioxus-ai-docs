# Cloud Security, Connectivity, and Migration

## API-key ownership and limits

Temporal Cloud API keys inherit RBAC permissions from the linked user or
Service Account.

- Users manage their own keys.
- Global Administrators and Account Owners manage all Service Account keys.
- Namespace Admins manage Namespace-scoped Service Account keys.
- A Service Account may create its own replacement key regardless of its
  configured permissions, but needs the normal permission to delete the old
  key.
- Disabling account-wide key creation does not invalidate existing keys.

Limits are 10 non-expired keys per user, 20 per Service Account, and a maximum
lifetime of two years.

```bash
tcld apikey create \
  --name worker-key \
  --duration 90d \
  --service-account-id <service-account-id>
```

## Namespace API-key authentication

API keys are an alternative to mTLS only if API-key authentication was enabled
for the Namespace during setup. An enabled key can authenticate SDKs and the
Temporal CLI at:

```text
<namespace>.<account>.tmprl.cloud:7233
```

The same key type is used by `tcld`, Terraform, and the Cloud Ops API for
control-plane operations.

## Connectivity Rules select paths

Creating an AWS PrivateLink endpoint or GCP Private Service Connect endpoint
and attaching a Connectivity Rule are separate operations.

- With no rules, a Namespace accepts public traffic and configured private
  paths.
- Attaching any rule immediately rejects every unmatched path.
- The Web UI is not subject to Connectivity Rule enforcement.
- An AWS rule is optional and uses a `vpce-...` endpoint ID and an `aws-`
  region.
- A GCP rule is required to move PSC out of `Pending` and needs the PSC
  connection ID, a `gcp-` region, and the GCP project ID.

```bash
tcld connectivity-rule create \
  --connectivity-type private \
  --connection-id "vpce-abcde" \
  --region "aws-us-east-1"

tcld connectivity-rule create \
  --connectivity-type private \
  --connection-id "1234567890" \
  --region "gcp-us-central1" \
  --gcp-project-id "my-project-123"
```

## Rule replacement semantics

Connectivity Rules cannot be updated in place. A Namespace's rule attachments
are replaced as a complete set, not patched.

Stage a public rule alongside private rules before removing public access:

```bash
tcld namespace set-connectivity-rules \
  --namespace "orders.example" \
  --connectivity-rule-ids "public-rule" \
  --connectivity-rule-ids "private-rule"

tcld namespace set-connectivity-rules \
  --namespace "orders.example" \
  --connectivity-rule-ids "private-rule"
```

`--remove-all` makes the Namespace public again. Only Account Admins and
Account Owners can manage rules through `tcld`, Terraform, or the Cloud Ops
API.

Default limits are:

- five private rules per Namespace;
- 50 private rules per account; and
- one public rule per account.

Enabling Stable IPs later requires recreating and reattaching the public rule.

## Private endpoint DNS and TLS routing

Provisioning private connectivity does not alter client name resolution.
Configure private DNS, or point the client directly at the PrivateLink DNS
name or PSC IP and override its TLS server name.

The required SNI depends on topology and authentication:

- Single-region mTLS uses the Namespace endpoint.
- Single-region API-key authentication uses the regional API endpoint, such as
  `us-east-1.aws.api.temporal.io`.
- A multi-region Namespace uses its active regional endpoint.

An incorrect TLS server name can reset the TLS connection even when the client
can reach port 7233.

```bash
export TEMPORAL_ADDRESS=vpce-0123456789abcdef.example.vpce.amazonaws.com:7233
export TEMPORAL_NAMESPACE=orders.example
export TEMPORAL_API_KEY=<key-secret>
export TEMPORAL_TLS_SERVER_NAME=us-east-1.aws.api.temporal.io
temporal workflow count
```

## Private control-plane connectivity

Programmatic control-plane clients require `saas-api.tmprl.cloud`. Its AWS
PrivateLink service is available only in `us-west-2`:

```text
com.amazonaws.vpce.us-west-2.vpce-svc-0c57a5930b6f6be0e
```

Other regions must peer with a VPC containing that endpoint in `us-west-2`.
PrivateLink does not make the control plane private-only; the public endpoint
remains available. Private DNS for the endpoint requires VPC DNS hostnames and
DNS support.

## Live migration

Automated bidirectional migration uses Workflow replication to move running
executions:

- between self-hosted Temporal and Temporal Cloud; or
- between Cloud regions and providers.

The running executions do not need to restart. Manual migration instead
repoints Clients and Workers while executions on the old Namespace finish
naturally.
