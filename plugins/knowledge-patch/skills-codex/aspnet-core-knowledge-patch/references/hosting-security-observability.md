# Hosting, Security, Compression, and Observability

Batch attribution: `10.0`.

## Collect Authentication and Identity Metrics

ASP.NET Core reports authentication duration and counts for challenge, forbid, sign-in, sign-out, and authorization operations.

Identity metrics use the `Microsoft.AspNetCore.Identity` meter. Available instruments include:

- `aspnetcore.identity.user.create.duration`
- `aspnetcore.identity.user.check_password_attempts`
- `aspnetcore.identity.sign_in.sign_ins`

Select instruments intentionally rather than assuming Identity measurements share another authentication meter.

## Control Diagnostics for Handled Exceptions

Exceptions handled by an `IExceptionHandler` do not emit logs and other diagnostics by default. Set `ExceptionHandlerOptions.SuppressDiagnosticsCallback` to choose which handled exceptions remain observable, or return `false` for every exception to restore reporting:

```csharp
app.UseExceptionHandler(new ExceptionHandlerOptions
{
    SuppressDiagnosticsCallback = context => false
});
```

## Bind Development `.localhost` Domains

Kestrel treats configured `*.localhost` hosts as loopback bindings instead of wildcard external bindings.

The `web` and `blazor` templates accept `--localhost-tld` to create a host such as `<project>.dev.localhost`. After adopting that domain, trust the development certificate again because the development certificate covers `*.dev.localhost`:

```bash
dotnet dev-certs https --trust
```

## Use Evicting Memory Pools

ASP.NET Core registers `IMemoryPoolFactory<byte>`. Its `Create` method returns pools that automatically evict idle blocks.

A custom registered `IMemoryPoolFactory<byte>` does not acquire this behavior automatically. The custom implementation must provide its own eviction behavior.

## Secure New HTTP.sys Request Queues

`HttpSysOptions.RequestQueueSecurityDescriptor` accepts a `GenericSecurityDescriptor` that grants or denies queue access to users and groups.

The descriptor applies only when HTTP.sys creates a new request queue. It cannot change the security descriptor of an existing queue, so queue lifecycle must be considered when validating the configuration.

## Test Apps That Use Top-Level Statements

The ASP.NET Core source generator emits the `public partial class Program` needed by test projects. Remove a manual declaration from applications that use top-level statements; retaining it is no longer required for integration-test access.
