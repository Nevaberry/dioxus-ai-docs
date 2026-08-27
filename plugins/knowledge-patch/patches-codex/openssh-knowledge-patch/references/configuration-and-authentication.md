# Configuration and Authentication

## Server packaging and isolation

### Install `sshd-auth` (batch 10.0-10.3)

OpenSSH 10.0 moves each connection's user-authentication phase out of
`sshd-session` into a separate `sshd-auth` executable.

- Install `sshd-auth` in portable packages, custom installations, images, and
  integrity or execution policies.
- Attribute authentication-phase log messages to `sshd-auth` where log
  processing groups messages by executable.
- Treat a missing `sshd-auth` binary as a packaging error rather than an
  authentication configuration error.

### Require a working Linux sandbox (batch 10.4)

On Linux builds that select the seccomp sandbox, failure to enable seccomp or
`NO_NEW_PRIVS` prevents `sshd` from continuing. Confirm both features in the
actual runtime. If a platform cannot provide them, disable the sandbox at
configure time; the former log-and-continue behavior is gone.

## Matching, expansion, and refusal

### Use the new match criteria (batch 10.0-10.3)

`Match version` is valid in both client and server configuration. Client
configuration also supports `Match sessiontype` and `Match command`.
Session types are `shell`, `exec`, `subsystem`, and `none`.

```sshconfig
Match version OpenSSH_10.*
    SetEnv GENERATION=10
```

Use `Match tagged ""` or `Match command ""` to match an explicitly empty
value.

### Expand client values deliberately (batch 10.0-10.3)

Client `SetEnv` and `User` values expand percent tokens and environment
variables. Expansion of `User` excludes `%r` and `%C` because they are
self-referential. Review values that previously expected literal `%` or
environment syntax.

### Glob authorization files (batch 10.0-10.3)

Server `AuthorizedKeysFile` and `AuthorizedPrincipalsFile` accept `glob(3)`
patterns, enabling split authorization data:

```sshconfig
AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys.d/*
```

Ensure file ownership, permissions, and deployment rules cover every matched
file.

### Refuse configured destinations (batch 10.0-10.3)

Client `RefuseConnection` aborts configuration processing with its argument as
the error when reached in an active `Host` or `Match` block:

```sshconfig
Match host old.example
    RefuseConnection "old.example is retired; use new.example"
```

## Identity and certificate authorization

### Apply command-line identity validation (batch 10.0-10.3)

- OpenSSH 10.1 rejects control characters in command-line or percent-expanded
  usernames and NUL characters in `ssh://` URIs. Trusted literal usernames in
  configuration files remain exempt.
- OpenSSH 10.3 validates usernames before `Match exec` expansion.
- The `-J`/`ProxyJump` command-line user and host names are validated, while
  `ProxyJump` values read from configuration files intentionally are not
  subject to that check.

Do not assume command-line and configuration-file identities share identical
validation boundaries.

### Harden certificate-principal matching (batch 10.0-10.3)

- An empty user-certificate principals list is not a wildcard when a trusted
  CA is constrained by an `authorized_keys` `principals="..."` restriction.
- Wildcard principals work for host certificates, not user certificates.
- A comma within one certificate principal is no longer confused with a
  configured list of several principals.

## Forwarding and authentication policy

### Let `DisableForwarding` override tunnels (batch 10.4)

`DisableForwarding=yes` overrides `PermitTunnel=yes` as documented. On older
servers, explicitly configure `PermitTunnel=no` when tunnels must be forbidden;
do not treat `DisableForwarding` alone as sufficient there.

### Handle GSSAPI caveats and hardening (batch 10.4)

- `GSSAPIStrictAcceptorCheck` is ineffective when the server is joined to
  Windows Active Directory.
- Upgrade servers with `GSSAPIAuthentication` enabled for the fixed
  pre-authentication denial of service. `MaxAuthTries` did not mitigate the
  affected path, while `PerSourcePenalties` did.
- The minimum authentication delay is restored in cases that previously
  skipped it. Re-test latency assumptions in authentication clients and tests.

### Control delegated GSSAPI credentials (batch 10.0-10.3)

OpenSSH 10.3 adds server-side `GSSAPIDelegateCredentials` to `sshd_config`,
mirroring the client option. Set it according to whether the server should
accept credentials delegated by clients.

### Set finer per-source penalties (batch 10.0-10.3)

The server supports an `invaliduser` category, whose default is the same five
seconds as `authfail`, and floating-point durations for subsecond penalties:

```sshconfig
PerSourcePenalties invaliduser:10s authfail:0.5s
```

This permits a distinct penalty for nonexistent accounts without applying the
same duration to every authentication failure.

## Configuration validation and output

### Accept mixed-case `sshd -G` directives (batch 10.4)

Configuration dump mode emits mixed-case directive names such as
`PubkeyAuthentication` rather than only lowercase names. Make parsers
case-tolerant or match the actual emitted spelling instead of relying on
lowercase literals.

### Fail invalid algorithm lists during processing (batch 10.4)

Invalid cipher and MAC lists in files or command-line arguments now fail while
configuration is processed, rather than surfacing later at runtime. Run config
validation as part of deployment and report the early failure accurately.
