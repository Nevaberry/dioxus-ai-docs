# Hosting, HTTP, Caching, and Security

## Development hosts and certificates

### Treat `.localhost` names as loopback

Kestrel treats configured `*.localhost` hosts as loopback bindings rather than
wildcard external bindings (since 10.0). The `web` and `blazor` templates accept
`--localhost-tld` to produce a host such as `<project>.dev.localhost`.

The development certificate includes `*.dev.localhost`, but the updated
certificate must be trusted again:

```bash
dotnet dev-certs https --trust
```

## Memory pools

### Preserve idle-block eviction in custom factories

Dependency injection now provides an `IMemoryPoolFactory<byte>` whose `Create`
method returns pools that automatically evict idle blocks (since 10.0).
Replacing the registered factory also replaces this behavior: a custom factory
must implement eviction itself if it is required.

## HTTP.sys queue access

### Set security when creating a request queue

Assign a `GenericSecurityDescriptor` to
`HttpSysOptions.RequestQueueSecurityDescriptor` to grant or deny request-queue
access to users and groups (since 10.0). The descriptor is used only when
HTTP.sys creates a new queue. It cannot modify the security of an existing
queue, so ensure queue ownership and creation order are explicit.
