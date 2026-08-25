# Plugins and Extensions

## Controller-side I/O

Controller-side task forks in `2.19-2.20` do not have functional standard
input, output, or error streams. Plugin code running there must use Ansible's
`Display` facility for messages rather than reading from or writing to the
standard streams.

## Callback and strategy plugins

Callback plugins in `2.19-2.20` must derive from `CallbackBase`. The v1
callback API and the catch-all `v2_on_any` callback are deprecated; implement
the applicable specific `v2_` callbacks.

Third-party strategy plugins are deprecated and have no planned replacement.
Account for that before adding or expanding a custom strategy dependency.

The `oneline` and `tree` callbacks are deprecated, along with their `-o` and
`-t` command-line arguments. Move result formatting and persistence to
supported callback surfaces.

## Jinja plugins and extensions

Custom Jinja extensions are deprecated in `2.19-2.20`. Reimplement their
behavior as filter, test, or lookup plugins. Builtin filters and tests can be
addressed with their fully qualified names, such as
`ansible.builtin.<name>`.

A Jinja plugin must opt in before accepting an undefined top-level argument.
When using `environment.getitem`, either catch `MarkerError` and return a
marker or explicitly opt in to marker values.

## Native Python values

Values supplied by Ansible in `2.19-2.20` can be subclasses of Python builtin
types. Convert them to plain builtins before passing them to a strict external
library. Packages below `module_utils` may contain `__init__.py`, so normal
package layouts are supported there.

## Vars plugin API

The legacy fallback to `get_host_vars` or `get_group_vars` is removed in
`2.19-2.20`. A vars plugin must inherit `BaseVarsPlugin` and implement
`get_vars`.

The internal variable cache is deprecated for removal in 2.24. Use the `vars`
and `varnames` lookups rather than reaching into the cache.

## Collection package discovery

In `2.21.3`, the collection loader returns Python modules correctly when
`pkgutil.iter_modules()` scans a package within a collection path that also
contains compiled Python extension modules. Package-discovery code should not
filter out valid modules merely because compiled extensions share the path.
