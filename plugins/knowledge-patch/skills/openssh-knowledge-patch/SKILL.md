---
name: openssh-knowledge-patch
description: OpenSSH
license: MIT
version: "10.4"
metadata:
  author: Nevaberry
---

# OpenSSH Knowledge Patch

## Use this patch

1. Identify the target client and server versions before changing algorithms, authentication, forwarding, agent handling, or file-transfer automation.
2. Separate client behavior from server behavior. Defaults and validation often changed on only one side.
3. Read the matching topic reference before editing `ssh_config`, `sshd_config`, packaging, parsers, or scripts.
4. Preserve explicit compatibility exceptions only when the peer requires them; do not re-enable removed algorithms as a general default.
5. Treat security fixes as upgrade requirements when an older release cannot enforce the intended policy.
6. Re-test configuration dumps and human-readable command output before relying on literal casing, names, or formatting.

## Reference index

| Reference | Topics |
| --- | --- |
| [cryptography-and-keys.md](references/cryptography-and-keys.md) | Removed algorithms, post-quantum defaults, warnings, certificates, key formats, FIDO, revocation |
| [configuration-and-authentication.md](references/configuration-and-authentication.md) | Server packaging and sandboxing, matching and expansion, authorization, forwarding, GSSAPI, penalties |
| [connections-and-agents.md](references/connections-and-agents.md) | Rekey behavior, QoS, multiplexing, timeouts, agent lifecycle, sockets, extensions |
| [file-transfer.md](references/file-transfer.md) | `scp`, `sftp`, destination containment, `internal-sftp`, listings, mode preservation |

## Breaking changes and deprecations

### Remove assumptions about legacy algorithms

- Treat DSA signatures as unavailable. OpenSSH 10.0 removes DSA support entirely.
- Do not assume the server offers finite-field `diffie-hellman-group*` or `diffie-hellman-group-exchange-*` methods by default. Their client defaults did not change at the same time.
- Do not depend on compiled-in groups when a moduli file exists but contains no suitable groups; that condition no longer falls back.
- Remove XMSS keys before moving to 10.1 or later.
- Upgrade or replace peers that cannot rekey before using 10.3 or later.

### Install the split authentication executable

OpenSSH 10.0 moves per-connection user authentication from `sshd-session` into `sshd-auth`.

- Include `sshd-auth` in portable packages, custom install manifests, images, and integrity policies.
- Include `sshd-auth` when assigning authentication-phase log messages to executables.
- Diagnose missing-binary authentication failures as packaging defects, not configuration failures.

### Make sandbox support an explicit build decision

On Linux seccomp builds, failure to enable seccomp or `NO_NEW_PRIVS` is fatal in 10.4.

- Ensure both facilities work in the target runtime.
- Disable the sandbox at configure time when the platform cannot provide them.
- Do not rely on the former log-and-continue path.

### Enforce rekey interoperability

OpenSSH 10.4 disconnects a peer that sends a non-key-exchange message during post-authentication rekey.

- Fix peers that violate RFC 4253 section 7.1 instead of suppressing the disconnect.
- Upgrade clients to receive the fix for a use-after-free triggered when a server changes its host key during rekey.

### Upgrade for transfer containment

- Upgrade clients that download from untrusted servers: `sftp host:/path .` now prevents a server from choosing an unexpected local destination.
- Upgrade remote-to-remote `scp` clients: a malicious server can no longer write into the parent of the intended target directory.
- Audit `internal-sftp` command lines with ten or more arguments. Older releases discard the tenth and later arguments and may silently lose a security option.

### Avoid the 10.1 `ControlPersist` regression

Do not leave interactive terminal users on OpenSSH 10.1 when `ControlPersist` is active; 10.2 fixes the terminal-state regression.

## High-use cryptography and key changes

### Account for the post-quantum key-exchange default

- Expect `mlkem768x25519-sha256` to be the default key exchange from 10.0.
- Expect cipher preference to be ChaCha20/Poly1305, AES-GCM 128/256, then AES-CTR 128/192/256.
- From 10.1, expect a default-on warning when negotiation selects a non-post-quantum key exchange; control it with `WarnWeakCrypto`.
- Plan to remove SHA1 SSHFP dependencies. The client warns that SHA1 records will eventually be ignored, and `ssh-keygen -r` emits only SHA256 records.

### Opt in to the experimental composite signature

OpenSSH 10.4 supports the disabled-by-default ML-DSA 44 and Ed25519 composite key type.

```sh
ssh-keygen -t mldsa44-ed25519
```

Add it explicitly to relevant lists such as `HostKeyAlgorithms` and `PubkeyAcceptedAlgorithms`; key generation alone does not enable negotiation.

### Keep algorithm policy exact

- Expect invalid cipher and MAC lists to fail during configuration processing rather than later at runtime.
- On 10.3 or later, an ECDSA name in `PubkeyAcceptedAlgorithms` or `HostbasedAcceptedAlgorithms` admits only that exact ECDSA algorithm.
- Read [cryptography-and-keys.md](references/cryptography-and-keys.md) before changing revocation files, resident-key downloads, or PKCS#8 workflows.
- Read [configuration-and-authentication.md](references/configuration-and-authentication.md) before changing certificate-principal authorization.

## High-use configuration and authentication changes

### Use the new match criteria

Use `Match version` in client or server configuration. On clients, also use `Match sessiontype` and `Match command`; session types are `shell`, `exec`, `subsystem`, and `none`.

```sshconfig
Match version OpenSSH_10.*
    SetEnv GENERATION=10
```

Use `Match tagged ""` or `Match command ""` when an empty value must match explicitly.

### Refuse destinations from configuration

Use `RefuseConnection` inside an active client `Host` or `Match` block to stop processing with a useful error.

```sshconfig
Match host old.example
    RefuseConnection "old.example is retired; use new.example"
```

### Apply expansion and file globs deliberately

- Allow percent-token and environment expansion in client `SetEnv` and `User` values.
- Exclude self-referential `%r` and `%C` when expanding `User`.
- Use `glob(3)` patterns in server `AuthorizedKeysFile` and `AuthorizedPrincipalsFile` when authorization data is split across files.

```sshconfig
AuthorizedKeysFile .ssh/authorized_keys .ssh/authorized_keys.d/*
```

### Re-check forwarding and authentication policy

- On 10.4, rely on `DisableForwarding=yes` to override `PermitTunnel=yes`. On older servers, set `PermitTunnel=no` explicitly.
- Do not rely on `GSSAPIStrictAcceptorCheck` on a server joined to Windows Active Directory; it is ineffective there.
- Upgrade servers using GSSAPI authentication for the pre-authentication denial-of-service fix and restored minimum authentication delays.
- Use `PerSourcePenalties` rather than `MaxAuthTries` as mitigation for the older GSSAPI denial-of-service path.
- On 10.3 or later, distinguish nonexistent users with `invaliduser` and use floating-point durations for subsecond penalties.

```sshconfig
PerSourcePenalties invaliduser:10s authfail:0.5s
```

## High-use agent and connection changes

### Handle the agent socket migration

From 10.1, local and forwarded agent sockets use hostname-hashed paths under `~/.ssh/agent` instead of `/tmp`.

- Use `ssh-agent -T` only when the legacy `/tmp` layout is required.
- Use `-U` to suppress stale-socket cleanup, `-u` to perform cleanup only, and `-uu` to ignore the hostname during cleanup.
- Expect tooling that hard-codes `/tmp` agent paths to fail after the migration.

### Control key lifetime and agent operations

- Send `SIGUSR1` to a 10.0-or-later agent to clear all keys.
- Use systemd-style socket activation only with `LISTEN_PID`/`LISTEN_FDS` and `ssh-agent -d` or `-D` without an explicit socket path.
- Expect certificates added from 10.1 onward to expire from the agent five minutes after their certificate expiry.
- Pass `ssh-add -N` when automatic certificate lifetime enforcement must be disabled.
- Use `ssh-add -Q` on 10.3 or later to report supported agent extensions.

### Re-test transport policy

- Account for dynamic `IPQoS`: interactive-only traffic defaults to EF, non-interactive traffic uses the operating-system default, and the selection changes as channels change.
- Remove legacy `lowdelay`, `reliability`, and `throughput` values because they are ignored.
- On 10.3 servers, rely on normal first-match-wins precedence for `IPQoS`; the VA codepoint is also accepted.
- Expect `UnusedConnectionTimeout` to begin only after the final channel closes on 10.3 or later.

## High-use file-transfer changes

- Expect `scp` and `sftp` to invoke `ssh` with `ControlMaster no`. They reuse an existing master but do not create one implicitly.
- Expect `sftp ls -ln` to print numeric user and group IDs on 10.4; remove workarounds for the earlier name output.
- For root downloads using legacy `scp -O`, pass `-p` when setuid or setgid preservation is intentional. From 10.3, those bits are otherwise cleared.

## Migration checklist

- Install and permit execution of `sshd-auth`.
- Test server sandbox initialization in the deployment environment.
- Validate algorithm lists and exact ECDSA allowlists.
- Exercise post-authentication rekey against non-OpenSSH peers.
- Test `sshd -G` consumers with mixed-case directive names.
- Audit long `internal-sftp` invocations and untrusted transfer paths.
- Test agent discovery after the socket-layout change.
- Review GSSAPI, forwarding, certificate-principal, and per-source penalty policy in the detailed references.
