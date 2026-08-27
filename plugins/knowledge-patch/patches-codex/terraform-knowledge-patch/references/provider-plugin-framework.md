# Terraform Plugin Framework

All guidance in this reference derives from `provider-plugin-framework`.

## Provider-defined functions

Framework v1.5 introduces the `function` package and `provider.ProviderWithFunctions`; compatibility protection begins in v1.8. Upgrading through the early versions is source-breaking:

- v1.6 changes variadic values from `types.List` to `types.Tuple` and replaces `RunResponse.Diagnostics` with `FuncError`.
- v1.7 requires every parameter to set `Name`.
- v1.8 removes `Definition.Parameter()`.

Framework v1.8 also replaces `xattr.TypeWithValidate` with `xattr.ValidateableAttribute`, adds `function.ValidateableParameter`, and adds type-specific `ParameterValidator` and `ParameterWith...Validators` interfaces.

## Dynamic and 32-bit values

Framework v1.7 adds dynamic types, values, and attributes across resource, data-source, and provider schemas, functions, defaults, plan modifiers, and validators. Framework v1.10 adds equivalent native `Int32` and `Float32` coverage.

## Cross-resource-type state moves

Framework v1.6 adds `resource.ResourceWithMoveState` for Terraform 1.8 cross-type moves. Framework-only providers need v1.12 or later because that version fixes a server defect that prevented moves.

## Nested-object plan modification

Starting in Framework v1.9, a child modifier does not implicitly turn a null or unknown nested object into a known object. Add an object-level modifier that makes the object known before child modifiers run when the provider depends on that behavior.

## Experimental deferred operations

Framework v1.9 adds experimental deferral fields to provider configuration, resource `Read`, `ModifyPlan`, and `ImportState`, and data-source `Read`. Corresponding request types carry `ClientCapabilities`. The surface targets prerelease Terraform clients and has no compatibility guarantee.

## Embedded model fields

Framework v1.11 reflection promotes exported fields from embedded structs during `Config.Get`, `Plan.Get`, and related conversions. An embedded unexported struct that was previously ignored can now produce an unexpected-field diagnostic. Tag the embedded field to preserve the earlier behavior.

```go
type thingModel struct {
    embeddedModel `tfsdk:"-"`
}
```

## Ephemeral resources

Framework v1.13 adds `ephemeral.EphemeralResource`, `ephemeral/schema`, and `provider.ProviderWithEphemeralResources`; compatibility protection starts in v1.14. Implementations provide `Metadata`, `Schema`, and `Open`. Optional interfaces add configuration, validation, renewal, and close behavior. `ConfigureResponse.EphemeralResourceData` carries provider clients.

## Write-only schema contracts

Framework v1.14 adds `WriteOnly` for managed-resource attributes used with Terraform 1.11 or later. A write-only attribute:

- Must also be `Required` or `Optional`.
- Cannot be `Computed` or use set nesting.
- Requires every child of a write-only list-, map-, or single-nested attribute to be write-only.
- Must be read from configuration because prior, planned, and final state are forced to `null`; provider attempts to persist it are discarded.

```go
"password_wo": schema.StringAttribute{
    Optional:  true,
    WriteOnly: true,
},
```

A write-only value creates no normal plan difference. `RequiresReplace` is the exception and makes a configured value trigger replacement. For rotation without replacement, pair the secret with a stored version or keeper, or keep only a secure hash in private state. `PreferWriteOnlyAttribute` validators can steer users away from legacy state-backed secrets.

## Resource identity

Framework v1.15 adds `resource.ResourceWithIdentity`, `resource/identityschema`, `tfsdk.ResourceIdentity`, and identity fields on CRUD and import requests and responses. Identity schemas support primitive and list attributes only, omit ordinary `Required` and `Computed`, and expect each attribute to select exactly one of `RequiredForImport` or `OptionalForImport`.

Set identity during `Create`, `Read`, and `Update`; return it from `Read` so incomplete imports can be completed from provider configuration or remote data. Identity is immutable by default. Set `MetadataResponse.ResourceBehavior.MutableIdentity = true` only when the remote identity genuinely changes.

For identity imports, `ImportStateRequest.ID` is empty and `ImportStateRequest.Identity` carries the values. Retain non-empty ID handling for legacy imports, or use `resource.ImportStatePassthroughWithIdentity` when both forms map to the same state attribute.

A Framework v1.15 upgrade needs at least `terraform-plugin-go` v0.28.0, `terraform-plugin-mux` v0.20.0, `terraform-plugin-sdk/v2` v2.37.0, and `terraform-plugin-testing` v1.13.1 to avoid Terraform 1.12 runtime errors.

## Null-preserving plan modifiers

Framework v1.15.1 changes every `UseStateForUnknown` modifier to preserve known null prior values for unconfigured attributes. Child modifiers on new nested objects can consequently yield inconsistent plans. Framework v1.17 adds `UseNonNullStateForUnknown`, which preserves only known, non-null state and retains the earlier child-attribute behavior.

## Provider-defined actions

Framework v1.16 adds `action.Action`, `action/schema`, and `provider.ProviderWithActions` for Terraform 1.14 actions. `ConfigureResponse.ActionData` carries provider clients. Action schemas allow attributes, nested blocks, and normal validation; Framework v1.17 permits write-only action arguments.

## Provider-side list resources

Framework v1.16 adds `list.ListResource` and `provider.ProviderWithListResources`. Each list has a configuration schema and associates with an existing managed-resource type whose schema and identity describe returned objects. `ConfigureResponse.ListResourceData` carries provider clients. `ListResourceWithRawV5Schemas` and `ListResourceWithRawV6Schemas` can target non-Framework resources.

## Provider configuration deprecations

Framework v1.18 lets provider configuration schema attributes and blocks include provider-authored deprecation messages.

## Experimental state stores

Framework v1.18 adds experimental `statestore`, `statestore/schema`, and `provider.ProviderWithStateStores`. `ConfigureResponse.StateStoreData` is passed to each state store's `Initialize`. There is no compatibility promise until Terraform Core's `state_store` support becomes generally available.

## Go toolchain floors

Minimum Go versions rise as follows:

| Framework | Minimum Go |
|---|---|
| v1.6 | 1.21 |
| v1.12 | 1.22 |
| v1.15 | 1.23 |
| v1.16 | 1.24 |
| v1.19 | 1.25 |
