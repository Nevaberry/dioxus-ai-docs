# Web, Assets, and Storage

## Request and response behavior

### Query parsing and redirect diagnostics

In `8.1`, query parsing keeps a leading `[` in a root parameter name and no
longer treats semicolons as pair separators.
`config.action_dispatch.ignore_leading_brackets` is deprecated.

```ruby
ActionDispatch::ParamBuilder.from_query_string("[foo]=bar")
# => { "[foo]" => "bar" }

ActionDispatch::QueryParser.each_pair("foo=bar;baz=quux").to_a
# => [["foo", "bar;baz=quux"]]
```

New applications enable verbose development redirect logs. Existing
applications can opt in:

```ruby
config.action_dispatch.verbose_redirect_logs = true
```

### Markdown responses

The `8.1-guide` adds `.md` negotiation and `render markdown:`. The rendered
object supplies `to_markdown`.

```ruby
respond_to do |format|
  format.html
  format.md { render markdown: @page }
end
```

### Live streaming execution state

`ActionController::Live` shares isolated execution state with its worker thread
by default. Exclude selected keys when streaming code needs independent state,
such as its own Active Record connection context:

```ruby
config.action_controller.live_streaming_excluded_keys = [
  :active_record_connected_to_stack
]
```

## Propshaft

### Load paths and digest preservation

The `8.0-guide` notes that Propshaft copies every file under
`config.assets.paths` to `public/assets` during precompilation, not only assets
referenced by bundles. Exclude compiler-only source directories by full path:

```ruby
config.assets.excluded_paths << Rails.root.join("app/assets/stylesheets")
```

Name a file that must retain an existing digest with the
`-[digest].digested.<extension>` suffix.

### Subresource Integrity

Select SHA-256, SHA-384, or SHA-512, then opt each helper into SRI with
`integrity: true`:

```ruby
config.assets.integrity_hash_algorithm = "sha384"
```

```erb
<%= stylesheet_link_tag "application", integrity: true %>
<%= javascript_include_tag "application", integrity: true %>
```

In production, helpers omit integrity hashes over plain HTTP.
`stylesheet_link_tag :all` selects every stylesheet; `:app` selects only those
under `app/assets`.

## Turbo refreshes

The `hotwire-morphing` guidance treats rendering the current page again as a
page refresh. By default Turbo replaces the body and resets scrolling. Page
directives can morph only changed DOM and preserve horizontal and vertical
scroll:

```html
<meta name="turbo-refresh-method" content="morph">
<meta name="turbo-refresh-scroll" content="preserve">
```

### Refreshable frames

A `src`-backed frame with `refresh="morph"` reloads during a page refresh. Its
current content remains visible until the response arrives, then the result is
morphed into place. This preserves independently loaded regions such as
pagination through a page morph.

```html
<turbo-frame id="results" src="/results?page=2" refresh="morph">
</turbo-frame>
```

### Refresh streams and broadcasts

The `refresh` stream action reloads the page and can override the page's
configured refresh method and scroll behavior:

```html
<turbo-stream action="refresh" method="morph" scroll="preserve"></turbo-stream>
```

Consecutive broadcast refreshes are debounced. In Rails, use
`broadcasts_refreshes` with a normal stream subscription instead of emitting a
separate DOM-operation broadcast for every change:

```ruby
class Calendar < ApplicationRecord
  broadcasts_refreshes
end
```

```erb
<%= turbo_stream_from @calendar %>
```

## Active Storage delivery hardening

### Byte ranges and disk keys

Active Storage accepts only one byte range per request and limits it to 100 MB
by default. `DiskService#path_for` consistently raises `InvalidKeyError` for
keys with dot segments, invalid keys, or paths outside the service root.
`delete_prefixed` treats glob metacharacters literally rather than expanding
them.

### GCS IAM signing

GCS URL signing through IAM again uses application default credentials. Set
authorization on the service's memoized IAM client without changing unrelated
Google API clients:

```ruby
ActiveStorage::Blob.service.iam_client.authorization =
  Google::Auth::ImpersonatedServiceAccountCredentials.new(options)
```

## Active Storage image-processing security

The `7.2.3.2-8.1.3.1-security` releases—Rails 7.2.3.2, 8.0.5.1, and
8.1.3.1—call `Vips.block_untrusted(true)` at boot. This disables loaders and
savers that libvips marks unfuzzed or untrusted.

When ruby-vips is installed, Active Storage now requires libvips 8.13 or newer
and ruby-vips 2.2.1 or newer. Older versions raise `RuntimeError` during boot.

### Changed transformation and analysis behavior

Variant transformation now raises `Vips::Error` for BMP, ICO, and PSD inputs,
as well as outputs to unfuzzed formats such as FITS and JXL or any format
delegated to ImageMagick.

Analysis of BMP, ICO, PSD, SVG, JPEG XL, JPEG 2000, and Netpbm inputs no longer
records dimensions. Attaching, storing, and downloading these files are
unchanged.

If affected attachment types should never be transformed, remove their MIME
types from the variable-content list:

```ruby
Rails.application.config.active_storage.variable_content_types -= %w[
  image/bmp image/vnd.microsoft.icon image/vnd.adobe.photoshop
]
```

MiniMagick attachment processing itself is unchanged. However, the untrusted
operation block and version checks apply process-wide whenever ruby-vips is
installed. A MiniMagick-only application can avoid both by removing ruby-vips.
