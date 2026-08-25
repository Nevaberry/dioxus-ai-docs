# Policies, Security, and Capabilities

Use this reference for backend TLS validation, Gateway certificates,
authentication, backend traffic policy, session persistence, and feature
advertisement.

## BackendTLSPolicy

### Subject alternative names are Extended

`BackendTLSPolicy.subjectAltNames` moved from Core to Extended in 1.3.0.
Support for the field is optional even when an implementation supports the
policy. Target references also receive CEL validation.

Check the implementation's advertised or documented support before generating
SAN-dependent policy. Do not infer support solely from the presence of the
CRD.

### The policy is Standard

`BackendTLSPolicy` graduated to the Standard channel in 1.4.0. Its status and
conflict behavior were tightened:

- Reference resolution is reported with `ResolvedRefs`.
- Invalid-policy behavior is standardized.
- Target-reference conflict handling is standardized.
- SAN validation takes precedence over Hostname validation.

The resource's Standard status does not turn its Extended fields into Core
features.

### Trust configuration can be implementation-specific

`BackendTLSPolicy.validation.wellKnownCACertificates` can use
implementation-specific values in addition to standardized choices (since
1.5.0). Such values reduce portability; accept or emit one only when the
target implementation defines its semantics.

### More routes and CA references are supported

`BackendTLSPolicy` can be combined with additional Route types in 1.6.0.
The maximum number of certificate-authority references increased from 8 to
16. Controllers and validation code should use the newer limit while still
checking whether the selected Route type is supported.

## Gateway certificate features

Two certificate capabilities are Standard since 1.5.0:

- Client-certificate validation for TLS terminated at a Gateway.
- Selection of the Gateway client certificate used for TLS connections to
  backends.

These cover different connection legs. A deployment that validates downstream
clients and authenticates to an upstream backend needs both behaviors
configured and supported.

## External authentication

HTTP external authentication is an Experimental HTTPRoute feature introduced
in 1.4.0. It allows a Route to delegate authorization to an external service.

Experimental authentication expanded to Gateway-level configuration in 1.5.0.
Check whether the implementation supports route scope, Gateway scope, or both,
and keep policy placement consistent with the desired enforcement boundary.

## XBackendTrafficPolicy

`XBackendTrafficPolicy` replaced `BackendLBPolicy` in 1.3.0. It combines the
earlier session-persistence settings with Experimental retry budgets across
all endpoints of a destination Service.

Retry-budget fields are nested:

```yaml
budget:
  percent: 20
  interval: 10s
```

Use `budget.percent` and `budget.interval`; the earlier flat names
`budgetPercent` and `budgetInterval` are not the final API.

As an Experimental `X` kind, this policy is Extended and has no conformance
feature name. Its availability must be checked with the implementation rather
than inferred from a conformance profile.

## Session persistence validation

A session-persistence `cookieConfig` is valid only when the associated
persistence type is `Cookie` (since 1.5.0). Reject configurations that attach
cookie settings to another persistence type.

The `idleTimeout` field was removed from the Experimental SessionPersistence
API in 1.6.0. Remove it from manifests and generators instead of treating it
as an ignored hint.

## Supported-feature reporting

`GatewayClass.status.supportedFeatures` is a Standard capability-reporting API
since 1.4.0.

Percentage request mirroring is a Standard-channel Extended feature introduced
in 1.3.0. Implementations advertise HTTPRoute support with
`HTTPRouteRequestPercentageMirror`. Because Extended support is optional,
feature status should be checked before deploying percentage mirrors.

Not every Experimental Extended resource has a conformance feature name.
`XListenerSet` and `XBackendTrafficPolicy`, for example, require a direct
implementation support check.

The Experimental `Mesh` resource from 1.4.0 reports mesh-supported features
separately, allowing mesh capabilities to be exposed independently of Gateway
capabilities.

## Policy evaluation checklist

1. Resolve target references and emit `ResolvedRefs` correctly.
2. Apply SAN precedence and distinguish Extended fields from Core support.
3. Restrict implementation-specific CA values to their defining controller.
4. Check Route-type policy support and the 16-reference CA limit.
5. Verify both frontend and backend certificate capabilities for mutual TLS.
6. Place authentication at the supported and intended enforcement scope.
7. Validate session-persistence type relationships and remove `idleTimeout`.
8. Consult feature status, conformance names, and implementation documentation
   as appropriate for each capability.
