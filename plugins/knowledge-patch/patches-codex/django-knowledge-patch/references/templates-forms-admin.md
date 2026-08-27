# Templates, Forms, and Admin

## Define template partials

The 6.0-guide adds named fragments with `partialdef` and renders them with `partial`. Add `inline`
when the definition should also render in place.

```django
{% partialdef filter_controls inline %}
  <form>{{ filter_form }}</form>
{% endpartialdef %}

{% partial filter_controls %}
```

A view can render only a named fragment by appending `#<partial-name>` to the template name:

```python
return render(request, "video.html#view_count", context)
```

Keep fragment names local and explicit, and test both full-template and fragment-only rendering.

## Build simple paired tags

`Library.simple_block_tag()` creates a paired tag without a custom parser or node. The decorated
function receives the rendered block as its first `content` argument (5.2-guide).

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

## Attach parser metadata and run engine checks

Custom tags can attach extra data to a `Parser` for later access on the resulting `Template`
(since 5.1). Template engines also implement `check()` and register it with Django's system-check
framework. Keep parser-attached data namespaced to the extension and exercise engine checks in
CI.

## Use current template helpers

`format_html_join()` accepts an iterable of mappings and passes each mapping as keyword arguments
to `format_html()` (5.2-guide):

```python
format_html_join(
    "\n",
    "<h2>{name}</h2>",
    ({"name": nebula.name} for nebula in nebulae),
)
```

Calling `format_html()` with neither positional nor keyword interpolation arguments is removed in
6.0. `SafeString.__add__()` returns `NotImplemented` when its right operand is not a string (since
5.2), allowing normal Python fallback behavior instead of assuming a safe result.

Within a template loop, `forloop.length` exposes the total number of items (6.0-guide):

```django
{{ forloop.counter }}/{{ forloop.length }}
```

## Merge query-string mappings

The `querystring` tag always prefixes its output with `?`, including the empty output used to
clear an existing query string. It accepts multiple positional mappings and merges them
left-to-right, with later mappings winning duplicate keys (6.0-guide).

```django
{% querystring request.GET extra_params %}
```

Do not add another literal `?` around its output.

## Select a custom BoundField class

Choose a `BoundField` subclass at the broadest appropriate level through
`BaseRenderer.bound_field_class`, `Form.bound_field_class`, or `Field.bound_field_class`
(5.2-guide). This avoids creating a custom field class solely to override `get_bound_field()`.

```python
class SearchForm(forms.Form):
    query = forms.CharField(bound_field_class=CustomBoundField)
```

## Preserve accessible error relationships

Rendered forms associate fields and errors using `aria-describedby` (since 5.2).
`BoundField.aria_describedby` exposes the generated relationship, and `ErrorList(field_id=...)`
supports the matching error container. Preserve these IDs and attributes in custom form and
widget templates.

The `Script` form-media asset object allows custom HTML attributes on JavaScript assets. Prefer it
to manually assembling script tags when a widget needs attributes such as `type`, `defer`, or
integrity metadata.

## Customize the admin safely

The admin's `base.html` includes an `extrabody` block immediately before `</body>` (since 5.2).
Use it for page-end markup rather than replacing the whole base template. Admin `URLField` values
render as links, but as of 5.2.17 only values passing `URLValidator` become links; invalid values
remain plain text.

Admindocs understands ``:role:`link text <link>` `` syntax in docstrings (since 5.2). Model pages
are restricted to users with the corresponding view or change permission.

`AdminSite.password_change_form` selects a custom password-change form (since 6.0). Overrides of
`ModelAdmin.lookup_allowed()` must accept `request`, and admin logging extensions should use the
plural `log_deletions()` and `log_actions()` APIs.

## Account for bulk admin logging

The `delete_selected` action writes multiple `LogEntry` objects using `bulk_create()` (since 5.1).
Those log entries do not emit `pre_save` or `post_save`. Do not depend on per-row save signals for
admin bulk-deletion audit processing.

## Block data-changing calls in templates

User-manager creation methods and synchronous and async queryset creation, bulk-creation,
get-or-create, and update-or-create methods set `alters_data=True` (since 5.2). Template rendering
therefore refuses to invoke them. Custom wrappers around data-changing methods should preserve the
same marker.

## Remove old rendering compatibility

`DjangoDivFormRenderer` and `Jinja2DivFormRenderer` are removed in 6.0, as is `ChoicesMeta`.
Update renderer settings and metaclass imports instead of keeping a version shim around those
names.
