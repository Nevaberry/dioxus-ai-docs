# Configuration and Authentication

## Server process split

OpenSSH 10.0 moves each connection's user-authentication phase from `sshd-session` into a separate `sshd-auth` executable.

- Install `sshd-auth` in portable packages, custom prefixes, containers, chroots, and immutable allowlists.
- Expect authentication-phase log messages to be attributed to `sshd-auth`.
- Check packaging before debugging authentication configuration when the executable is missing or blocked.

## Linux sandbox failures

On Linux builds that use the seccomp sandbox, OpenSSH 10.4 treats failure to enable seccomp or `NO_NEW_PRIVS` as fatal. Verify those facilities in containers and restricted service environments. If the platform cannot provide them, disable the sandbox at configure time; the former log-and-continue behavior is gone.

## Configuration dumps and validation

OpenSSH 10.4 emits mixed-case directive names from `sshd -G`, such as `PubkeyAuthentication`, instead of all-lowercase names. Make parsers case-insensitive or normalize keys before matching.

## Match criteria

OpenSSH 10.0 adds `Match version` to both client and server configuration. A version pattern may be written as:

```sshconfig
Match version OpenSSH_10.*
```

Client configuration also gains `Match sessiontype` and `Match command`. Valid session types are `shell`, `exec`, `subsystem`, and `none`.

Use `Match tagged ""` and `Match command ""` to match an explicitly empty value. Do not treat an omitted argument as equivalent.

## Expansion and authorization paths

Client `SetEnv` and `User` values expand percent tokens and environment variables from 10.0. For `User`, exclude self-referential `%r` and `%C` tokens.

Server `AuthorizedKeysFile` and `AuthorizedPrincipalsFile` accept `glob(3)` patterns. For example:

```sshconfig
AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys.d/*
```

Account for file ordering and permissions when splitting authorization material.

## Refusing configured destinations

Use the client `RefuseConnection` directive to abort configuration processing with its argument as the error:

```sshconfig
Match host old.example
    RefuseConnection "old.example is retired; use new.example"
```

Place it in an active `Host` or `Match` block so the intended destination is rejected before a connection is attempted.

## Command-line identity validation

OpenSSH 10.1 rejects control characters in command-line or percent-expanded usernames and NUL characters in `ssh://` URIs. Trusted literal usernames in configuration files remain exempt.

OpenSSH 10.3 performs username validation early enough to precede `Match exec` expansion. It also validates command-line `-J` and `ProxyJump` user and host names, but intentionally does not apply that ProxyJump check to configuration-file values. Do not assume command-line and file-based ProxyJump inputs have identical validation.

## Forwarding policy

In 10.4, `DisableForwarding=yes` overrides `PermitTunnel=yes` as documented. On older servers, set `PermitTunnel=no` explicitly whenever tunnels must be prohibited; `DisableForwarding` alone did not reliably enforce that policy.

## Certificate authorization

OpenSSH 10.3 stops treating an empty user-certificate principals list as a wildcard when the CA is trusted through an `authorized_keys` `principals="..."` restriction. Host certificates support principal wildcards consistently; user certificates do not. Matching also keeps a comma inside one certificate principal distinct from a configured multi-principal list.

## GSSAPI behavior

Do not depend on `GSSAPIStrictAcceptorCheck` when the server is joined to Windows Active Directory; the setting is ineffective in that environment.

OpenSSH 10.4 fixes a pre-authentication denial of service when `GSSAPIAuthentication` is enabled. `MaxAuthTries` did not mitigate the older path, while `PerSourcePenalties` applied. The release also restores the minimum authentication delay in several cases where it was not enforced. Upgrade rather than treating `MaxAuthTries` as a substitute.

OpenSSH 10.3 adds server-side `GSSAPIDelegateCredentials`, mirroring the client option. Set it in `sshd_config` when the server must decide whether to accept credentials delegated by a client.

## Per-source penalties

OpenSSH 10.3 adds the `invaliduser` category to `PerSourcePenalties`, with the same default five-second penalty as `authfail`. It also accepts floating-point durations for subsecond penalties:

```sshconfig
PerSourcePenalties invaliduser:10s authfail:0.5s
```

Use separate values when nonexistent-account probes deserve a stronger penalty than general authentication failures.
