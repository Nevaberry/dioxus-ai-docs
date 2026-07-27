# Connections and Privilege Escalation

The connection changes in this reference are attributed to batch
`2.19-2.20`.

## SSH Password and Agent Handling

The SSH connection defaults to `SSH_ASKPASS` for passwords.
`ansible`, `ansible-playbook`, and `ansible-console` can spawn or reuse an SSH
agent.

The variables `ansible_ssh_private_key` and
`ansible_ssh_private_key_passphrase` allow a private key and its passphrase to
be loaded from variables. Keep these values under the same secret-handling
controls as key files and vault data.

Use `SSH_AGENT_EXECUTABLE` to select the agent executable. Use
`ANSIBLE_SSH_VERBOSITY` or the inventory variable `ansible_ssh_verbosity` to
increase SSH-only verbosity without increasing all Ansible output.

## Paramiko and Transport Configuration

The Paramiko connection is deprecated for removal in 2.21. Migrate explicit
`paramiko` inventory settings and connection dependencies to the SSH
connection before using that release.

The following configuration was removed in 2.20:

- `DEFAULT_TRANSPORT=smart`
- `PARAMIKO_HOST_KEY_AUTO_ADD`
- `PARAMIKO_LOOK_FOR_KEYS`

Remove these settings rather than attempting to preserve their old selection
or key-discovery behavior.

## Local Connection Become Behavior

The local connection adds two become settings:

| Setting | Default | Effect |
| --- | --- | --- |
| `become_strip_preamble` | `true` | Strips the privilege-escalation preamble |
| `become_success_timeout` | 10 seconds | Limits the wait for successful escalation |

If automation parses become output, test it with preamble stripping enabled.
If escalation legitimately takes longer, set a deliberate success timeout
instead of relying on an unbounded wait.

The `sudo_chdir` setting changes directory before invoking `sudo`. Account for
the pre-escalation working directory when commands depend on relative paths,
environment files, or directory permissions.
