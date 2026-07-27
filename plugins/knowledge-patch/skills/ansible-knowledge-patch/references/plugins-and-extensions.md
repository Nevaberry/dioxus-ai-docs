# Plugins and Extensions

These plugin migration points are attributed to batch `2.19-2.20`.

## Controller-Side Task Forks

Controller-side task forks no longer have functional stdin, stdout, or stderr.
Plugins executing there must send messages through `Display`; direct writes to
the standard streams are not a supported communication path.

Ansible values stored by templating can be subclasses of Python builtins.
Convert a value to its plain native type before passing it to a library that
performs exact type checks.

## Jinja Filters, Tests, and Extensions

Builtin Jinja filters and tests can be addressed by their fully qualified
names:

```jinja2
{{ value | ansible.builtin.default('fallback') }}
```

Custom Jinja extensions are deprecated. Implement the behavior as a filter,
test, or lookup plugin instead.

Custom Jinja plugins must explicitly opt in before they accept undefined
top-level arguments. A plugin using `environment.getitem` must choose one of
these marker-safe approaches:

- Catch `MarkerError` and return a marker.
- Explicitly opt in to receiving marker values.

Do not swallow a marker and return an ordinary value because that loses the
deferred undefined state.

## Callback Plugins

Callback plugins must derive from `CallbackBase`. The v1 callback API is
deprecated. The catch-all `v2_on_any` callback is also deprecated; implement
the applicable, specifically named `v2_` callbacks.

Task results can expose `warnings` and `deprecations`. Diagnostic callbacks
should read those fields where appropriate rather than depending only on
controller verbosity.

## Strategy Plugins

Third-party strategy plugins are deprecated, and there is no planned
replacement. Avoid creating a new dependency on a custom strategy. For an
existing strategy, isolate its behavior and plan a migration to supported
playbook, action, or plugin surfaces.

## Vars Plugins

Vars plugins no longer fall back to `get_host_vars` or `get_group_vars`.
Inherit from `BaseVarsPlugin` and implement `get_vars`.

The internal variable cache is deprecated for removal in 2.24. Use the `vars`
and `varnames` lookups instead of reaching into the internal cache.

## `module_utils` Packaging

Packages below `module_utils` may contain `__init__.py`. Use normal Python
package organization when it improves imports, while preserving collection
fully qualified names and target-side dependency constraints.
