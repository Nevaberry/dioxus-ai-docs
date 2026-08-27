# Connections and Privilege Escalation

## SSH password and key handling

The SSH connection defaults to `SSH_ASKPASS` for password prompting
(`2.19-2.20`). The `ansible`, `ansible-playbook`, and `ansible-console`
commands can create or reuse an SSH agent.

Inventory variables can provide a private key and its passphrase:

```yaml
ansible_ssh_private_key: "{{ vault_private_key }}"
ansible_ssh_private_key_passphrase: "{{ vault_private_key_passphrase }}"
```

Use `SSH_AGENT_EXECUTABLE` to select the SSH agent executable. Use
`ANSIBLE_SSH_VERBOSITY` or `ansible_ssh_verbosity` when extra diagnostics
should apply only to the SSH connection.

## Paramiko and removed settings

The Paramiko connection was deprecated for removal in 2.21. Migrate
configuration and inventory to the SSH connection rather than introducing or
retaining a Paramiko dependency.

The following configuration was removed in 2.20:

- `DEFAULT_TRANSPORT=smart`
- `PARAMIKO_HOST_KEY_AUTO_ADD`
- `PARAMIKO_LOOK_FOR_KEYS`

## Local become behavior

The local connection has these become settings:

- `become_strip_preamble` defaults to true.
- `become_success_timeout` defaults to 10 seconds.

Account for the stripped preamble when parsing become output and for the
timeout when privilege escalation is slow. `sudo_chdir` changes the working
directory before invoking `sudo`.

## Sensitive Windows transport output

Since the 2.19.10/2.20.6 patch lines, PSRP and WinRM do not log raw standard
output and standard error at verbosity 5 when `no_log: true` is set. Do not
add logging workarounds that would re-expose those secrets.
