---
name: openssh-knowledge-patch
description: OpenSSH
version: "10.4"
license: MIT
metadata:
  author: Nevaberry
---


# OpenSSH Knowledge Patch

## Use this patch

1. Identify the exact client, server, and agent versions before changing
   algorithms, authentication, forwarding, multiplexing, or file-transfer
   automation.
2. Keep client and server behavior separate. Several defaults and validations
   changed on only one side.
3. Read the matching topic reference before editing `ssh_config`,
   `sshd_config`, packages, output parsers, or automation.
4. Preserve compatibility exceptions only for peers that require them. Do not
   restore removed algorithms as broad defaults.
5. Treat memory-safety, authentication, containment, and agent-binding fixes as
   upgrade requirements.
6. Test effective configuration, rekey, multiplexing, and transfers against the
   actual peer implementations used in production.

## Reference index

| Reference | Topics |
| --- | --- |
| [cryptography-and-keys.md](references/cryptography-and-keys.md) | Algorithm removal and defaults, composite signatures, certificates, revocation, FIDO, and key formats |
| [configuration-and-authentication.md](references/configuration-and-authentication.md) | Packaging, sandboxing, effective configuration, matching, identity validation, authorization, forwarding, GSSAPI, and penalties |
| [connections-and-agents.md](references/connections-and-agents.md) | Rekey, QoS, timeouts, multiplexing, agent sockets, key lifetime, extensions, and forwarding boundaries |
| [file-transfer.md](references/file-transfer.md) | `scp`, `sftp`, destination containment, `internal-sftp`, listings, control masters, and mode preservation |

## Breaking changes and deprecations

### Remove legacy cryptography assumptions

- Treat DSA signatures as unavailable from OpenSSH 10.0.
- Do not assume a server offers finite-field `diffie-hellman-group*` or
  `diffie-hellman-group-exchange-*` methods by default. The corresponding
  client default was not removed at the same time.
- Do not expect compiled-in groups to rescue a present moduli file that has no
  suitable groups.
- Remove experimental XMSS keys before deploying 10.1 or later.
- Upgrade or replace peers that cannot rekey before using 10.3 or later.

### Install the authentication executable

OpenSSH 10.0 moves per-connection user authentication from `sshd-session` to
`sshd-auth`.

- Include `sshd-auth` in portable packages, images, custom install manifests,
  executable allowlists, and integrity policies.
- Expect authentication-phase log messages to be attributed to `sshd-auth`.
- Diagnose a missing `sshd-auth` as a packaging defect rather than an
  authentication-policy failure.

### Make Linux sandbox support explicit

On OpenSSH 10.4 Linux builds that use the seccomp sandbox, failure to enable
seccomp or `NO_NEW_PRIVS` prevents `sshd` from continuing.

- Confirm both facilities work in the deployed runtime.
- Disable the sandbox at configure time if the platform cannot provide them.
- Do not depend on the former log-and-continue behavior.

### Enforce rekey interoperability

OpenSSH 10.4 disconnects a peer that sends a non-key-exchange message during a
post-authentication rekey.

- Fix peers that violate RFC 4253 section 7.1 instead of suppressing the
  disconnect.
- Upgrade clients to receive the fix for a use-after-free triggered when a
  server changes its host key during rekey.
- Treat peers that cannot rekey as incompatible with OpenSSH 10.3 and later.

### Upgrade agents used through forwarding

Upgrade forwarded agents to OpenSSH 10.5. Earlier agents could refuse
`session-bind@openssh.com` while locked, allowing a remote user of the
forwarded agent to perform operations that should have remained local-only.
Prioritize agents that can add PKCS#11 tokens or hold destination-restricted
keys.

### Upgrade concurrent multiplexing clients

OpenSSH 10.5 fixes a potential realloc use-after-free when automation adds a
remote forwarding through the local multiplexing socket while another
remote-forward open request is pending. Upgrade clients that mutate remote
forwards concurrently over a shared control connection.

### Upgrade for transfer containment

- Upgrade clients that download from untrusted servers. `sftp host:/path .`
  now prevents the server from selecting an unexpected local destination.
- Upgrade remote-to-remote `scp` clients so a malicious server cannot write
  into the parent of the intended target directory.
- Audit `internal-sftp` invocations with ten or more arguments. Older releases
  discard the tenth and later arguments and can silently lose a security
  option.

### Avoid the `ControlPersist` terminal regression

Do not leave interactive users on OpenSSH 10.1 when `ControlPersist` is active.
OpenSSH 10.2 fixes the regression that could leave terminal sessions unusable.

## High-use cryptography and key changes

### Account for new negotiation defaults

- Expect `mlkem768x25519-sha256` to be the default key exchange from 10.0.
- Expect cipher preference to be ChaCha20/Poly1305, AES-GCM 128/256, then
  AES-CTR 128/192/256.
- From 10.1, expect a default-on warning when negotiation selects a
  non-post-quantum key exchange; configure it with `WarnWeakCrypto`.
- Plan to remove dependencies on SHA1 SSHFP records. The client warns that they
  will eventually be ignored, and `ssh-keygen -r` emits only SHA256 records.

### Opt in to composite signatures

OpenSSH 10.4 supports an experimental ML-DSA 44 and Ed25519 composite key type.
It remains disabled by default.

```sh
ssh-keygen -t mldsa44-ed25519
```

Add the type explicitly to applicable lists such as `HostKeyAlgorithms` and
`PubkeyAcceptedAlgorithms`; generating a key does not enable negotiation.

### Keep algorithm and key policy exact

- Expect invalid cipher and MAC lists to fail while configuration is processed
  instead of later at runtime.
- On 10.3 or later, an ECDSA name in `PubkeyAcceptedAlgorithms` or
  `HostbasedAcceptedAlgorithms` admits only that exact ECDSA algorithm.
- Read [cryptography-and-keys.md](references/cryptography-and-keys.md) before
  changing certificate principals, revocation files, resident-key downloads,
  or PKCS#8 workflows.

## High-use configuration and authentication changes

### Match new connection properties

Use `Match version` in client or server configuration. Client configuration can
also match `sessiontype` and `command`; session types are `shell`, `exec`,
`subsystem`, and `none`.

```sshconfig
Match version OpenSSH_10.*
    SetEnv GENERATION=10
```

Use `Match tagged ""` or `Match command ""` when the empty value must match
explicitly.

### Refuse destinations from configuration

Use `RefuseConnection` inside an active client `Host` or `Match` block to abort
configuration processing with a useful error.

```sshconfig
Match host old.example
    RefuseConnection "old.example is retired; use new.example"
```

### Apply expansion and authorization globs deliberately

- Client `SetEnv` and `User` values expand percent tokens and environment
  variables, but `User` excludes the self-referential `%r` and `%C` tokens.
- Server `AuthorizedKeysFile` and `AuthorizedPrincipalsFile` accept `glob(3)`
  patterns.

```sshconfig
AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys.d/*
```

### Re-check forwarding and GSSAPI policy

- On 10.4, `DisableForwarding=yes` overrides `PermitTunnel=yes`. On older
  servers, set `PermitTunnel=no` explicitly when tunnels must be prohibited.
- Do not depend on `GSSAPIStrictAcceptorCheck` for a server joined to Windows
  Active Directory; it is ineffective there.
- Upgrade GSSAPI-enabled servers for the pre-authentication denial-of-service
  fix and restored minimum authentication delays.
- Use `PerSourcePenalties`, not `MaxAuthTries`, to mitigate the older GSSAPI
  denial-of-service path.

## High-use agent and connection changes

### Handle the agent socket migration

From 10.1, local and forwarded agent sockets use hostname-hashed paths under
`~/.ssh/agent` instead of `/tmp`.

- Use `ssh-agent -T` only when the legacy `/tmp` layout is required.
- Use `-U` to suppress stale-socket cleanup, `-u` to perform cleanup only, and
  `-uu` to ignore the hostname during cleanup.
- Remove tooling assumptions that agent sockets always live under `/tmp`.

### Control key lifetime and agent operations

- Send `SIGUSR1` to a 10.0-or-later agent to clear all keys.
- Use systemd-style socket activation only when `LISTEN_PID` and `LISTEN_FDS`
  are set and `ssh-agent` runs with `-d` or `-D` without an explicit path.
- Expect certificates loaded from 10.1 onward to be removed five minutes after
  their certificate expiry. Pass `ssh-add -N` to disable that lifetime.
- Use `ssh-add -Q` on 10.3 or later to query supported agent extensions.

### Re-test transport behavior

- Interactive-only traffic defaults to EF; non-interactive traffic uses the
  operating-system default, and selection changes as channel types change.
- Remove legacy `lowdelay`, `reliability`, and `throughput` values because they
  are ignored.
- On 10.3 servers, expect first-match-wins `IPQoS` precedence and support for
  the VA codepoint.
- Expect `UnusedConnectionTimeout` to begin only after the final channel closes
  on 10.3 or later.

## High-use file-transfer changes

- Expect `scp` and `sftp` to invoke `ssh` with `ControlMaster no`. They reuse an
  existing master but do not create one implicitly.
- Expect `sftp ls -ln` on 10.4 to print numeric user and group IDs; remove
  workarounds for the earlier name output.
- For root downloads using legacy `scp -O`, pass `-p` only when preserving
  setuid or setgid bits is intentional. From 10.3, those bits are otherwise
  cleared.

## Validation checklist

- Confirm packages and images install and can execute `sshd-auth`.
- Exercise seccomp and `NO_NEW_PRIVS` initialization in the deployment runtime.
- Validate algorithm lists and exact ECDSA allowlists before rollout.
- Exercise post-authentication rekey against every non-OpenSSH peer.
- Make `sshd -G` consumers accept mixed-case directive names.
- Audit long `internal-sftp` commands and transfers from untrusted servers.
- Test agent discovery, cleanup, certificate expiry, locking, and forwarding.
- Reproduce concurrent remote-forward changes over multiplexed connections.
- Review GSSAPI, forwarding, principal, and per-source penalty policy in the
  detailed references.
