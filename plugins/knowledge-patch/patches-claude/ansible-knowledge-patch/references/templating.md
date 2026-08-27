# Templating, Values, and Conditionals

## Trusted, single-pass templating

In `2.19-2.20`, Jinja in a string is evaluated only when the string's source is
trusted. Playbooks, vars files, and many inventory sources are trusted; facts
and module results are not. Literal Jinja delimiters in an untrusted string do
not make it executable, and attempting to use such content as a template emits
a warning.

Plugins that create a template string must explicitly apply trust. Plugins that
transform one must preserve its trust metadata. Do not restore multi-pass
evaluation: a template result is not recursively evaluated as another template.

Embedded templates outside Jinja string constants are errors. Embedded
templates inside those constants warn. Write ordinary conditionals without
Jinja delimiters; only a complete, trusted string expression is a supported
exception.

```yaml
# Correct
when: service_state == 'running'

# Do not use delimiters for an ordinary conditional
when: "{{ service_state == 'running' }}"
```

Test facts and module return values containing literal `{{ ... }}` to ensure
they remain data rather than becoming executable expressions.

## Native values and strict boolean conditionals

Templates in `2.19-2.20` always use Jinja native mode. A non-string result is
not automatically stringified, and `None` is not generally replaced by an
empty string. `set_fact` also preserves `yes`, `no`, `true`, and `false` as
strings when those values were supplied as strings.

The following settings no longer alter that behavior:

- `DEFAULT_JINJA2_NATIVE`
- `DEFAULT_NULL_REPRESENTATION`
- `DEFAULT_UNDEFINED_VAR_BEHAVIOR`
- `STRING_TYPE_FILTERS`

Conditionals must return a boolean. A non-boolean result fails by default.
`ALLOW_BROKEN_CONDITIONALS` can temporarily downgrade the failure to a
deprecation warning for staged migration; in that compatibility mode, literal
`None` and empty strings evaluate true. Make conversions and comparisons
explicit rather than depending on those exceptional truthiness rules.

Ansible values stored by the engine may be subclasses of Python builtins.
Before handing them to third-party libraries that reject subclasses, convert
them to the corresponding plain Python type.

## Lazy templating and `omit`

Structures are templated lazily in `2.19-2.20`: only the portions that code
accesses are evaluated. A bad expression may therefore fail when a member is
read, rather than when its enclosing mapping or list is constructed.

`omit` is removed from its parent container during templating. In a loop, put
`default(omit)` on the exact value that should disappear from the task's module
arguments.

```yaml
- ansible.builtin.user:
    name: "{{ item.name }}"
    shell: "{{ item.shell | default(omit) }}"
  loop: "{{ users }}"
```

A caller of `Templar.template()` must catch `AnsibleValueOmittedError` when the
entire templated result is omitted.

## Undefined values and markers

Custom Jinja plugins in `2.19-2.20` must explicitly opt in if they accept an
undefined top-level argument. A plugin that calls `environment.getitem` must
catch `MarkerError` and return a marker, or explicitly opt in to receiving
marker values. Do not turn a marker into an ordinary successful value by
accident.

## Sandbox behavior

The standard Jinja sandbox replaces the immutable sandbox in `2.19-2.20`.
Useful methods such as `list.append` and `dict.update` are available again,
while attributes beginning with `_` and known side-effect methods remain
blocked.

A `range()` object cannot be a final template result; consume it through a
filter. Final `set` and `tuple` results are converted to lists.

In Jinja `set` or `with` blocks, containers passed to methods are copied. A
mutation is discarded unless the method returns the changed value. Unobserved
exceptions from those blocks are ignored in the same way as undefined values.

## JSON conversion profiles

In `2.19-2.20`, `from_json`, `to_json`, and `to_nice_json` accept a `profile`
argument. It defaults to `tagless`.

The template lookup's `convert_data` option no longer performs conversion.
Apply `from_json` explicitly when lookup output must become structured data.
