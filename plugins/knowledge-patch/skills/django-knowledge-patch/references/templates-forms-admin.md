# Templates, Forms, and Admin

Batch attribution: `5.1`, `5.2-guide`, `5.2`, `6.0-guide`, `6.0`.

## Contents

- [Template partials](#template-partials)
- [Simple block tags and extension hooks](#simple-block-tags-and-extension-hooks)
- [Template loop and query-string helpers](#template-loop-and-query-string-helpers)
- [HTML formatting](#html-formatting)
- [BoundField customization](#boundfield-customization)
- [Accessible form errors and script assets](#accessible-form-errors-and-script-assets)
- [Admin templates, links, documentation, and passwords](#admin-templates-links-documentation-and-passwords)

## Template partials

Define a named fragment with `partialdef` (since `6.0-guide`):

```django
{% partialdef filter_controls %}
  <form>{{ filter_form }}</form>
{% endpartialdef %}
```

Render it elsewhere in the same template with `partial`:

```django
{% partial filter_controls %}
```

Add `inline` to render the fragment at its definition site as well:

```django
{% partialdef filter_controls inline %}
  <form>{{ filter_form }}</form>
{% endpartialdef %}
```

A view can render only a named fragment by appending `#<partial-name>` to the template name:

```python
return render(request, "video.html#view_count", context)
```

Keep fragment context requirements explicit. A fragment-only response still renders in the
context supplied by the view, but omits the rest of the template response.

## Simple block tags and extension hooks

### Paired block tags

`Library.simple_block_tag()` builds a paired template tag without a custom parser or node (since
`5.2-guide`). The rendered body is passed as the decorated function's first `content` argument:

```python
@register.simple_block_tag
def button(content, colour="primary"):
    return format_html(
        '<button class="{}">{}</button>',
        colour,
        content,
    )
```

```django
{% button colour="secondary" %}Cancel{% endbutton %}
```

### Parser and engine hooks

A custom tag can attach additional data to its `Parser` for access on the resulting `Template`
(since `5.1`). Use this for coordinated template-level metadata rather than global state.

Template engine implementations have a `check()` method registered with Django's system-check
framework (since `5.1`). Put static configuration validation there so `manage.py check` reports it.

## Template loop and query-string helpers

Inside a template `for` loop, `forloop.length` exposes the total number of items (since
`6.0-guide`):

```django
{{ forloop.counter }}/{{ forloop.length }}
```

The `querystring` tag always prefixes its result with `?`, including the empty result used to clear
an existing query string (since `6.0-guide`). It accepts multiple positional mappings and merges
them from left to right; a later mapping wins when keys collide:

```django
{% querystring request.GET extra_params %}
```

Do not add a second `?` around the tag output.

## HTML formatting

`format_html_join()` accepts an iterable of mappings and passes every mapping as keyword arguments
to `format_html()` (since `5.2-guide`):

```python
format_html_join(
    "\n",
    "<h2>{name}</h2>",
    ({"name": nebula.name} for nebula in nebulae),
)
```

This allows named placeholders rather than tuple-position coupling. `format_html()` itself must
receive at least one argument or keyword argument in Django 6.0.

## BoundField customization

Select a `BoundField` subclass at three levels (since `5.2-guide`):

1. Set `BaseRenderer.bound_field_class` for project-wide rendering.
2. Set `Form.bound_field_class` for a form class.
3. Pass or set `Field.bound_field_class` for one field.

```python
class SearchForm(forms.Form):
    query = forms.CharField(bound_field_class=CustomBoundField)
```

Use the narrowest level needed. This avoids creating a custom field class solely to override
`get_bound_field()`.

## Accessible form errors and script assets

Rendered forms associate fields and errors with `aria-describedby` (since `5.2`).
`BoundField.aria_describedby` exposes the computed relationship, and `ErrorList(field_id=...)`
lets custom rendering preserve the target field ID. Carry these attributes through custom widget,
field, and error-list templates.

The `Script` form-media asset represents JavaScript with arbitrary HTML attributes (since `5.2`).
Use it when a script requires attributes such as `type`, `defer`, `async`, integrity metadata, or a
nonce instead of emitting a raw script tag in a widget template.

## Admin templates, links, documentation, and passwords

- `admin/base.html` has an `extrabody` block immediately before `</body>` (since `5.2`). Put
  end-of-body admin customizations there.
- Admin `URLField` values render as clickable links (since `5.2`). Recheck custom display methods
  that previously added their own anchors.
- Admindocs supports the docstring role syntax ``:role:`link text <link>` `` (since `5.2`).
- Admindocs model pages require the corresponding model view or change permission (since `5.2`).
  Do not assume documentation is visible merely because the user can enter the admin site.
- `AdminSite.password_change_form` selects the form used by the admin password-change view (since
  `6.0`).
- `AdminUserCreationForm` and `AdminPasswordChangeForm` can save an unusable password, allowing an
  administrator to disable password-based authentication (since `5.1`).
- The admin's `delete_selected` action writes multiple `LogEntry` rows through `bulk_create()`
  (since `5.1`), so those entries do not trigger `pre_save` or `post_save` signals.
