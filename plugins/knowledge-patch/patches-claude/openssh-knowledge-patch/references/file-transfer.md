# File Transfer

## Destination containment

### Contain SFTP local destinations

OpenSSH 10.4 prevents a malicious server from choosing an unexpected local
destination for command-line downloads such as:

```sh
sftp host:/path .
```

Upgrade clients that retrieve files from untrusted servers rather than trying
to validate a server-selected path after the transfer.

### Contain remote-to-remote SCP destinations

OpenSSH 10.4 prevents a malicious server participating in a remote-to-remote
`scp` transfer from writing into the parent of the intended target directory.
Upgrade clients that coordinate such transfers with untrusted servers.

## SFTP server invocation and output

### Preserve every `internal-sftp` argument

Before the OpenSSH 10.4 fix, long `internal-sftp` command lines silently
discarded the tenth and later arguments. This could drop a security-relevant
option. Audit invocations with ten or more arguments and upgrade instead of
depending on options after the ninth position.

### Consume numeric long listings

In OpenSSH 10.4, `sftp ls -ln` prints numeric user and group IDs as requested.
Earlier releases incorrectly printed names. Remove parsing workarounds that
translated or otherwise compensated for the old output.

## Multiplexing behavior

### Do not expect transfers to create control masters

From OpenSSH 10.0, `scp` and `sftp` invoke `ssh` with `ControlMaster no`.
A configured `ControlMaster yes` or `auto` no longer makes a transfer create a
multiplexing master implicitly. The transfer still reuses a master that already
exists. Start a master explicitly when later operations depend on one.

## Legacy SCP mode preservation

### Opt in to preserving privileged bits as root

From OpenSSH 10.3, root downloads made with legacy `scp -O` clear setuid and
setgid bits unless `-p` explicitly requests mode preservation. Add `-p` only
when automation intentionally preserves those bits; otherwise retain the safer
default.
