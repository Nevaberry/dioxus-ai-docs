# Deployment, Containers, Native Output, and UI

Compatibility guidance is attributed to `10.0-guides`; publishing features are
attributed to `10.0`.

## Default Container Base Distribution

Default .NET 10 container images use Ubuntu. Builds that depend on packages, paths,
or a package manager from the previous distribution must pin the intended base
image or adapt their installation steps. Rebuild and validate native dependencies
when changing bases.

## Published File-Based Apps

`dotnet publish app.cs` produces a native executable because file-based apps use
Native AOT by default for publishing. Add `#:property PublishAot=false` when a
dependency is incompatible. File-based apps also accept `#:project` references
and support executable extensionless shebang files.

```csharp
#!/usr/bin/env dotnet
#:project ../ClassLib/ClassLib.csproj
#:property PublishAot=false
Console.WriteLine(new ClassLib.Greeter().Greet());
```

## Console Container Publishing and Image Format

Console projects can run `dotnet publish /t:PublishContainer` without setting
`EnableSdkContainerSupport`. Set `ContainerImageFormat` to `Docker` or `OCI` to
avoid inheriting a default that depends on the base image and whether the image
is multi-architecture.

```xml
<PropertyGroup>
  <ContainerImageFormat>OCI</ContainerImageFormat>
</PropertyGroup>
```

## Windows Desktop Compatibility

- Projects that reference both WPF and Windows Forms must disambiguate `MenuItem`
  and `ContextMenu`.
- `HtmlElement.InsertAdjacentElement` has a renamed parameter; named-argument
  call sites must use the new name.
- `StatusStrip` defaults to the system render mode.
- Some `System.Drawing` failures throw `ExternalException` instead of
  `OutOfMemoryException`; update exception handling accordingly.
- WPF rejects empty `ColumnDefinitions` and `RowDefinitions`.
- Incorrect `DynamicResource` usage can terminate the application. Validate
  resource references during startup and UI tests.
