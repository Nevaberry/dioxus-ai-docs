# Auditing and Inference

Use this reference for protected-operation audit trails, querying audit events
across a cluster, trace correlation, and request-scoped external inference
credentials.

## Audit logging

### Record protected API operations (since 1.17.0)

Qdrant can audit API operations that require authentication or authorization.
Enable audit logging when protected actions need an operational or compliance
record. Define retention and access policy for the resulting data because the
records describe authenticated activity.

Audit coverage is tied to operations requiring authentication or authorization;
do not assume it is a general-purpose trace of every internal action.

### Query audit events cluster-wide (since 1.18.0)

Use the audit-log query endpoint to aggregate entries from every cluster node.
Returned details include timestamp, API method, authentication type, access
result, and client information. Filter by time range or any field value rather
than reading each node's log file independently.

A practical investigation flow is:

1. Bound the query by the narrowest useful time window.
2. Filter on request, access-result, authentication, client, or operation data.
3. Use a tracing identifier to join the event to client and distributed logs.
4. Expand the time range only when the first query is insufficient.

Cluster aggregation makes the endpoint the preferred view when a request could
have reached any peer.

### Correlate audit entries with traces (since 1.18.0)

Audit entries store a caller-supplied tracing ID when the request contains one
of these headers:

- `x-request-id`
- `x-tracing-id`
- `traceparent`

Propagate one of them consistently from the application boundary. Preserve the
same value in client logs and downstream tracing so an audited operation can be
followed across systems. Avoid placing secrets or personal data in correlation
IDs.

## External inference credentials

### Supply credentials per request (since 1.17.0)

External inference-provider API keys can be supplied in the request header.
This lets credentials accompany an individual inference request rather than
being shared as one static server-side value.

Use request headers when credentials are tenant-specific, short-lived, or
selected dynamically. Apply normal secret-handling controls:

- Send credentials only over authenticated encrypted connections.
- Prevent request headers containing keys from entering ordinary access logs,
  traces, exception messages, or audit metadata.
- Scope keys to the minimum provider permissions required.
- Keep key selection separate from user-controlled arbitrary header forwarding.
- Rotate or revoke the key without requiring collection recreation.

## Operational checks

- Exercise both allowed and denied protected operations and confirm their audit
  records are queryable.
- Query across the cluster rather than inspecting only the node that received a
  client connection.
- Verify time-range and field filtering against realistic event volume.
- Confirm one correlation header survives proxies and reaches the audit entry.
- Redact external inference keys at every logging and tracing boundary.
- Test concurrent tenants with different request-scoped provider credentials.
