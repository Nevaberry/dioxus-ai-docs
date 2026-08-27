# Packaging, Runtime, and Service Integration

Use this reference when building packages, assembling images, overriding
services, rendering templates, or consuming command results.

## Packaging layout

### Installed files use `/usr/lib`

Since 25.1, packaged files install under `/usr/lib` rather than `/lib`
(guidance recorded in 26.1).

Review downstream assumptions in:

- package manifests and file lists;
- patches that use absolute installation paths;
- service definitions with hard-coded paths;
- image assembly logic that copies installed files; and
- tests that assert the old layout.

Do not retain `/lib` solely because an older package used that location.

### Meson replaces setuptools and distutils

Since 25.3, cloud-init builds with Meson instead of setuptools or distutils
(guidance recorded in 26.1). The Meson build also supports BSD.

When adapting a downstream package:

1. Remove assumptions that the setuptools or distutils entry point performs
   the build.
2. Use the Meson workflow expected by the package environment.
3. Inspect generated installation paths instead of translating old commands
   mechanically.
4. Reconcile package manifests and file lists against the actual Meson result.
5. Include the current BSD support when maintaining BSD packaging.

Treat the backend and installed-layout changes as related audit work, but verify
each independently.

## Runtime support

### Python 3.8 is unsupported

Python 3.8 is no longer supported (26.1). Do not select it as the interpreter
for a current build or package.

Check:

- the interpreter used during package builds;
- distribution dependency constraints;
- service shebangs or launch commands; and
- image tests that may still run under an older default interpreter.

## systemd integration

### Audit overridden `ExecStart=` commands

The socket protocol used by cloud-init's systemd units changed in 25.3 for
compatibility with alternatives such as `ncat -U` (guidance recorded in 26.1).
Downstream units that override `ExecStart=` must update their command.

Inspect the effective unit rather than only the vendor file:

```sh
systemctl cat cloud-init.service
```

If a drop-in or replacement unit supplies `ExecStart=`:

1. Compare it with the command in the current packaged unit.
2. Update it for the current socket protocol.
3. Verify startup and socket communication in the assembled image.

## Jinja rendering

Cloud-init renders Jinja templates in a sandbox (26.2). Existing custom
templates that use operations forbidden by the sandbox must be revised.

Migration checks:

- Render every custom template with the packaged cloud-init version.
- Replace access to forbidden operations with supported template inputs and
  expressions.
- Exercise error paths so a rejected template cannot leave an apparently
  successful but incomplete provisioning run.
- Keep the sandbox boundary intact; do not weaken it to preserve an old
  template.

## Mount configuration

The `mounts` module escapes special characters in mount paths when it writes
`fstab` (26.2). This lets paths containing those characters be represented
correctly.

Consumers that inspect or post-process generated `fstab` must retain the
escaping. Validate both the serialized entry and the resulting mount instead of
comparing against an unescaped literal path.

## Boot analysis

`analyze_boot` returns an integer exit code (26.2). Callers can treat the value
as conventional process status.

Update integrations that assumed a non-numeric result:

- propagate the integer through wrappers;
- use normal success and failure handling;
- avoid string-only comparisons; and
- test both zero and nonzero outcomes.
