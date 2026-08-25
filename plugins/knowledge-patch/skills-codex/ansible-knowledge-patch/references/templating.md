# Templating, Values, and Conditionals

## Trusted, single-pass templating

Since `2.19-2.20`, Ansible evaluates Jinja in strings only when the value's
source is trusted. Playbooks, variable files, and many inventory sources are
trusted; facts and module-result strings are not. Literal Jinja delimiters in
an untrusted string are left unevaluated and produce a warning.

Plugins that create a value intended to be templated must apply trust, and
plugins that transform a trusted template must preserve that trust. Do not use
module output or facts as a way to inject executable template expressions.

Templating is single-pass. A template must not generate a new template for a
later evaluation pass. Embedded templates outside Jinja string constants are
errors; embedded templates inside such constants warn. Remove Jinja delimiters
from ordinary conditionals unless the complete value is a single trusted string
expression.

```yaml
# Direct expression; produces a boolean.
when: service_enabled | bool

# Do not use delimiters for an ordinary conditional.
when: "{{ service_enabled | bool }}"
```

## Native result values

Templates always use native Jinja values. A non-string result is not
automatically stringified, and `None` is not generally converted to an empty
string. `set_fact` also preserves `yes`, `no`, `true`, and `false` when they
arrive as literal strings.

The following settings no longer change these semantics:

- `DEFAULT_JINJA2_NATIVE`
- `DEFAULT_NULL_REPRESENTATION`
- `DEFAULT_UNDEFINED_VAR_BEHAVIOR`
- `STRING_TYPE_FILTERS`

Stored values may be Ansible subclasses of Python builtins. Before handing a
value to a third-party API that performs strict type checks, convert it to the
corresponding plain Python type.

## Boolean-only conditionals

Conditionals that yield non-booleans fail by default. Add an explicit
comparison or use an appropriate conversion such as `| bool`.

`ALLOW_BROKEN_CONDITIONALS` is a temporary migration control: it downgrades the
failure to a deprecation warning. Do not rely on its compatibility truthiness;
in that mode, literal `None` and empty strings evaluate as true.

## Lazy templating and omitted values

Only accessed portions of a structure are templated. Construction can succeed
even when an untouched member would fail, so test the actual access paths.

During templating, `omit` is removed from its parent container. In a loop,
apply `default(omit)` to the module argument that should disappear:

```yaml
- ansible.builtin.user:
    name: "{{ item.name }}"
    shell: "{{ item.shell | default(omit) }}"
  loop: "{{ users }}"
```

Code calling `Templar.template()` must catch `AnsibleValueOmittedError` when
the entire templated result is omitted.

## Undefined values and markers

Custom Jinja plugins do not accept an undefined top-level argument unless they
explicitly opt in. A plugin that calls `environment.getitem` must handle
`MarkerError` and return a marker, or explicitly opt in to receiving marker
values. See [plugins-and-extensions.md](plugins-and-extensions.md) for the
plugin migration context.

## Sandbox behavior

The standard Jinja sandbox replaces the immutable sandbox. Mutations such as
`list.append` and `dict.update` are available again, while attributes beginning
with `_` and known side-effect methods remain blocked.

A template cannot return a `range()` object; consume it with a filter. Final
`set` and `tuple` values are converted to lists.

In 2.20, a container created in a Jinja `set` or `with` block is copied when it
is passed to a method. A mutation that is not returned by the method is
therefore discarded. Unobserved exceptions in those blocks are ignored in the
same way as undefined values.

## JSON conversion profiles

`from_json`, `to_json`, and `to_nice_json` accept a `profile` argument. Its
default is `tagless`.

The template lookup's `convert_data` option no longer performs conversion.
Apply `from_json` explicitly when the rendered template contains JSON that must
be parsed:

```yaml
parsed: "{{ lookup('ansible.builtin.template', 'data.json.j2') | from_json }}"
```
