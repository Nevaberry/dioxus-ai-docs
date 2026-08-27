# Observability, Identity, and SignalR

## Exception handling diagnostics

### Handled exceptions are suppressed by default

Exceptions handled by an `IExceptionHandler` do not emit logs or other
diagnostics by default (since 10.0). Use
`ExceptionHandlerOptions.SuppressDiagnosticsCallback` to select handled
exceptions that still need reporting. Returning `false` restores the earlier
reporting behavior for every handled exception:

```csharp
app.UseExceptionHandler(new ExceptionHandlerOptions
{
    SuppressDiagnosticsCallback = context => false
});
```

## Authentication and Identity telemetry

### Observe authentication and authorization activity

ASP.NET Core reports authentication duration and counts for challenge, forbid,
sign-in, sign-out, and authorization activity (since 10.0). Configure the
application's metrics pipeline to collect the relevant framework instruments.

Identity uses the `Microsoft.AspNetCore.Identity` meter. Available instruments
include:

- `aspnetcore.identity.user.create.duration`
- `aspnetcore.identity.user.check_password_attempts`
- `aspnetcore.identity.sign_in.sign_ins`

### Add passkeys to an existing Blazor Web App

Existing Blazor Web Apps can adopt passkey user authentication through the
dedicated migration path provided for existing apps (`10.0-migration`). Treat
this as an Identity migration rather than assuming passkeys are limited to newly
created templates.

### Update Identity redirects after changing navigation exceptions

The Blazor Web App template sets
`<BlazorDisableThrowNavigationException>true</BlazorDisableThrowNavigationException>`
to avoid navigation exceptions during static SSR (`10.0-migration`). When an
older Individual Accounts app opts into the property:

1. Remove the `InvalidOperationException` thrown by `RedirectTo`.
2. Remove all five `[DoesNotReturn]` attributes.

Make both edits in
`Components/Account/IdentityRedirectManager.cs`; leaving either contract behind
makes the helper's annotations disagree with its new control flow.
