# Plugins and Extensions

## Controller-side task forks

Controller-side task forks no longer provide functional standard input,
standard output, or standard error streams (`2.19-2.20`). Use Ansible's
`Display` facility for plugin messages rather than writing to those streams.

Values supplied by Ansible may subclass Python builtins. Convert them to plain
Python types before passing them to libraries that reject subclasses.

## Callback plugins

Callback plugins must inherit from `CallbackBase`. The v1 callback API and
`v2_on_any` are deprecated; implement the specific `v2_` callbacks that match
the events the plugin consumes.

The `oneline` and `tree` callback plugins are deprecated, as are their `-o`
and `-t` command arguments. Do not make integrations depend on those callback
surfaces.

## Strategy and Jinja extensions

Third-party strategy plugins are deprecated with no planned replacement.
Custom Jinja extensions are also deprecated; replace them with filter, test,
or lookup plugins.

Builtin Jinja filters and tests can be addressed using their fully qualified
names, `ansible.builtin.<name>`.

Custom Jinja plugins must explicitly opt in before accepting an undefined
top-level argument. When a plugin uses `environment.getitem`, either catch
`MarkerError` and return a marker or opt in to receiving marker values. Review
[templating.md](templating.md) before changing how a plugin preserves trust or
handles lazy values.

## Vars plugins and variable access

Vars plugins no longer fall back to `get_host_vars` or `get_group_vars`. They
must inherit `BaseVarsPlugin` and implement `get_vars`.

The internal variable cache is deprecated for removal in 2.24. Use the `vars`
and `varnames` lookups instead.

## `module_utils` packages

Python packages nested below `module_utils` may include `__init__.py`. Account
for normal package initialization behavior when organizing shared module code.

## Collection discovery with compiled extensions

In `2.21.3`, the collection loader correctly returns Python modules when
`pkgutil.iter_modules()` scans a package within a collection path that contains
compiled Python extension modules. Avoid workarounds that assume such modules
cannot be discovered; retain compatibility handling only when older controller
versions still need it.
