# Terraform Plugin Framework

## Provider-defined functions

Framework v1.5 introduces the `function` package and
`provider.ProviderWithFunctions`. Compatibility protection begins in v1.8;
upgrades across the earlier releases are source-breaking
(`provider-plugin-framework`):

- v1.6 changes variadic values from `types.List` to `types.Tuple` and replaces
  `RunResponse.Diagnostics` with `FuncError`.
- v1.7 requires every parameter to set `Name`.
- v1.8 removes `Definition.Parameter()`.

Framework v1.8 replaces `xattr.TypeWithValidate` with
`xattr.ValidateableAttribute` and adds `function.ValidateableParameter`.
Type-specific `ParameterValidator` and `ParameterWith...Validators` interfaces
provide parameter-level validation (`provider-plugin-framework`).

## Schema value types

Framework v1.7 adds dynamic types, values, and attributes across resource,
data-source, and provider schemas, functions, defaults, plan modifiers, and
validators. Framework v1.10 provides equivalent native coverage for `Int32`
and `Float32` (`provider-plugin-framework`).

## Cross-resource-type state moves

Framework v1.6 adds `resource.ResourceWithMoveState` for Terraform cross-type
moves. Framework-only providers need v1.12 or later because it fixes a server
bug that prevented these moves (`provider-plugin-framework`).

## Plan modification behavior

Starting in Framework v1.9, child plan modifiers no longer turn a null or
unknown nested object into a known object implicitly. Add an object-level
modifier that makes the object known before child modifiers execute when that
is required (`provider-plugin-framework`).

Framework v1.15.1 changes every `UseStateForUnknown` modifier to preserve a
known null prior value for an unconfigured attribute. Child modifiers on a new
nested object can consequently produce an inconsistent plan. Framework v1.17
adds `UseNonNullStateForUnknown`, which preserves only known non-null state and
retains the earlier child-attribute behavior (`provider-plugin-framework`).

## Experimental deferred operations

Framework v1.9 adds experimental deferral fields to provider configuration,
resource `Read`, `ModifyPlan`, and `ImportState`, and data-source `Read`, with
matching `ClientCapabilities` on requests. This surface targets prerelease
Terraform clients and has no compatibility guarantee
(`provider-plugin-framework`).

## Embedded structs in state and configuration

Framework v1.11 promotes exported fields from embedded structs during
`Config.Get`, `Plan.Get`, and similar reflection conversions. An embedded
unexported struct that was ignored can now produce an unexpected-field
diagnostic. Tag the embedded field to preserve the previous behavior
(`provider-plugin-framework`).

```go
type thingModel struct {
    embeddedModel `tfsdk:"-"`
}
```

## Ephemeral resources

Framework v1.13 adds `ephemeral.EphemeralResource`, `ephemeral/schema`, and
`provider.ProviderWithEphemeralResources`; compatibility protection begins in
v1.14 (`provider-plugin-framework`). Implementations provide `Metadata`,
`Schema`, and `Open`. Optional interfaces add configuration, validation,
renewal, and close behavior, and `ConfigureResponse.EphemeralResourceData`
carries configured provider clients.

## Write-only managed-resource attributes

Framework v1.14 adds `WriteOnly` for Terraform write-only arguments
(`provider-plugin-framework`). A write-only attribute:

- Must also be `Required` or `Optional`.
- Cannot be `Computed` or use set nesting.
- Requires all children of a write-only list-, map-, or single-nested
  attribute to be write-only.
- Must be read from configuration; prior, planned, and final state are forced
  to null, and attempts to persist the value are discarded.

```go
"password_wo": schema.StringAttribute{
    Optional:  true,
    WriteOnly: true,
},
```

A write-only value cannot create a normal plan difference.
`RequiresReplace` is the exception: a configured value then triggers
replacement. For rotation without replacement, pair the value with a stored
version or keeper, or retain only a secure hash in private state.
`PreferWriteOnlyAttribute` validators can direct users away from a legacy
state-backed secret (`provider-plugin-framework`).

## Managed resource identity

Framework v1.15 adds `resource.ResourceWithIdentity`,
`resource/identityschema`, `tfsdk.ResourceIdentity`, and identity fields on
CRUD and import requests and responses (`provider-plugin-framework`). Identity
schemas accept only primitive and list attributes, omit ordinary `Required`
and `Computed` semantics, and require each attribute to choose exactly one of
`RequiredForImport` or `OptionalForImport`.

Set identity during `Create`, `Read`, and `Update`, and return it from `Read`
so an incomplete import identity can be completed from provider configuration
or remote data. Identity is immutable by default; opt into genuinely mutable
remote identity with
`MetadataResponse.ResourceBehavior.MutableIdentity = true`
(`provider-plugin-framework`).

For identity imports, `ImportStateRequest.ID` is empty and
`ImportStateRequest.Identity` carries the input. Preserve non-empty ID handling
for legacy imports, or use `resource.ImportStatePassthroughWithIdentity` when
both forms map to the same state attribute (`provider-plugin-framework`).

A Framework v1.15 upgrade also needs at least:

- `terraform-plugin-go` v0.28.0.
- `terraform-plugin-mux` v0.20.0.
- `terraform-plugin-sdk/v2` v2.37.0.
- `terraform-plugin-testing` v1.13.1.

These floors avoid Terraform runtime errors with identity support
(`provider-plugin-framework`).

## Provider-defined actions

Framework v1.16 adds `action.Action`, `action/schema`, and
`provider.ProviderWithActions` for Terraform actions. Action schemas support
attributes, nested blocks, and standard validation;
`ConfigureResponse.ActionData` carries configured clients. Framework v1.17
also permits write-only action arguments (`provider-plugin-framework`).

## Provider-side list resources

Framework v1.16 adds `list.ListResource` and
`provider.ProviderWithListResources` (`provider-plugin-framework`). Each list
has its own configuration schema but is associated with a managed-resource type
whose schema and identity describe results. `ConfigureResponse.ListResourceData`
carries clients. `ListResourceWithRawV5Schemas` and
`ListResourceWithRawV6Schemas` let list implementations target resources not
implemented with the Framework.

## Provider configuration deprecations

Framework v1.18 permits provider configuration attributes and blocks to carry
provider-authored deprecation messages (`provider-plugin-framework`).

## Experimental state stores

Framework v1.18 adds experimental `statestore`, `statestore/schema`, and
`provider.ProviderWithStateStores`. `ConfigureResponse.StateStoreData` is
passed to each store's `Initialize` method. The API has no compatibility
promise until matching Terraform Core support is generally available
(`provider-plugin-framework`).

## Go toolchain floors

The minimum Go version rises as follows (`provider-plugin-framework`):

| Framework | Minimum Go |
| --- | --- |
| v1.6 | 1.21 |
| v1.12 | 1.22 |
| v1.15 | 1.23 |
| v1.16 | 1.24 |
| v1.19 | 1.25 |
