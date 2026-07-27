# Connections and Agents

## Post-authentication rekey

OpenSSH 10.4 disconnects clients or servers that send non-key-exchange messages during a post-authentication key re-exchange. Bring peers into compliance with RFC 4253 section 7.1; implementations that relied on leniency may stop interoperating.

The same release fixes a client use-after-free triggered when a server changes its host key during rekey. Upgrade exposed clients rather than avoiding rekey as a workaround.

OpenSSH 10.3 also removes compatibility for peers that cannot rekey at all. Replace or upgrade those peers.

## Dynamic IPQoS

OpenSSH 10.1 changes the default `IPQoS` behavior:

- Use EF for interactive-only traffic.
- Use the operating-system default for non-interactive traffic.
- Switch dynamically as channel types change.

Legacy `lowdelay`, `reliability`, and `throughput` values are ignored. Remove them instead of expecting their former mappings.

OpenSSH 10.3 accepts the VA codepoint and makes server `IPQoS` follow normal first-match-wins configuration precedence. Put the preferred value in the earliest applicable block.

## Multiplexing regression

OpenSSH 10.1 can leave terminal sessions unusable when `ControlPersist` is active. OpenSSH 10.2 fixes the regression. Avoid 10.1 for persistent control sockets, especially for interactive sessions.

## Idle connection timing

From 10.3, `UnusedConnectionTimeout` becomes active only after the last channel closes. A preceding `ChannelTimeout` no longer starts it early. API clients may therefore keep a transport alive and open later channels after earlier channels close, up to the configured unused-connection limit.

## Agent key clearing and socket activation

From 10.0, send `SIGUSR1` to `ssh-agent` to clear all loaded keys.

The agent also supports systemd-style socket activation when `LISTEN_PID` and `LISTEN_FDS` are set. Run `ssh-agent` with `-d` or `-D` and without a socket path in this mode; supplying a path defeats the activation contract.

## Agent socket layout and cleanup

From 10.1, local and forwarded agent sockets move from `/tmp` to hostname-hashed paths under `~/.ssh/agent`.

- Use `-T` to restore the `/tmp` layout.
- Use `-U` to suppress stale-socket cleanup.
- Use `-u` to perform cleanup only.
- Use `-uu` to perform cleanup while ignoring the hostname.

Update scripts and service units that assume the socket lives below `/tmp`.

## Certificate lifetime in the agent

From 10.1, `ssh-add` assigns a loaded certificate a lifetime ending five minutes after the certificate's own expiry. The agent removes it at that point. Use `ssh-add -N` when automatic lifetime assignment must be disabled.

## Standard agent-forwarding extensions

OpenSSH 10.3 supports the IANA-assigned agent-forwarding codepoints and prefers them when the peer advertises them through `EXT_INFO`. It retains the older `@openssh.com` names for compatibility.

`ssh-agent` implements the standardized `query` extension. Use `ssh-add -Q` to report the extensions an agent supports instead of inferring them from its version.
