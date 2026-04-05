# Views & HTTP

## `reverse()` with `query` and `fragment`

*Since 5.2 (April 2025)*

```python
from django.urls import reverse

reverse("search", query={"q": "django", "page": "2"})
# "/search/?q=django&page=2"

reverse("docs", fragment="section-3")
# "/docs/#section-3"
```

## `HttpRequest.get_preferred_type()` and `HttpResponse.text`

*Since 5.2 (April 2025)*

```python
# Content negotiation
def my_view(request):
    preferred = request.get_preferred_type(["text/html", "application/json"])
    if preferred == "application/json":
        return JsonResponse(data)
    return render(request, "page.html", context)

# String access to response content (cached, uses response charset)
response = self.client.get("/")
response.text  # str, instead of response.content.decode()
```

## `preserve_request` on Redirects

*Since 5.2 (April 2025)*

New `preserve_request` argument on `redirect()`, `HttpResponseRedirect`, and `HttpResponsePermanentRedirect`. When `True`, uses 307/308 status codes (browser reuses HTTP method and body).

```python
from django.shortcuts import redirect

redirect("/new-endpoint/", preserve_request=True)  # 307 instead of 302
redirect("/new-endpoint/", permanent=True, preserve_request=True)  # 308 instead of 301
```

## New Form Widgets

*Since 5.2 (April 2025)*

`ColorInput` (`<input type="color">`), `SearchInput` (`<input type="search">`), `TelInput` (`<input type="tel">`).

## `AsyncPaginator` and `AsyncPage`

*Since 6.0 (December 2025)*

New async implementations of `Paginator` and `Page` for use in async views.

```python
from django.core.paginator import AsyncPaginator

paginator = AsyncPaginator(queryset, per_page=25)
page = await paginator.aget_page(page_number)
```

## Oracle Connection Pools

*Since 5.2 (April 2025)*

Oracle now supports connection pools via `OPTIONS["pool"]` in `DATABASES`.
