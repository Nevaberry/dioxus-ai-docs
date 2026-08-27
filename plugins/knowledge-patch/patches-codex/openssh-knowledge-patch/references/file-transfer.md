# File Transfer

## Connection multiplexing

### Do not implicitly create a control master (batch 10.0-10.3)

From OpenSSH 10.0, `scp` and `sftp` invoke `ssh` with `ControlMaster no`.
A transfer may reuse an already-running master, but configured `ControlMaster
yes` or `auto` no longer makes the transfer create one implicitly. Start a
master separately when automation depends on reuse.

## Destination containment

### Contain SFTP local destinations (batch 10.4)

The command form `sftp host:/path .` prevents a malicious server from choosing
an unexpected local destination. Upgrade clients that download from untrusted
servers rather than attempting to reproduce this containment in wrapper
scripts.

### Contain remote-to-remote SCP destinations (batch 10.4)

Remote-to-remote `scp` prevents a malicious server from writing into the parent
of the intended target directory. Upgrade clients used with untrusted servers
or partially trusted remote endpoints.

## Server command invocation

### Audit long `internal-sftp` command lines (batch 10.4)

Earlier releases silently discarded the tenth and subsequent arguments of an
`internal-sftp` command line. This could remove a security-relevant option.
Audit invocations with ten or more arguments and upgrade; do not depend on
arguments beyond the ninth position on an affected server.

## Listing and mode behavior

### Parse numeric SFTP listings (batch 10.4)

`sftp ls -ln` displays numeric user and group IDs as requested. Earlier
releases incorrectly printed names. Remove workarounds that translate or parse
the earlier name output, and test scripts against numeric fields.

### Preserve privileged mode bits only by request (batch 10.0-10.3)

From OpenSSH 10.3, root downloads made with legacy `scp -O` clear setuid and
setgid bits unless `-p` explicitly requests mode preservation. Automation that
intentionally preserves those bits must opt in with `-p`; otherwise retain the
safer clearing behavior.
