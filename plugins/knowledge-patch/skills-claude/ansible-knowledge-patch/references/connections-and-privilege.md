# Connections and Privilege Escalation

## SSH password and key handling

The SSH connection in `2.19-2.20` defaults to `SSH_ASKPASS` for password
prompts. The `ansible`, `ansible-playbook`, and `ansible-console` commands can
spawn or reuse an SSH agent.

Use `ansible_ssh_private_key` together with
`ansible_ssh_private_key_passphrase` to load a private key supplied through
variables. `SSH_AGENT_EXECUTABLE` selects the agent binary.

For verbosity limited to the SSH connection, use the
`ANSIBLE_SSH_VERBOSITY` environment variable or the
`ansible_ssh_verbosity` inventory variable. Do not increase global verbosity
when only transport diagnostics are needed.

## Paramiko migration and removed settings

The Paramiko connection is deprecated in `2.19-2.20` for removal in 2.21.
Migrate inventories and configuration to the SSH connection instead of adding
new Paramiko dependencies.

These settings are removed in 2.20:

- `DEFAULT_TRANSPORT=smart`
- `PARAMIKO_HOST_KEY_AUTO_ADD`
- `PARAMIKO_LOOK_FOR_KEYS`

Delete compatibility code that writes or depends on those settings.

## Local become behavior

The local connection in `2.19-2.20` adds two become controls:

- `become_strip_preamble`, which defaults to true.
- `become_success_timeout`, which defaults to 10 seconds.

Tests that parse privilege-escalation output must account for preamble
stripping. Slow local escalation flows may need a deliberate timeout override.

`sudo_chdir` changes directory before invoking `sudo`; it does not change
directory only after privilege escalation.
