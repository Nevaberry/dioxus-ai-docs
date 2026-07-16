# Web, Assets, and Storage

Topic details draw from batches `7.2`, `8.0-guide`, `8.0`, `8.1-guide`, `8.1`, and `hotwire-morphing`.

## Contents

- [Browser guards and request parsing](#browser-guards-and-request-parsing)
- [Rendering and live streaming](#rendering-and-live-streaming)
- [Propshaft assets and integrity](#propshaft-assets-and-integrity)
- [Turbo morphing refreshes](#turbo-morphing-refreshes)
- [Active Storage hardening and GCS](#active-storage-hardening-and-gcs)

## Browser guards and request parsing

### Browser version guards

`allow_browser` blocks recognized browsers that match the configured names but fall below the requested versions (`7.2`). Unknown browsers and clients without a user-agent remain allowed. A blocked client receives `public/406-unsupported-browser.html` with status 406.

New applications place the guard in `ApplicationController`. Scope it with normal `only:` or `except:` action options:

```ruby
allow_browser versions: :modern
allow_browser versions: { safari: 16.4, firefox: 121, ie: false }
allow_browser versions: { chrome: 119 }, only: :show
```

### Query parsing and redirects

Action Pack no longer strips a leading bracket from a root parameter name and no longer uses semicolons as query-pair separators (`8.1`):

```ruby
ActionDispatch::ParamBuilder.from_query_string("[foo]=bar")
# => { "[foo]" => "bar" }

ActionDispatch::QueryParser.each_pair("foo=bar;baz=quux").to_a
# => [["foo", "bar;baz=quux"]]
```

`config.action_dispatch.ignore_leading_brackets` is deprecated. New applications enable verbose redirect logging in development; existing applications can opt in:

```ruby
config.action_dispatch.verbose_redirect_logs = true
```

### View compatibility

Do not pass content to void-element builders such as `tag.br`; that form is deprecated (`7.2`). `form_with(model: nil)` is removed and multiple-path route declarations are deprecated (`8.0`).

## Rendering and live streaming

### Markdown responses

Controllers negotiate `.md` requests and render an object through `to_markdown` with `render markdown:` (`8.1-guide`):

```ruby
respond_to do |format|
  format.html
  format.md { render markdown: @page }
end
```

Ensure the rendered object implements `to_markdown`.

### Isolated execution state for live responses

`ActionController::Live` shares execution state with its worker thread by default (`8.1`). Exclude selected keys when streaming code needs independent state, such as a separate Active Record connection context:

```ruby
config.action_controller.live_streaming_excluded_keys = [
  :active_record_connected_to_stack
]
```

## Propshaft assets and integrity

### Load paths and digest preservation

Propshaft copies every asset under `config.assets.paths` to `public/assets` during precompilation (`8.0-guide`), not only files referenced by bundles. Exclude compiler-only input directories with their full paths:

```ruby
config.assets.excluded_paths <<
  Rails.root.join("app/assets/stylesheets")
```

Name a file that must retain an existing digest with the `-[digest].digested.<extension>` suffix.

### Subresource Integrity

Choose SHA-256, SHA-384, or SHA-512, then opt each helper into integrity output:

```ruby
config.assets.integrity_hash_algorithm = "sha384"
```

```erb
<%= stylesheet_link_tag "application", integrity: true %>
<%= javascript_include_tag "application", integrity: true %>
```

In production, helpers omit SRI hashes when the asset is served over plain HTTP (`8.0-guide`). `stylesheet_link_tag :all` selects every stylesheet; `stylesheet_link_tag :app` selects only stylesheets under `app/assets`.

## Turbo morphing refreshes

### Page refresh behavior

Turbo treats rendering the current page again as a page refresh (`hotwire-morphing`). By default it replaces the body and resets scrolling. Use page directives to morph only changed DOM and preserve both horizontal and vertical scroll:

```html
<meta name="turbo-refresh-method" content="morph">
<meta name="turbo-refresh-scroll" content="preserve">
```

### Refreshable frames

A `src`-backed frame with `refresh="morph"` reloads during a page refresh. It retains its current content until the response arrives, then morphs the result in place. This preserves independently loaded state such as pagination:

```html
<turbo-frame
  id="results"
  src="/results?page=2"
  refresh="morph">
</turbo-frame>
```

### Refresh streams and broadcasts

The `refresh` stream action reloads the page and can override the page-level method and scroll behavior:

```html
<turbo-stream
  action="refresh"
  method="morph"
  scroll="preserve">
</turbo-stream>
```

Consecutive broadcast refreshes are automatically debounced (`hotwire-morphing`). In Rails, replace per-change DOM-operation broadcasts with `broadcasts_refreshes` and keep a normal stream subscription:

```ruby
class Calendar < ApplicationRecord
  broadcasts_refreshes
end
```

```erb
<%= turbo_stream_from @calendar %>
```

## Active Storage hardening and GCS

### Range and disk-key handling

Active Storage accepts only one blob byte range per request and limits the range to 100 MB by default (`8.1`).

`DiskService#path_for` consistently raises `InvalidKeyError` for dot segments, otherwise invalid keys, or paths outside the configured root. `delete_prefixed` treats glob metacharacters literally rather than expanding them.

The Azure storage backend is deprecated (`8.0`); plan a service migration.

### GCS IAM signing

GCS URL signing through IAM again uses application default credentials (`8.1`). Set authorization on the service's memoized IAM client when impersonation or a distinct signing identity is required, without changing other Google API clients:

```ruby
ActiveStorage::Blob.service.iam_client.authorization =
  Google::Auth::ImpersonatedServiceAccountCredentials.new(options)
```
