# Web, Assets, and Storage

## Browser version guards

Rails 7.2 (`7.2`) provides `allow_browser`. It blocks matched browser families below the requested versions while allowing unknown browsers and clients without a user-agent. A blocked request receives `public/406-unsupported-browser.html` with status 406.

New applications place the guard in `ApplicationController`. Scope it with `only:` or `except:` when needed:

```ruby
allow_browser versions: :modern
allow_browser versions: { safari: 16.4, firefox: 121, ie: false }
allow_browser versions: { chrome: 119 }, only: :show
```

## Query parsing and redirects

Rails 8.1 (`8.1`) preserves a leading `[` in a root query key and no longer treats semicolons as pair separators. Remove reliance on `config.action_dispatch.ignore_leading_brackets`.

```ruby
ActionDispatch::ParamBuilder.from_query_string("[foo]=bar")
# => { "[foo]" => "bar" }

ActionDispatch::QueryParser.each_pair("foo=bar;baz=quux").to_a
# => [["foo", "bar;baz=quux"]]
```

New applications enable verbose redirect logs in development. Existing applications can set `config.action_dispatch.verbose_redirect_logs = true`.

## Markdown responses

Controllers can negotiate `.md` and render an object through its `to_markdown` method with `render markdown:` (`8.1-guide`):

```ruby
respond_to do |format|
  format.html
  format.md { render markdown: @page }
end
```

## Propshaft load paths and digests

Propshaft copies every asset under `config.assets.paths` into `public/assets` during precompilation (`8.0-guide`), not only assets referenced by bundles. Exclude compiler-only input directories by full path:

```ruby
config.assets.excluded_paths << Rails.root.join("app/assets/stylesheets")
```

Name a file that must retain its existing digest with the `-[digest].digested.<extension>` suffix.

## Propshaft Subresource Integrity

Configure SHA-256, SHA-384, or SHA-512 and opt individual helpers into SRI with `integrity: true`:

```ruby
config.assets.integrity_hash_algorithm = "sha384"
```

```erb
<%= stylesheet_link_tag "application", integrity: true %>
<%= javascript_include_tag "application", integrity: true %>
```

Production helpers omit integrity hashes over plain HTTP. `stylesheet_link_tag :all` selects every stylesheet; `:app` selects only stylesheets under `app/assets`.

## Declarative Turbo morph refreshes

Turbo recognizes rendering the current page again as a page refresh (`hotwire-morphing`). By default it replaces the body and resets scrolling. Page directives can morph only changed DOM and preserve both horizontal and vertical scroll:

```html
<meta name="turbo-refresh-method" content="morph">
<meta name="turbo-refresh-scroll" content="preserve">
```

## Morph-refreshable frames

A `src`-backed frame with `refresh="morph"` reloads on page refresh. It retains its current content until the response arrives, then morphs in the result. This keeps independently loaded regions such as pagination through a page morph.

```html
<turbo-frame id="results" src="/results?page=2" refresh="morph">
</turbo-frame>
```

## Refresh streams and model broadcasts

The `refresh` stream action reloads the page and may override the page's refresh method and scroll behavior. Consecutive broadcast refreshes are automatically debounced.

```html
<turbo-stream action="refresh" method="morph" scroll="preserve"></turbo-stream>
```

In Rails, pair `broadcasts_refreshes` with a normal stream subscription instead of broadcasting a DOM operation for every change:

```ruby
class Calendar < ApplicationRecord
  broadcasts_refreshes
end
```

```erb
<%= turbo_stream_from @calendar %>
```

## Isolated execution state for live streams

`ActionController::Live` shares execution state with its worker thread by default (`8.1`). Exclude selected keys when streaming work must establish independent state, such as its own Active Record connection context:

```ruby
config.action_controller.live_streaming_excluded_keys = [
  :active_record_connected_to_stack
]
```

## Active Storage range and disk-key hardening

Active Storage accepts one byte range per request and limits a requested range to 100 MB by default (`8.1`). `DiskService#path_for` consistently raises `InvalidKeyError` for dot segments, invalid keys, and paths outside the service root. `delete_prefixed` treats glob metacharacters literally rather than expanding them.

## GCS IAM authorization

GCS URL signing through IAM again uses application default credentials (`8.1`). Set authorization on Active Storage's memoized IAM client when impersonation is required without altering other Google API clients:

```ruby
ActiveStorage::Blob.service.iam_client.authorization =
  Google::Auth::ImpersonatedServiceAccountCredentials.new(options)
```

## Active Storage libvips security hardening

The security batch `7.2.3.2-8.1.3.1-security` applies to Rails 7.2.3.2, 8.0.5.1, and 8.1.3.1. These releases call `Vips.block_untrusted(true)` at boot, disabling loaders and savers that libvips marks unfuzzed or untrusted.

When ruby-vips is installed, Active Storage requires libvips 8.13 or newer and ruby-vips 2.2.1 or newer. Older versions raise `RuntimeError` during boot.

The block changes image handling as follows:

- Variant transformation of BMP, ICO, and PSD inputs raises `Vips::Error`.
- Output to unfuzzed formats such as FITS or JXL, or to any format delegated to ImageMagick, raises `Vips::Error`.
- Analysis of those inputs, plus SVG, JPEG XL, JPEG 2000, and Netpbm, no longer records dimensions.
- Attaching, storing, and downloading remain unchanged.

If affected attachments should never be transformed, remove their MIME types from the variable-content list:

```ruby
Rails.application.config.active_storage.variable_content_types -= %w[
  image/bmp image/vnd.microsoft.icon image/vnd.adobe.photoshop
]
```

MiniMagick attachment processing itself is unchanged. However, the restrictions and version checks apply process-wide whenever ruby-vips is installed. A MiniMagick-only application can remove ruby-vips to avoid both.
