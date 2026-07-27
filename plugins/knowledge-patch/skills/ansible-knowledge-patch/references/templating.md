# Templating, Values, and Conditionals

The templating transitions in this reference are attributed to batch
`2.19-2.20`.

## Trusted, Single-Pass Evaluation

Ansible evaluates Jinja in a string only when the string's source is trusted.
Playbooks, variable files, and many inventory sources are trusted. Module
results and facts are untrusted, so Jinja markers found in those strings are
not evaluated and cause a warning.

Plugins that create a string intended for later templating must apply trust.
Plugins that transform a trusted template string must preserve that trust.
Never infer trust merely from the presence of Jinja delimiters.

Security-motivated multi-pass templating is gone. A rendered value is not
reinterpreted as another template:

- An embedded template outside a Jinja string constant is an error.
- An embedded template inside a Jinja string constant produces a warning.
- A conditional should omit Jinja delimiters unless its entire value is one
  trusted string expression.

```yaml
vars:
  expected_port: 443

tasks:
  - ansible.builtin.debug:
      msg: TLS is configured
    when: service.port == expected_port
```

## Native Values

Templates always operate in Jinja native mode. Non-string results are not
automatically stringified, and `None` is not generally converted to an empty
string. The following settings no longer change that behavior:

- `DEFAULT_JINJA2_NATIVE`
- `DEFAULT_NULL_REPRESENTATION`
- `DEFAULT_UNDEFINED_VAR_BEHAVIOR`
- `STRING_TYPE_FILTERS`

`set_fact` leaves `yes`, `no`, `true`, and `false` as strings when the input
values are strings. Convert at the point where a boolean or another native
type is required.

Stored values may be subclasses of Python builtins. Plugin code should convert
them to plain native values before calling libraries that reject subclasses.

## Strict Boolean Conditionals

A conditional returning a non-boolean value fails by default.
`ALLOW_BROKEN_CONDITIONALS` temporarily changes the failure to a deprecation
warning for migration. In that compatibility mode, literal `None` and empty
strings evaluate as true, so the mode must not be treated as ordinary Python
truthiness.

Prefer an explicit predicate:

```yaml
when: response.status == 200
```

```yaml
when: feature_flag | bool
```

## Lazy Templating

Only accessed portions of a structure are templated. Building or passing a
large mapping therefore does not guarantee every nested expression has already
been evaluated. Tests should access the same branches that production tasks
consume, and exception handling should surround the access point.

## `omit`

`omit` is removed from its parent container during templating. A loop value
that should disappear from task arguments must apply `default(omit)` where the
argument is formed:

```yaml
- ansible.builtin.file:
    path: "{{ item.path }}"
    owner: "{{ item.owner | default(omit) }}"
  loop: "{{ managed_paths }}"
```

Callers of `Templar.template()` must catch `AnsibleValueOmittedError` when the
entire templated result is omitted.

## Sandbox Behavior and Final Values

The standard Jinja sandbox replaces the immutable sandbox. This restores
ordinary methods such as `list.append` and `dict.update`. Attributes beginning
with `_` and known side-effect methods remain blocked.

A `range()` object cannot be the final value returned by a template; consume
it through a filter. Final `set` and `tuple` values are converted to lists.

In the later behavior covered by batch `2.19-2.20`, containers created inside
Jinja `set` or `with` blocks are copied when passed to a method. A mutation
that is not returned by that method is discarded. Unobserved exceptions in
those blocks are ignored in the same way as undefined values.

## JSON and Template Lookup Conversion

`from_json`, `to_json`, and `to_nice_json` accept a `profile` argument. The
default profile is `tagless`.

The template lookup's `convert_data` option no longer performs conversion.
Apply `from_json` explicitly when the rendered template contains JSON:

```yaml
vars:
  parsed: "{{ lookup('ansible.builtin.template', 'data.json.j2') | from_json }}"
```
