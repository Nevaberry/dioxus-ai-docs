# Temporal Cloud Authentication, Connectivity, and Migration

## Apply API-key ownership and limits

Cloud API keys inherit RBAC from their linked user or Service Account.

- Users manage their own keys.
- Global Administrators and Account Owners manage every Service Account key.
- Namespace Admins manage Namespace-scoped Service Account keys.
- A Service Account may create its own replacement key regardless of its
  configured permissions, but needs the normal permission to delete the old
  key.
- Disabling account-wide key creation does not invalidate existing keys.

The limits are 10 non-expired keys per user, 20 per Service Account, and a
maximum lifetime of two years.

```bash
tcld apikey create \
  --name worker-key \
  --duration 90d \
  --service-account-id <service-account-id>
```

## Enable API-key authentication per Namespace

API keys are an alternative to mTLS only when API-key authentication was
enabled for the Namespace during setup.

The same key can authenticate SDKs and the Temporal CLI against
`<namespace>.<account>.tmprl.cloud:7233`. `tcld`, Terraform, and the Cloud Ops
API use API keys for control-plane operations.

## Understand what Connectivity Rules enforce

Creating an AWS PrivateLink endpoint or GCP Private Service Connect endpoint
and attaching a Connectivity Rule are separate steps.

- With no rules, a Namespace accepts public traffic and configured private
  paths.
- Attaching any rule immediately rejects every path that no rule matches.
- The Web UI is not subject to Connectivity Rule enforcement.
- An AWS rule is optional. It uses a `vpce-...` endpoint ID and an `aws-`
  region.
- A GCP rule is required to move PSC out of `Pending`. It needs the PSC
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

## Replace rules and attachment sets safely

Rules cannot be updated in place. Replace a rule when its properties change.
A Namespace's attached rules are also replaced as a complete set rather than
patched incrementally.

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

`--remove-all` makes the Namespace public again. Enabling Stable IPs later
requires recreating and reattaching the public rule.

Only Account Admins and Account Owners can manage rules through `tcld`,
Terraform, or the Cloud Ops API. Default limits are five private rules per
Namespace, 50 private rules per account, and one public rule per account.

## Configure private DNS and TLS routing

Provisioning private connectivity does not change client name resolution.
Configure private DNS, or point the client at its PrivateLink DNS name or PSC
IP and explicitly override the TLS server name.

The correct TLS server name depends on topology and authentication:

- Single-region mTLS uses the Namespace endpoint as SNI.
- Single-region API-key authentication uses the regional API endpoint, such
  as `us-east-1.aws.api.temporal.io`.
- A multi-region Namespace uses its active regional endpoint.

The wrong SNI can reset TLS even when port 7233 is reachable.

```bash
export TEMPORAL_ADDRESS=vpce-0123456789abcdef.example.vpce.amazonaws.com:7233
export TEMPORAL_NAMESPACE=orders.example
export TEMPORAL_API_KEY=<key-secret>
export TEMPORAL_TLS_SERVER_NAME=us-east-1.aws.api.temporal.io
temporal workflow count
```

## Reach the control plane privately

Programmatic control-plane clients require `saas-api.tmprl.cloud`.
Its AWS PrivateLink service is available only in `us-west-2`:

```text
com.amazonaws.vpce.us-west-2.vpce-svc-0c57a5930b6f6be0e
```

Clients in other regions must peer with a VPC containing that endpoint in
`us-west-2`. PrivateLink does not make the control plane private-only; its
public endpoint remains available. Private DNS for the endpoint requires VPC
DNS hostnames and DNS support.

## Choose a live-migration mode

Automated migration uses Workflow replication to move running executions
between self-hosted Temporal and Cloud, or between Cloud regions and providers,
without restarting those executions.

Manual migration instead repoints Clients and Workers while executions on the
old Namespace finish naturally.
