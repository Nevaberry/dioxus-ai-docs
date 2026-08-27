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

1. Identify both client and server versions before changing algorithms,
   authentication, forwarding, agent handling, or file-transfer automation.
2. Separate client behavior from server behavior. Defaults and validation may
   have changed on only one side.
3. Read the matching topic reference before editing `ssh_config`,
   `sshd_config`, packaging, output parsers, or transfer scripts.
4. Preserve a compatibility exception only when a specific peer requires it;
   never restore removed algorithms as a general default.
5. Treat fixes for memory safety, authentication denial of service, forwarded
   agent restrictions, and transfer containment as upgrade requirements.
6. Re-test configuration dumps and human-readable command output before
   depending on literal names, casing, or formatting.

## Reference index

| Reference | Topics |
| --- | --- |
| [cryptography-and-keys.md](references/cryptography-and-keys.md) | Algorithm removals and defaults, warnings, composite signatures, exact allowlists, revocation, FIDO, PKCS#8 |
| [configuration-and-authentication.md](references/configuration-and-authentication.md) | Packaging, sandboxing, matching, expansion, identity validation, authorization, forwarding, GSSAPI, penalties |
| [connections-and-agents.md](references/connections-and-agents.md) | Rekeying, multiplexing, QoS, timeouts, agent lifecycle, forwarding extensions and security fixes |
| [file-transfer.md](references/file-transfer.md) | `scp`, `sftp`, control masters, destination containment, `internal-sftp`, listings, mode preservation |

## Breaking changes and deprecations

### Remove assumptions about legacy algorithms

- Treat DSA signatures as unavailable; support was removed entirely.
- Do not assume the server offers finite-field `diffie-hellman-group*` or
  `diffie-hellman-group-exchange-*` methods by default. The client default did
  not change at the same time.
- Do not depend on compiled-in groups when a present moduli file contains no
  suitable groups; that condition no longer falls back.
- Remove experimental XMSS keys before upgrading from an older installation.
- Upgrade or replace peers that cannot rekey.

### Install the split authentication executable

Per-connection user authentication runs in `sshd-auth`, separately from
`sshd-session`.

- Include `sshd-auth` in portable packages, custom install manifests,
  containers, and executable integrity policies.
- Include it when mapping authentication-phase log messages to executables.
- Diagnose a missing binary as a packaging defect, not an `sshd_config`
  failure.

### Make Linux sandbox support an explicit build decision

On Linux seccomp builds, failure to enable seccomp or `NO_NEW_PRIVS` is fatal.

- Verify that both facilities work in the deployed runtime.
- Disable the sandbox at configure time when the platform cannot provide them.
- Do not rely on the former log-and-continue behavior.

### Enforce rekey interoperability

Clients and servers disconnect a peer that sends a non-key-exchange message
during post-authentication rekey. Fix implementations that violate RFC 4253
section 7.1. Upgrade clients for the use-after-free fix when a server changes
its host key during rekey.

### Upgrade for security-sensitive forwarding

- Upgrade agents that may be forwarded. A locked agent must still process
  `session-bind@openssh.com` so remote users cannot bypass restrictions on
  operations intended to be local-only, including adding PKCS#11 tokens or
  using destination-restricted keys.
- Upgrade clients whose automation adds remote forwards concurrently through a
  shared control connection; the multiplexed path had a realloc use-after-free
  race while another remote-forward request was pending.

### Upgrade for transfer containment

- Upgrade clients that download from untrusted servers: `sftp host:/path .`
  now prevents the server from choosing an unexpected local destination.
- Upgrade remote-to-remote `scp` clients so a malicious server cannot write
  into the parent of the intended target directory.
- Audit `internal-sftp` command lines with ten or more arguments. Older
  releases silently discarded the tenth and later arguments, potentially
  dropping a security option.

### Avoid the `ControlPersist` terminal regression

Do not leave interactive terminal users on the affected release when
`ControlPersist` is active; the following release fixes the terminal state.

## High-use cryptography and key changes

### Account for post-quantum key-exchange defaults

- Expect `mlkem768x25519-sha256` to be the default key exchange.
- Expect cipher preference to be ChaCha20/Poly1305, AES-GCM 128/256, then
  AES-CTR 128/192/256.
- Expect a default-on warning when negotiation selects a non-post-quantum key
  exchange; control it with `WarnWeakCrypto`.
- Plan to remove SHA1 SSHFP dependencies. The client warns that SHA1 records
  will eventually be ignored, and `ssh-keygen -r` emits only SHA256 records.

### Opt in to the experimental composite signature

Generate the ML-DSA 44 and Ed25519 composite key type with:

```sh
ssh-keygen -t mldsa44-ed25519
```

The scheme is disabled by default. Add it explicitly to applicable lists such
as `HostKeyAlgorithms` and `PubkeyAcceptedAlgorithms`; generating a key does
not enable negotiation.

### Keep algorithm policy exact

- Expect invalid cipher and MAC lists to fail during configuration processing,
  not later at runtime.
- An ECDSA name in `PubkeyAcceptedAlgorithms` or
  `HostbasedAcceptedAlgorithms` admits only that exact ECDSA algorithm.
- Read [cryptography-and-keys.md](references/cryptography-and-keys.md) before
  changing revocation files, resident-key downloads, or PKCS#8 workflows.

## High-use configuration and authentication changes

### Use the expanded match criteria

Use `Match version` in client or server configuration. On clients, also use
`Match sessiontype` and `Match command`; session types are `shell`, `exec`,
`subsystem`, and `none`.

```sshconfig
Match version OpenSSH_10.*
    SetEnv GENERATION=10
```

Use `Match tagged ""` or `Match command ""` when an empty value must match
explicitly.

### Refuse a destination from client configuration

Use `RefuseConnection` inside an active `Host` or `Match` block to stop
processing with a useful error.

```sshconfig
Match host old.example
    RefuseConnection "old.example is retired; use new.example"
```

### Apply expansion and authorization globs deliberately

- Percent-token and environment expansion applies to client `SetEnv` and
  `User`; `%r` and `%C` are excluded from `User` to avoid self-reference.
- Server `AuthorizedKeysFile` and `AuthorizedPrincipalsFile` accept `glob(3)`
  patterns.

```sshconfig
AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys.d/*
```

### Re-check forwarding and GSSAPI policy

- Rely on `DisableForwarding=yes` to override `PermitTunnel=yes` only on a
  server with the fixed behavior. On older servers, set `PermitTunnel=no`.
- Do not rely on `GSSAPIStrictAcceptorCheck` for a server joined to Windows
  Active Directory; it is ineffective there.
- Upgrade GSSAPI-enabled servers for the pre-authentication denial-of-service
  fix and restored minimum authentication delays. `MaxAuthTries` did not
  mitigate the older path, but `PerSourcePenalties` applied.
- Use `invaliduser` and floating-point durations for finer penalties.

```sshconfig
PerSourcePenalties invaliduser:10s authfail:0.5s
```

### Re-test configuration consumers

`sshd -G` emits mixed-case directive names such as `PubkeyAuthentication`.
Parsers must accept the emitted casing instead of matching lowercase names
literally.

## High-use agent and connection changes

### Handle the agent socket migration

Local and forwarded agent sockets use hostname-hashed paths under
`~/.ssh/agent` instead of `/tmp`.

- Use `ssh-agent -T` only when the legacy `/tmp` layout is required.
- Use `-U` to suppress stale-socket cleanup, `-u` for cleanup only, and `-uu`
  to ignore the hostname during cleanup.
- Remove tooling assumptions that agent sockets always live under `/tmp`.

### Control key lifetime and agent operations

- Send `SIGUSR1` to an agent to clear all keys.
- Use systemd-style socket activation only with `LISTEN_PID`/`LISTEN_FDS` and
  `ssh-agent -d` or `-D` without an explicit socket path.
- Certificates loaded into an agent expire five minutes after their own
  expiry; pass `ssh-add -N` to disable this automatic lifetime.
- Use `ssh-add -Q` to report supported agent extensions.

### Re-test transport policy

- Interactive-only traffic defaults to EF, non-interactive traffic uses the
  operating-system default, and the selection changes as channels change.
- Remove `lowdelay`, `reliability`, and `throughput`; they are ignored.
- Server `IPQoS` uses first-match-wins precedence and accepts the VA codepoint.
- `UnusedConnectionTimeout` begins only after the final channel closes.

## High-use file-transfer changes

- `scp` and `sftp` invoke `ssh` with `ControlMaster no`: they reuse an existing
  master but do not create one implicitly.
- `sftp ls -ln` prints numeric user and group IDs. Remove workarounds for the
  earlier name output.
- For root downloads using legacy `scp -O`, pass `-p` when preserving setuid or
  setgid bits is intentional; otherwise those bits are cleared.

## Migration checklist

- Install and permit execution of `sshd-auth`.
- Test Linux sandbox initialization in the deployment runtime.
- Validate cipher, MAC, and exact ECDSA algorithm lists.
- Exercise post-authentication rekey with non-OpenSSH peers.
- Test `sshd -G` consumers with mixed-case directive names.
- Audit long `internal-sftp` invocations and untrusted transfer paths.
- Test agent discovery, expiry, locking, and forwarded-agent restrictions.
- Review GSSAPI, forwarding, certificate-principal, identity-validation, and
  per-source penalty policy in the detailed references.
