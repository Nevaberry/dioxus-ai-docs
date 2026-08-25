# Upgrading and Compatibility

## Browser compatibility

### Version guards

The `7.2` `allow_browser` controller guard blocks recognized browsers below
the requested versions. Unknown browsers and clients without a user-agent are
allowed. Blocked clients receive `public/406-unsupported-browser.html` with
status 406.

New applications place the guard in `ApplicationController`. Scope it with
`only:` or `except:` when it should not apply to every action.

```ruby
allow_browser versions: :modern
allow_browser versions: { safari: 16.4, firefox: 121, ie: false }
allow_browser versions: { chrome: 119 }, only: :show
```

## Action Controller and views

### Parameters and exception rendering

`ActionController::Parameters` can no longer be compared with a `Hash`.
`config.action_controller.allow_deprecated_parameters_hash_equality` is
deprecated, so update comparisons rather than retaining the compatibility
switch.

`config.action_dispatch.show_exceptions` no longer accepts boolean `true` or
`false`; use a supported symbolic setting.

### Builder and form restrictions

Passing content to a void-element builder such as `tag.br` is deprecated.
`form_with(model: nil)` is removed.

Declare one route path at a time. Multiple-path route declarations are
deprecated.

## Cache stores

Cache stores no longer accept `:pool_size` or `:pool_timeout`. Cache format
version 6.1 is unsupported, and `MemCacheStore` no longer accepts an existing
`Dalli::Client` instance.

## Framework-wide changes

### Regular-expression timeout

Rails `8.0` sets Ruby's global `Regexp.timeout` to one second by default.
Applications with intentionally expensive regular expressions should set an
explicit value after reviewing their performance and denial-of-service risk.

### Removed extension and compatibility APIs

Remove code that depends on:

- console extension through `Rails::ConsoleMethods`;
- `ActiveSupport::ProxyObject`;
- an `@`-prefixed `attr_internal_naming_format`; or
- array arguments to `ActiveSupport::Deprecation#warn`.

Railties `8.1` also removes `bin/rake stats` and `STATS_DIRECTORIES`.

### Deprecations needing replacement

Plan replacements for:

- `Benchmark.ms`;
- the Active Storage Azure backend;
- addition or `since` between `Time` and `ActiveSupport::TimeWithZone`;
- `String#mb_chars` and `ActiveSupport::Multibyte::Chars`; and
- `ActiveSupport::Configurable`.

`to_time` now always preserves the receiver's timezone, and
`config.active_support.to_time_preserves_timezone` is deprecated. Audit code
that depended on the older conversion behavior.
