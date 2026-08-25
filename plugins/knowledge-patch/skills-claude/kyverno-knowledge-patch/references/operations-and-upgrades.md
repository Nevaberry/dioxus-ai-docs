# Operations and Upgrades

## Helm Chart Pairing

Kyverno 1.16.0 uses Helm chart 3.6.0:

```bash
helm repo update
helm upgrade --install kyverno kyverno/kyverno \
  -n kyverno \
  --version 3.6.0
```

Kyverno 1.17.0 uses Helm chart 3.7.0:

```bash
helm repo update
helm upgrade --install kyverno kyverno/kyverno \
  -n kyverno \
  --version 3.7.0
```

Check the deployed application and chart versions independently before an
upgrade. Render the chart with site-specific values and validate CRD/API
availability before applying policy manifests that use a promoted API version.

## Policies Chart Customization

In 1.18.0, the policies Helm chart can configure `ValidatingPolicy` exclusions
by:

- namespace;
- subject;
- resource rules;
- match conditions.

It also supports `auditAnnotation` configuration and per-policy annotation
overrides. Review rendered policies rather than assuming a chart-level
exclusion maps directly to webhook routing; Kyverno-specific CEL
`matchConditions` are evaluated by Kyverno.

## API and SDK Consumers

As of 1.17.0, CEL API types live in the lighter-weight `kyverno/api`
repository for Go consumers. The Kyverno SDK lives in `kyverno/sdk` for
controllers and other integrations.

Update Go module imports intentionally when consuming policy types or
embedding policy evaluation. The SDK can also support service-edge
authorization integrations that load, compile, and evaluate policies.

## Legacy Policy Lifecycle

`ClusterPolicy` and `CleanupPolicy` are deprecated in 1.17.0. They remain
functional, but the published schedule limits them to critical fixes in 1.18
and 1.19 and plans removal in 1.20.

Migration priorities:

1. replace legacy `validate.pattern` rules with CEL expressions in
   `ValidatingPolicy`;
2. choose the specialized validating, mutating, generating, image-validating,
   or deleting kind;
3. choose a namespaced kind when ownership and effects should stay within one
   namespace;
4. move manifests to `policies.kyverno.io/v1` where the installed CRDs serve
   it;
5. test policy behavior, exception semantics, reports, Events, and metrics.

## Community Support Window

Starting with 1.18.0, community patch support covers only the current and
immediately previous releases, for roughly three months. Patches in that
window are limited to critical or high-severity CVEs and other critical fixes.

Operators should schedule frequent upgrades. Environments that require a longer
maintenance window need an explicit longer-term commercial support plan.

## Upgrade Verification Checklist

- Confirm the Kyverno application version and matching chart version.
- Confirm which CEL policy API versions the installed CRDs serve.
- Render chart customizations and inspect exclusions and annotations.
- Update report integrations to `openreports.io`.
- Review HTTP allowlists, blocklists, and the namespaced HTTP default.
- Test image verification, including Cosign and private-registry credentials.
- Exercise policies and exceptions with the CLI.
- Verify report filtering, success Events, metrics TLS, and HPA behavior.
- Track legacy-policy removal and the shortened community support window.
