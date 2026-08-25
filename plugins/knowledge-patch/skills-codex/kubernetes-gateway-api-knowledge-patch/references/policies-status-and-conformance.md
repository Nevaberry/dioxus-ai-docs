# Policies, Status, and Conformance

Use this reference when configuring backend TLS, retry or persistence policy,
or implementation capability reporting.

## Track BackendTLSPolicy feature levels

In 1.3.0, `BackendTLSPolicy.subjectAltNames` moved from Core to Extended.
Implementation support for the field is therefore optional. Target
references also gained CEL validation.

BackendTLSPolicy graduated to the Standard channel in 1.4.0. It reports
reference resolution with `ResolvedRefs`; invalid-policy behavior and
target-reference conflict handling are standardized. SAN validation takes
precedence over Hostname validation, so do not require both checks to decide
the same policy outcome.

## Select certificate authorities

`BackendTLSPolicy.validation.wellKnownCACertificates` gained support for
implementation-specific values in 1.5.0 in addition to standardized choices.
Only emit a non-standard value after confirming the target implementation's
contract.

In 1.6.0, BackendTLSPolicy became usable with additional route types and the
maximum number of certificate-authority references increased from 8 to 16.
Clients and admission helpers should accept the larger list without assuming
that every implementation-specific route combination is available.

## Configure destination-wide retry budgets

Experimental `XBackendTrafficPolicy` replaced `BackendLBPolicy` in 1.3.0. It
combines the earlier session-persistence settings with retry budgets applied
across all endpoints of a destination Service.

The retry budget uses nested fields:

```yaml
budget:
  percent: 20
  interval: 10s
```

Use `budget.percent` and `budget.interval`; the former flat
`budgetPercent` and `budgetInterval` field names are obsolete.

`XBackendTrafficPolicy` is Extended and has no conformance feature name.
Verify its presence and exact behavior with the implementation.

## Validate session persistence

A session-persistence `cookieConfig` is valid only when the associated
persistence type is `Cookie` (1.5.0). Reject or repair mismatched
configurations before submission.

The Experimental SessionPersistence API removed `idleTimeout` in 1.6.0.
Remove the field rather than attempting to translate it to a renamed
SessionPersistence option.

## Read GatewayClass capability status

Percentage request mirroring introduced in 1.3.0 is a Standard-channel,
Extended feature. HTTPRoute implementations advertise it with
`HTTPRouteRequestPercentageMirror` in
`GatewayClass.status.supportedFeatures`.

The `supportedFeatures` reporting field itself graduated to the Standard
channel in 1.4.0. Consumers can use it for implementation feature discovery,
but must still use implementation-specific checks for experimental Extended
features that have no feature name.

## Separate mesh and Gateway capabilities

The Experimental `Mesh` resource introduced in 1.4.0 provides mesh-wide
configuration and reports supported features. It lets an implementation
expose mesh capabilities separately from Gateway capabilities.

Capability consumers must query the appropriate status surface; a feature
reported for a GatewayClass does not by itself establish a mesh capability,
and a Mesh capability does not establish Gateway support.
