# Terraform Plugin Framework

Provider implementation APIs and compatibility boundaries from Framework v1.5 through v1.19.

## Functions and schema types

### Dynamic and 32-bit schema values

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.7 adds `DynamicType`, `DynamicValue`, and `DynamicAttribute` across resource, data source, and provider schemas, plus dynamic function parameters/returns, defaults, plan modifiers, and validators. Framework v1.10 similarly adds native `Int32` and `Float32` types across schemas, functions, defaults, plan modifiers, custom values, and validation rather than requiring providers to model them as the older numeric types.

### Provider-defined function API stabilization

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.5 introduced the `function` package and `provider.ProviderWithFunctions`; the feature became compatibility-protected in v1.8. The intervening releases have important source-breaking edges: v1.6 represents variadic arguments as `types.Tuple` rather than `types.List` and replaces `RunResponse.Diagnostics` with `FuncError`, v1.7 requires every parameter to set `Name`, and v1.8 removes `Definition.Parameter()`.

Custom function values and parameters can validate through `attr/xattr.ValidateableAttribute` and `function.ValidateableParameter`. Type-specific `ParameterValidator` and `ParameterWith...Validators` interfaces provide parameter-level validation.

## Resource capabilities and state semantics

### `UseStateForUnknown` null semantics

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.15.1 changes every `UseStateForUnknown` plan modifier to preserve a known null prior value for an unconfigured attribute. This can make child modifiers in newly created nested objects produce inconsistent plans when they relied on the child remaining unknown; Framework v1.17 adds `UseNonNullStateForUnknown` to preserve only known, non-null state and recover the earlier behavior for that case.

### Cross-resource-type state moves

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.6 adds `resource.ResourceWithMoveState` for provider-side conversions used by Terraform 1.8 cross-type `moved` blocks. Framework-only providers should use v1.12 or later, which fixes a server bug that prevented these moves from working.

### Embedded `tfsdk` model fields

*Plugin Framework update — batch `provider-plugin-framework`.*

Starting in Framework v1.11, reflection used by `Config.Get`, `Plan.Get`, and related conversions promotes exported fields from embedded structs. An embedded unexported struct that was previously ignored can therefore cause an unexpected-field diagnostic; tag the embedded field itself to preserve the old behavior.

```go
type thingModel struct {
    Name          types.String `tfsdk:"name"`
    embeddedModel              `tfsdk:"-"`
}
```

### Managed resource identity implementation

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.15 adds `resource.ResourceWithIdentity`, `resource/identityschema`, `tfsdk.ResourceIdentity`, and `Identity` fields on CRUD and import request/response objects. The identity schema supports primitive and list attributes only; it has no `Required` or `Computed`, and each attribute should choose exactly one of `RequiredForImport` or `OptionalForImport`.

Set identity during `Create`, `Read`, and `Update` to avoid validation failures, and return it from `Read` so imports with incomplete identities can be filled from provider configuration or the remote API. Identity is immutable by default; a genuinely mutable remote identity requires `MetadataResponse.ResourceBehavior.MutableIdentity = true`.

For identity imports, `ImportStateRequest.ID` is empty and identity data arrives through `ImportStateRequest.Identity`; providers retaining older Terraform support must continue handling a non-empty ID. `resource.ImportStatePassthroughWithIdentity` handles the common case where either form maps to the same state attribute.

Upgrading to Framework v1.15 requires coordinated minimum versions to avoid Terraform 1.12 runtime errors: `terraform-plugin-go` v0.28.0, `terraform-plugin-mux` v0.20.0, `terraform-plugin-sdk/v2` v2.37.0, and `terraform-plugin-testing` v1.13.1.

### Provider-defined action implementation

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.16 adds the `action` and `action/schema` packages, the `action.Action` interface, and `provider.ProviderWithActions` for Terraform 1.14 actions. `provider.ConfigureResponse.ActionData` passes configured provider data to action instances; action schemas support attributes, nested blocks, standard validation, and, as of Framework v1.17, `WriteOnly` arguments.

### Provider-side ephemeral resources

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.13 introduced the `ephemeral` and `ephemeral/schema` packages, with compatibility protection beginning in v1.14. An implementation supplies `Metadata`, `Schema`, and `Open`; optional lifecycle interfaces add provider configuration, configuration validation, renewal, and close behavior.

Register constructors through `provider.ProviderWithEphemeralResources`. Provider-scoped clients or other data can be routed specifically to these implementations with `provider.ConfigureResponse.EphemeralResourceData`.

```go
var _ provider.ProviderWithEphemeralResources = (*ExampleProvider)(nil)

func (p *ExampleProvider) EphemeralResources(context.Context) []func() ephemeral.EphemeralResource {
    return []func() ephemeral.EphemeralResource{NewThingEphemeralResource}
}
```

### Provider-side list resources

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.16 adds `list.ListResource` for Terraform 1.14 queries. A list implementation is tied to an existing managed resource type because returned objects use that resource's schema and identity; it defines metadata, a list-configuration schema, and listing behavior, then is registered through `provider.ProviderWithListResources`.

`provider.ConfigureResponse.ListResourceData` passes provider-specific clients to list implementations. Providers extending non-Framework resources can supply their schemas through `ListResourceWithRawV5Schemas` or `ListResourceWithRawV6Schemas` instead.

### Write-only schema contracts

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.14 adds `WriteOnly` to managed-resource attributes. A write-only attribute must also be `Required` or `Optional`, cannot be `Computed`, cannot be a set or occur under set nesting, and when a list-, map-, or single-nested attribute is write-only all of its children must be write-only too.

```go
"password_wo": schema.StringAttribute{
    Optional:  true,
    WriteOnly: true,
},
```

Read the value from configuration, never plan or state: the framework forces its prior, planned, and final state values to `null` and undoes any provider attempt to persist it. It cannot create a normal plan difference; attaching `RequiresReplace` is the exception and makes the configured value trigger replacement. To detect intended rotation, pair it with a stored trigger/version, use keepers, or retain only a secure hash in private state; `PreferWriteOnlyAttribute` validators can warn users away from a legacy stored-secret attribute.

## Experimental APIs and compatibility boundaries

### Configuration-schema deprecations

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.18 can attach deprecation messages directly to attributes and blocks in provider configuration schemas. This is distinct from managed-resource deprecations and lets provider configuration usage produce the provider-authored migration warning.

### Experimental deferred operations

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.9 can report deferred work from provider configuration, resource `Read`, `ModifyPlan`, and `ImportState`, and data-source `Read`. Implementations must inspect the corresponding request's `ClientCapabilities` before setting a response's `Deferred` field; this surface was introduced for prerelease Terraform builds and was not covered by compatibility guarantees.

### Experimental state stores

*Plugin Framework update — batch `provider-plugin-framework`.*

Framework v1.18 introduces experimental `statestore` and `statestore/schema` packages plus `provider.ProviderWithStateStores`. `provider.ConfigureResponse.StateStoreData` is delivered to each state store's `Initialize` method, but the API carries no compatibility promise until Terraform Core's `state_store` support is generally available.

### Go toolchain floors

*Plugin Framework update — batch `provider-plugin-framework`.*

The Framework module's minimum Go version advances at several upgrade boundaries: v1.6 requires Go 1.21, v1.12 requires Go 1.22, v1.15 requires Go 1.23, v1.16 requires Go 1.24, and v1.19 requires Go 1.25. Provider builds must raise their toolchain with those Framework upgrades.

