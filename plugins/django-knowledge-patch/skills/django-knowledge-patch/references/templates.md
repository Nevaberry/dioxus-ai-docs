# Templates

## Template Partials

*Since 6.0 (December 2025)*

Define and reuse named fragments within a template. Partials can be rendered in isolation using `template_name#partial_name` syntax — ideal for htmx partial re-rendering.

```html
<!-- video.html -->
{% partialdef view_count inline %}
  <span id="view-count">{{ video.views }}</span>
{% endpartialdef %}

<h1>{{ video.title }}</h1>
{% partial view_count %}
```

`inline` on `partialdef` renders the definition in place. Without it, the definition is silent (only renders when explicitly called).

Render a partial in isolation from views:

```python
# Full template
render(request, "video.html", context)

# Just the partial (e.g., for htmx)
render(request, "video.html#view_count", context)
```

Works with `{% include %}`, `get_template()`, and any template-loading API.

## `simple_block_tag()` Decorator

*Since 5.2 (April 2025)*

New decorator for custom template tags that wrap a block of content.

```python
@register.simple_block_tag
def my_card(nodelist, title):
    return f'<div class="card"><h2>{title}</h2>{nodelist}</div>'
```

```html
{% my_card title="Hello" %}
  <p>Card content here</p>
{% endmy_card %}
```

## `forloop.length`

*Since 6.0 (December 2025)*

New `forloop.length` variable inside `{% for %}` loops gives total item count.

```html
{% for item in items %}
  {{ forloop.counter }} of {{ forloop.length }}: {{ item }}
{% endfor %}
```

## `{% querystring %}` Changes

*Since 6.0 (December 2025)*

`{% querystring %}` now always prefixes output with `?` and accepts multiple positional mapping args.
