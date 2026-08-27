# Connections and Agents

## Rekey and connection lifetime

### Enforce post-authentication rekey sequencing

OpenSSH 10.4 clients and servers disconnect peers that send a non-key-exchange
message during a post-authentication rekey. Test non-OpenSSH implementations
for compliance with RFC 4253 section 7.1 and fix peers that violate the
sequence.

The same release fixes a client use-after-free triggered when a server changes
its host key during rekey. Upgrade exposed clients. OpenSSH 10.3 also drops
compatibility with peers that cannot rekey at all.

### Start unused-connection timing after the final channel

In OpenSSH 10.3, `UnusedConnectionTimeout` starts only after the last channel
closes. A preceding `ChannelTimeout` no longer starts it early. API clients may
therefore keep the transport available for later channels after earlier ones
have closed.

## Multiplexing and forwarding

### Avoid the 10.1 `ControlPersist` terminal regression

OpenSSH 10.1 could leave terminal sessions unusable whenever `ControlPersist`
was active. OpenSSH 10.2 fixes the regression. Upgrade interactive systems that
use persistent control sockets.

### Upgrade clients that add remote forwards concurrently

OpenSSH 10.5 fixes a potential realloc use-after-free in the client. It can be
triggered when a remote forwarding is added through the local multiplexing
socket while another remote-forward open request is still pending. Upgrade
automation that changes remote forwards concurrently over a shared control
connection.

## Traffic policy

### Apply dynamic `IPQoS`

OpenSSH 10.1 makes `IPQoS` depend on active channel types: interactive-only
traffic defaults to EF, non-interactive traffic uses the operating-system
default, and the choice changes as channels change.

Legacy `lowdelay`, `reliability`, and `throughput` values are ignored. OpenSSH
10.3 adds the VA codepoint and makes server `IPQoS` follow normal
first-match-wins configuration precedence. Remove legacy values and test mixed
interactive and non-interactive sessions.

## Agent lifecycle and sockets

### Clear keys and use socket activation correctly

From OpenSSH 10.0, sending `SIGUSR1` clears all keys from `ssh-agent`.
Systemd-style socket activation is supported when `LISTEN_PID` and
`LISTEN_FDS` are set and the agent runs with `-d` or `-D` without an explicit
socket path. Do not combine activation with a manually selected socket path.

### Migrate agent socket discovery

OpenSSH 10.1 moves local and forwarded agent sockets from `/tmp` to
hostname-hashed paths below `~/.ssh/agent`.

- `ssh-agent -T` restores the legacy `/tmp` layout when compatibility requires
  it.
- `-U` suppresses stale-socket cleanup.
- `-u` performs cleanup only.
- `-uu` performs cleanup while ignoring the hostname.

Update tools that scan or hard-code `/tmp` socket paths.

### Enforce certificate lifetime in the agent

From OpenSSH 10.1, `ssh-add` gives a loaded certificate a lifetime ending five
minutes after the certificate's own expiry. The agent then removes it. Use
`ssh-add -N` when automatic certificate lifetime enforcement must be disabled.

## Agent protocol and forwarding boundaries

### Prefer standardized forwarding extensions

OpenSSH 10.3 supports the IANA-assigned agent-forwarding codepoints and prefers
them when they are advertised through `EXT_INFO`. The older `@openssh.com`
names remain available for compatibility. `ssh-agent` implements the
standardized `query` extension, and `ssh-add -Q` reports extensions supported
by an agent.

### Enforce binding while a forwarded agent is locked

OpenSSH 10.5 fixes `ssh-agent` refusing `session-bind@openssh.com` requests
while locked. The refusal could allow remote users of a forwarded agent to
perform operations intended to be local-only. Upgrade forwarded agents,
especially agents that can add PKCS#11 tokens or contain
destination-restricted keys.
