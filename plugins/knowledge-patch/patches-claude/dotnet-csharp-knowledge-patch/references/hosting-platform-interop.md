# Hosting, Platform Behavior, and Interop

The compatibility items in this reference are attributed to `10.0-guides`.

## Background Services, Configuration, and Logging

All of `BackgroundService.ExecuteAsync` now runs as a `Task`. Code before the first
`await` should no longer be treated as synchronously executed startup work. Review
startup ordering, exception observation, and tests that assume synchronous entry.

Configuration preserves null values. Providers and binders that previously treated
null as missing may now produce a distinguishable result; test defaulting and merge
behavior with explicit null inputs.

`ProviderAliasAttribute` moved to
`Microsoft.Extensions.Logging.Abstractions`. Update assembly/package assumptions and
rebuild consumers that inspect or reference the attribute.

Trim-related `DynamicallyAccessedMembers` annotations were removed from trim-unsafe
`Microsoft.Extensions.Configuration` code. Do not infer trimming safety from the old
annotations; retain required members explicitly or avoid the unsafe path.

The ICU override environment variable is `DOTNET_ICU_VERSION_OVERRIDE`. Replace
older variable names in launch scripts, containers, and deployment configuration.

## Native-Library Search

Single-file applications no longer probe the executable directory for native
libraries. Package native dependencies in a supported publish layout or resolve them
explicitly rather than relying on executable-directory proximity.

`DllImportSearchPath.AssemblyDirectory` now searches only the assembly directory.
Audit code that expected the flag to search additional locations, and test the
published artifact rather than only the build tree.

## COM Reflection

Casting an `IDispatchEx` COM object to `IReflect` now fails. Use the COM dispatch
surface directly or another supported reflection/interop mechanism; do not retain a
fallback that assumes this cast succeeds.

## Windows Desktop Compatibility

Projects referencing both WPF and Windows Forms must disambiguate `MenuItem` and
`ContextMenu`. Qualify the namespace or use explicit aliases at mixed-framework call
sites.

`HtmlElement.InsertAdjacentElement` has a renamed parameter. Source callers that use
named arguments must adopt the current parameter name; positional calls are not
affected by a name-only change.

`StatusStrip` defaults to the system render mode. Set the desired render mode
explicitly if appearance must be stable across a runtime update.

Some `System.Drawing` failures now throw `ExternalException` instead of
`OutOfMemoryException`. Revisit exception filters and recovery paths that handle only
the older type.

WPF rejects empty `ColumnDefinitions` and `RowDefinitions`. Remove empty declarations
or populate them with valid definitions.

Incorrect `DynamicResource` usage can terminate the application. Treat invalid
resource references as a correctness issue and exercise resource-loading paths in
startup and UI tests.
