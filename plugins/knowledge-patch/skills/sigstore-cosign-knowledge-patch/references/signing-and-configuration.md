# Signing and service configuration

## Service discovery

Service URLs are fetched from the TUF signing configuration by default. Treat that configuration as the source of the effective signing-service endpoints unless an explicit workflow decision overrides it.

Trusted-root and signing-config creation can use default services. This supports standard configuration creation without manually duplicating the service list.

## Base configuration precedence

`--base-config` can seed a signing configuration. The service definitions are then overridden, so base-file service entries must not be assumed to survive into the effective configuration.

Use this review sequence:

1. inspect the base configuration inputs;
2. create or derive the signing configuration;
3. inspect the effective service definitions after overrides;
4. confirm that the resulting endpoints match the intended trust and availability policy.

This precedence matters when a base file mixes general defaults with environment-specific service URLs.

## Trusted-root creation

Trusted-root creation can use default services. Keep the trusted-root artifact and signing configuration conceptually separate: one supplies verification trust material, while the other supplies signing-service configuration.

Do not infer the verification trust path merely from the URLs used during signing.

## TSA mutual TLS

TSA clients support mutual TLS when a signing configuration is used. Put the TSA client-authentication requirements into the signing-configuration workflow and test them with the effective endpoint selection.

A plain connectivity check is insufficient when the TSA requires a client certificate. Confirm that the configured client can authenticate and obtain the timestamp required by the signing path.

## Rekor v2 signed timestamps

Rekor v2 entries automatically require a signed timestamp. Rekor v2 signing with Fulcio enforces the TSA requirement.

Consequences for a signing workflow:

- TSA availability is a prerequisite, not an optional enhancement.
- The effective signing configuration must resolve to a usable timestamp service.
- TSA mTLS material must be available when the timestamp service requires it.
- A workflow should fail as a signing failure when it cannot obtain the required signed timestamp.

## Signing choices

`sign-blob` can sign with a certificate. Signing exposes `--signing-algorithm`, so a workflow can make the algorithm selection explicit.

Review certificate selection, signing algorithm, service endpoints, and bundle destination independently. Conflating these inputs makes it difficult to determine which trust or transport decision caused a failure.

## Configuration review

- Prefer TUF signing configuration as the default source of service URLs.
- Use default services when creating a standard trusted root or signing configuration.
- Verify service definitions after applying `--base-config`.
- Configure and test TSA mTLS through the signing configuration when required.
- Provision TSA access before attempting Rekor v2 signing.
- Keep signing configuration and verification trust material distinct.
- Record an explicit signing-algorithm choice when policy requires one.
