# Configuration and Authentication

## Installation and process boundaries

### Package `sshd-auth`

OpenSSH 10.0 moves each connection's user-authentication phase from
`sshd-session` to a separate `sshd-auth` executable. Portable packages, custom
installers, images, executable allowlists, and integrity policies must include
the new binary. Authentication-phase log records may now identify `sshd-auth`
as their source.

When authentication fails because the executable is absent or blocked, repair
the packaging or execution policy instead of changing `sshd_config`.

### Treat Linux sandbox initialization failures as fatal

On OpenSSH 10.4 Linux builds that use seccomp, failure to enable seccomp or
`NO_NEW_PRIVS` prevents `sshd` from continuing. Validate both facilities in
the deployed container, service, or host. If the platform cannot provide them,
disable the sandbox at configure time rather than relying on the former
log-and-continue behavior.

## Effective configuration and matching

### Parse mixed-case `sshd -G` output

In OpenSSH 10.4, configuration dump mode emits mixed-case directive names such
as `PubkeyAuthentication` instead of only lowercase names. Consumers of
`sshd -G` must compare directive names without assuming lowercase spelling.

### Match version, session type, command, and empty values

OpenSSH 10.0 adds `Match version` to client and server configuration. Client
configuration also gains `Match sessiontype` and `Match command`. Valid session
types are `shell`, `exec`, `subsystem`, and `none`.

```sshconfig
Match version OpenSSH_10.*
    SetEnv GENERATION=10
```

Use `Match tagged ""` and `Match command ""` to match an explicitly empty value.

### Refuse a destination through client configuration

`RefuseConnection` aborts client configuration processing and displays its
argument as the error. Place it in an active `Host` or `Match` block:

```sshconfig
Match host old.example
    RefuseConnection "old.example is retired; use new.example"
```

### Expand client values and glob authorization files carefully

Client `SetEnv` and `User` values expand percent tokens and environment
variables. `User` deliberately excludes the self-referential `%r` and `%C`
tokens.

Server `AuthorizedKeysFile` and `AuthorizedPrincipalsFile` accept `glob(3)`
patterns, which permits split authorization layouts:

```sshconfig
AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys.d/*
```

Account for every matched file when auditing access.

## Identity and authorization

### Validate command-line identities before expansion

OpenSSH 10.1 rejects control characters in command-line or percent-expanded
usernames and rejects NUL characters in `ssh://` URIs. Trusted literal
usernames in configuration files remain exempt.

OpenSSH 10.3 moves username validation early enough to occur before
`Match exec` expansion. It also validates user and host names passed by
command-line `-J` or `ProxyJump`, while intentionally leaving configuration-file
`ProxyJump` values outside that check. Validate both input paths in tools that
compose connections.

### Harden certificate-principal rules

OpenSSH 10.3 no longer treats a user certificate with an empty principals list
as a wildcard when a CA is trusted through an `authorized_keys`
`principals="..."` restriction. Wildcard support applies consistently to host
certificates, not user certificates, and a comma inside a certificate principal
is no longer confused with a configured list of multiple principals.

### Keep ECDSA authorization lists exact

From OpenSSH 10.3, listing one ECDSA name in `PubkeyAcceptedAlgorithms` or
`HostbasedAcceptedAlgorithms` admits only that algorithm. Earlier behavior
could admit every ECDSA variant. State every intended ECDSA algorithm.

## Forwarding and authentication policy

### Make `DisableForwarding` cover tunnels

In OpenSSH 10.4, `DisableForwarding=yes` overrides `PermitTunnel=yes` as
documented. On older servers, set `PermitTunnel=no` explicitly when tunnel
forwarding must be prohibited.

### Apply GSSAPI fixes and limitations

`GSSAPIStrictAcceptorCheck` is ineffective on a server joined to Windows Active
Directory. Do not use it as an enforcement boundary there.

OpenSSH 10.4 fixes a pre-authentication denial of service when
`GSSAPIAuthentication` is enabled and restores minimum authentication delays in
several cases where they were missing. `MaxAuthTries` did not mitigate the
older denial-of-service path, but `PerSourcePenalties` did. Upgrade affected
servers and retain source penalties as defense in depth.

### Control acceptance of delegated GSSAPI credentials

OpenSSH 10.3 adds server-side `GSSAPIDelegateCredentials` to `sshd_config`,
mirroring the client setting. Set it according to whether the server should
accept credentials delegated by a client.

### Distinguish invalid-user penalties

OpenSSH 10.3 adds the `invaliduser` category to `PerSourcePenalties`, with the
same default five-second duration as `authfail`, and accepts floating-point
durations for subsecond penalties. For example:

```sshconfig
PerSourcePenalties invaliduser:10s authfail:0.5s
```

This can penalize nonexistent-account attempts more heavily than other
authentication failures.
