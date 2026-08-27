---
name: ansible-knowledge-patch
description: Ansible Core
version: "2.21.2"
license: MIT
metadata:
  author: Nevaberry
---


# Ansible Core Knowledge Patch

Use this skill when changing Ansible playbooks, inventories, controller plugins,
connection settings, test targets, or modules that depend on current
`ansible-core` behavior.

## Working Method

1. Determine the installed or pinned `ansible-core` version from dependency
   manifests, execution-environment definitions, or lockfiles.
2. Inspect the affected playbooks and plugins for the migration points below.
3. Open the topic reference before changing behavior that depends on an exact
   configuration name, default, result type, or plugin API.
4. Prefer project tests and observed runtime behavior when a project carries
   compatibility shims or backports.

## Reference Index

| Reference | Topics |
| --- | --- |
| [templating.md](references/templating.md) | Trust, single-pass evaluation, native values, strict conditionals, lazy templating, `omit`, sandboxing, and JSON profiles |
| [plugins-and-extensions.md](references/plugins-and-extensions.md) | Controller-side I/O, callback and strategy migrations, Jinja plugins, markers, builtin names, vars plugins, and collection packages |
| [connections-and-privilege.md](references/connections-and-privilege.md) | SSH agents and askpass, Paramiko migration, connection verbosity, local become, and `sudo_chdir` |
| [playbooks-cli-and-inventory.md](references/playbooks-cli-and-inventory.md) | CLI flags, inventory parsing, diagnostics, deprecated play syntax, argument-spec validation, and Galaxy behavior |
| [modules-facts-and-windows.md](references/modules-facts-and-windows.md) | Fact access, file and package modules, result types, UTF-8 enforcement, Windows execution, and module patch behavior |
| [testing-runtime-and-security.md](references/testing-runtime-and-security.md) | `ansible-test` environments and timeout diagnostics, supported runtimes, maintenance dates, and security fixes |

## Highest-Priority Migration Checks

### Treat templating as trusted and single-pass

- Jinja expressions in untrusted strings, including facts and module results,
  are not evaluated merely because the strings contain delimiters.
- Preserve trust when a plugin transforms a value that is intended to remain a
  template. Apply trust explicitly when a plugin creates such a value.
- Remove designs that depend on one template producing another template for a
  later pass.
- Do not wrap ordinary conditionals in `{{ ... }}`. A whole trusted string
  expression is the narrow exception.

```yaml
# Preferred
when: service_enabled | bool

# Avoid
when: "{{ service_enabled | bool }}"
```

### Expect native values and boolean conditionals

- Template results retain native types; do not assume automatic string
  conversion.
- Do not assume `None` becomes an empty string.
- `set_fact` preserves the literal strings `yes`, `no`, `true`, and `false`
  when they are supplied as strings.
- A conditional must produce a boolean. Use an explicit comparison or a
  suitable conversion instead of relying on truthiness.
- Treat `ALLOW_BROKEN_CONDITIONALS` as a short-lived migration aid, not a
  permanent compatibility mode.

```yaml
- name: Use an explicit boolean conversion
  ansible.builtin.debug:
    msg: enabled
  when: feature_flag | bool
```

### Audit lazy values and `omit`

- Only accessed portions of a structure are templated, so errors may surface
  later than structure construction.
- `omit` is removed from its parent container during templating.
- In loops, use `default(omit)` on the value that should disappear from module
  arguments.
- Code calling `Templar.template()` must handle
  `AnsibleValueOmittedError` when the complete result is omitted.

```yaml
- ansible.builtin.user:
    name: "{{ item.name }}"
    shell: "{{ item.shell | default(omit) }}"
  loop: "{{ users }}"
```

## Plugin and Extension Quick Reference

### Controller-side code

- Task forks do not provide functional standard input, output, or error
  streams. Use `Display` for controller-side messages.
- Convert Ansible-provided subclasses of Python builtins to plain native types
  before passing them to strict third-party libraries.
- Builtin Jinja filters and tests may be addressed with the
  `ansible.builtin.<name>` form.
- Python packages below `module_utils` may contain `__init__.py`.

### Callback, strategy, vars, and Jinja migration

- Callback plugins must derive from `CallbackBase`.
- Replace the v1 callback API and `v2_on_any` with the specific `v2_`
  callbacks.
- Third-party strategy plugins are deprecated without a planned replacement.
- Replace custom Jinja extensions with filter, test, or lookup plugins.
- A Jinja plugin must explicitly opt in before accepting an undefined
  top-level argument.
- Code using `environment.getitem` must handle `MarkerError` and return a
  marker, or explicitly opt in to marker values.
- Vars plugins must inherit `BaseVarsPlugin` and implement `get_vars`.

## Connection and Privilege Quick Reference

### SSH authentication

- The SSH connection uses `SSH_ASKPASS` by default for password prompting.
- `ansible`, `ansible-playbook`, and `ansible-console` can create or reuse an
  SSH agent.
- `ansible_ssh_private_key` and
  `ansible_ssh_private_key_passphrase` can load a key from variables.
- Set `SSH_AGENT_EXECUTABLE` to choose the agent binary.
- Use `ANSIBLE_SSH_VERBOSITY` or `ansible_ssh_verbosity` for SSH-only
  verbosity.

### Deprecated transports and removed settings

- Migrate Paramiko connection use to the SSH connection.
- Remove `DEFAULT_TRANSPORT=smart`, `PARAMIKO_HOST_KEY_AUTO_ADD`, and
  `PARAMIKO_LOOK_FOR_KEYS`.
- For the local connection, account for `become_strip_preamble` defaulting to
  true and `become_success_timeout` defaulting to 10 seconds.
- `sudo_chdir` changes directory before invoking `sudo`.

## Playbook, CLI, and Inventory Quick Reference

- Use `--flush-cache` where cache invalidation is needed with `ansible`,
  `ansible-console`, or `ansible-pull`.
- Inventory files ending in `.ini` are parsed by default unless `ini` is put
  back into `INVENTORY_IGNORE_EXTS`.
- Use `DISPLAY_TRACEBACK` to control tracebacks; `-vvv` is not the traceback
  switch.
- Consume task-result `warnings` and `deprecations` when building diagnostic
  tooling.
- Prefer `--inventory` over the deprecated `--inventory-file` alias.
- Replace `play_hosts` with `ansible_play_batch`.
- Remove empty `args`, mapping-form `action`, and combinations of
  `key=value` arguments with `args`.
- Set `ansible_managed` as a regular variable instead of using
  `DEFAULT_MANAGED_STR`.

### Validate play arguments

Set `validate_argspec: true` to select the required play `name`, or use a
string to select another entry from `<playbook_name>.meta.yml`.

```yaml
# deploy.yml
- name: deploy
  hosts: all
  validate_argspec: true
```

```yaml
# deploy.meta.yml
argument_specs:
  deploy:
    options:
      environment:
        type: str
        required: true
```

## Modules, Facts, and Results Quick Reference

- Migrate injected top-level facts such as `ansible_os_distribution` to
  `ansible_facts['os_distribution']`.
- Prefer the `vars` and `varnames` lookups over the internal variable cache.
- Read per-volume-group logical volumes from each
  `ansible_facts['vgs']` entry's `lvs` subkey when completeness matters.
- `async_status.started` and `async_status.finished` are booleans, not integer
  flags.
- Pass lists to `include_vars.extensions` and `include_vars.ignore_files`.
- Use `encoding` with `blockinfile` and `lineinfile` for non-UTF-8 files.
- Expect `replace` to read, match, and write Unicode text.
- Review automatic dependency installation in `apt`, `dnf5`, and
  `deb822_repository` before relying on minimal target images.
- Treat non-UTF-8 module response strings as errors; disabling strict checking
  is a compatibility escape hatch.

## Test and Upgrade Checklist

- Exercise templates with facts and module-result strings containing literal
  Jinja delimiters.
- Test conditionals for genuine boolean results.
- Cover loop arguments that can resolve to `omit`.
- Run custom plugins without functional standard streams.
- Test SSH agent creation, key loading, and local become timeout behavior.
- Verify inventory discovery for `.ini` files.
- Assert boolean async-status fields in integrations.
- Run Windows automation under the intended PowerShell host and application
  control policy.
- Give `ansible-test` enough deadline headroom to emit pre-timeout thread
  diagnostics.
- Check the detailed references before removing compatibility workarounds.
