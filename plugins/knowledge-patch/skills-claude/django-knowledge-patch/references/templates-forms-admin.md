# Templates, Forms, and Admin

Load this reference for template extensions and fragments, form rendering,
accessible errors, form assets, and admin customizations.

## Extend template parsing and checks

Custom template tags can attach data to a `Parser` and later retrieve it from the
resulting `Template`. Template engines implement `check()` and register it with
Django's system-check framework. (`5.1`)

Use `Library.simple_block_tag()` for paired tags when the implementation only
needs the rendered body. The decorated function receives the block as its first
`content` argument. (`5.2-guide`)

```python
@register.simple_block_tag
def button(content, colour="primary"):
    return format_html('<button class="{}">{}</button>', colour, content)
```

```django
{% button colour="secondary" %}Cancel{% endbutton %}
```

`format_html_join()` accepts an iterable of mappings and passes each mapping to
`format_html()` as keyword arguments, enabling named placeholders.
(`5.2-guide`)

```python
format_html_join(
    "\n",
    "<h2>{name}</h2>",
    ({"name": nebula.name} for nebula in nebulae),
)
```

## Render template partials (`6.0-guide`)

`partialdef` names a fragment, `partial` renders it, and `inline` renders the
definition at its declaration site as well.

```django
{% partialdef filter_controls inline %}
  <form>{{ filter_form }}</form>
{% endpartialdef %}

{% partial filter_controls %}
```

Append `#<partial-name>` to the template name to render only the fragment:

```python
return render(request, "video.html#view_count", context)
```

Within a template `for` loop, `forloop.length` exposes the total iteration
count. (`6.0-guide`)

The `querystring` tag always prefixes output with `?`, including the empty result
used to clear a query string. It accepts multiple positional mappings and merges
them left-to-right; later mappings win. (`6.0-guide`)

```django
{% querystring request.GET extra_params %}
```

## Select custom bound fields (`5.2-guide`)

Choose a `BoundField` subclass at the project/rendering, form, or field level
with `BaseRenderer.bound_field_class`, `Form.bound_field_class`, or
`Field.bound_field_class`. A custom field class is no longer necessary solely to
override `get_bound_field()`.

```python
class SearchForm(forms.Form):
    query = forms.CharField(bound_field_class=CustomBoundField)
```

## Preserve accessible form relationships (`5.2`)

Rendered forms use `aria-describedby` to associate fields with their errors.
`BoundField.aria_describedby` exposes the relationship, and
`ErrorList(field_id=...)` emits a matching ID.

Use the `Script` form-media asset object when JavaScript includes need custom HTML
attributes.

## Customize the admin

- `admin/base.html` provides an `extrabody` block immediately before
  `</body>`. (`5.2`)
- Admin `URLField` values render as links. (`5.2`)
- Admindocs accepts `:role:\`link text <link>\`` in docstrings and limits model
  pages to users with the corresponding view or change permission. (`5.2`)
- `AdminSite.password_change_form` selects the password-change form used by the
  admin site. (`6.0`)
- Admin changelists and read-only fields validate `URLField` values with
  `URLValidator` before linking them; invalid values render as plain text.
  (`5.2.17`)

When admin `delete_selected` creates multiple `LogEntry` rows, it uses
`bulk_create()`. Those entries do not emit `pre_save` or `post_save`.
(`5.1`)

## Update removed customization points

`ModelAdmin.lookup_allowed()` overrides must accept `request`, and
`format_html()` must receive arguments or keyword arguments.
`DjangoDivFormRenderer`, `Jinja2DivFormRenderer`, and `ChoicesMeta` are
removed. (`6.0`)
