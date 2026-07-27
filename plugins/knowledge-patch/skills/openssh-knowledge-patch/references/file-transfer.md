# File Transfer

## Multiplexing behavior

From OpenSSH 10.0, `scp` and `sftp` invoke `ssh` with `ControlMaster no`. A transfer may reuse a multiplexing master that already exists, but a configured `ControlMaster yes` or `auto` no longer causes it to create one implicitly.

Start a master explicitly when transfer automation depends on one. Do not diagnose successful reuse as evidence that the transfer client can still create it.

## Destination containment

OpenSSH 10.4 contains destinations chosen by untrusted servers:

- In `sftp host:/path .`, the server can no longer select an unexpected local destination.
- In remote-to-remote `scp`, a malicious server can no longer write into the parent of the intended target directory.

Upgrade clients that connect to untrusted or mutually untrusted servers; destination sanitization in calling scripts is not a complete replacement for the client fixes.

## Long `internal-sftp` command lines

Before 10.4, long `internal-sftp` invocations silently discard the tenth and later arguments. Audit every invocation with ten or more arguments: a security-relevant option placed after the ninth argument may never have taken effect.

Upgrade rather than relying on later positions. When an immediate upgrade is impossible, shorten or reorder the invocation so every required option is within the first nine arguments, then verify the effective behavior.

## Numeric SFTP listings

In 10.4, `sftp ls -ln` prints numeric user and group IDs as requested. Earlier releases incorrectly printed names. Remove scripts that translate or compensate for the old output, and test parsers against numeric fields.

## Legacy SCP downloads as root

From 10.3, root downloads made with legacy `scp -O` clear setuid and setgid bits unless `-p` explicitly requests mode preservation.

- Omit `-p` for the safer default.
- Add `-p` only when preserving those bits is intentional and the source is trusted.
- Update automation that previously assumed root plus `-O` preserved all mode bits automatically.
