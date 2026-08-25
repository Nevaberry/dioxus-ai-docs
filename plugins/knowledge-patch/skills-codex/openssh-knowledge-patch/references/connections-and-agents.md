# Connections and Agents

## Rekeying and multiplexed forwarding

### Enforce post-authentication rekey rules (batch 10.4)

Clients and servers disconnect peers that send non-key-exchange messages during
a post-authentication rekey. Implementations that violate RFC 4253 section 7.1
may stop interoperating and should be fixed rather than exempted. The client
also fixes a use-after-free triggered when a server changes its host key during
rekey, so upgrade exposed clients.

### Upgrade peers that cannot rekey (batch 10.0-10.3)

OpenSSH 10.3 removes compatibility for peers that cannot rekey. Inventory and
upgrade those peers before deployment; do not restore obsolete behavior as a
broad compatibility setting.

### Avoid the remote-forwarding race (batch 10.5)

The client fixes a possible realloc use-after-free when a remote forwarding is
added through the local multiplexing socket while another remote-forward open
request is pending. Upgrade clients whose automation changes remote forwards
concurrently over one shared control connection.

### Avoid the `ControlPersist` terminal regression (batch 10.0-10.3)

OpenSSH 10.1 could leave terminal sessions unusable while `ControlPersist` was
active. OpenSSH 10.2 fixes it; interactive systems using persistent control
sockets should not remain on 10.1.

## Agent process and socket lifecycle

### Clear keys and use socket activation (batch 10.0-10.3)

- From 10.0, send `SIGUSR1` to `ssh-agent` to clear all keys.
- Systemd-style socket activation requires `LISTEN_PID` and `LISTEN_FDS`, with
  `ssh-agent -d` or `-D` and no explicit socket path.

### Migrate agent socket discovery (batch 10.0-10.3)

From 10.1, local and forwarded agent sockets use hostname-hashed paths under
`~/.ssh/agent` instead of `/tmp`.

- `ssh-agent -T` restores the legacy `/tmp` layout.
- `-U` suppresses stale-socket cleanup.
- `-u` performs cleanup only; `-uu` also ignores the hostname during cleanup.

Update software that scans or hard-codes `/tmp` agent socket paths.

### Enforce certificate lifetimes (batch 10.0-10.3)

From 10.1, `ssh-add` gives a loaded certificate a lifetime ending five minutes
after the certificate's own expiry, after which the agent removes it. Pass
`ssh-add -N` when automatic certificate lifetime enforcement must be disabled.

## Agent forwarding and extensions

### Preserve restrictions while an agent is locked (batch 10.5)

The fixed agent processes `session-bind@openssh.com` while locked. Previously,
refusing that request could allow remote users of a forwarded agent to perform
operations meant to be local-only. Upgrade forwarded agents, especially those
that can add PKCS#11 tokens or hold destination-restricted keys.

### Use standardized forwarding extensions (batch 10.0-10.3)

OpenSSH 10.3 supports IANA-assigned agent-forwarding codepoints and prefers
them when advertised through `EXT_INFO`, while retaining the older
`@openssh.com` names for compatibility. `ssh-agent` implements the standardized
`query` extension, and `ssh-add -Q` reports supported agent extensions. Accept
both standardized and compatibility names when interoperating with older
implementations.

## Transport policy and idle connections

### Account for dynamic `IPQoS` (batch 10.0-10.3)

- From 10.1, interactive-only traffic defaults to EF and non-interactive
  traffic uses the operating-system default. Selection changes dynamically as
  channel types change.
- Legacy `lowdelay`, `reliability`, and `throughput` values are ignored.
- From 10.3, the server applies normal first-match-wins precedence to `IPQoS`
  and accepts the VA codepoint.

Do not infer a connection's permanent QoS marking from its first channel.

### Start unused-connection timing after all channels close (batch 10.0-10.3)

From 10.3, `UnusedConnectionTimeout` starts only after the final channel
closes. A preceding `ChannelTimeout` no longer starts it early. API clients may
therefore keep a transport alive to open later channels after earlier channels
have closed.
