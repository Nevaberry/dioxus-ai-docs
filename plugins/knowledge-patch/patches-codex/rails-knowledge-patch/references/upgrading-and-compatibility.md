# Upgrading and Compatibility

## Controller and request compatibility

Rails 7.2 (`7.2`) removes equality comparison between `ActionController::Parameters` and `Hash`. Remove reliance on `config.action_controller.allow_deprecated_parameters_hash_equality`, which is deprecated.

`config.action_dispatch.show_exceptions` no longer accepts boolean `true` or `false`; migrate to a supported symbolic value. Passing content to a void-element builder such as `tag.br` is deprecated.

## Framework APIs removed in Rails 8

Rails 8.0 (`8.0`) removes:

- console extension through `Rails::ConsoleMethods`
- `form_with(model: nil)`
- `ActiveSupport::ProxyObject`
- an `attr_internal_naming_format` beginning with `@`
- array arguments to `ActiveSupport::Deprecation#warn`

It also deprecates multiple-path route declarations; declare one route path at a time.

Rails 8.1 (`8.1`) removes `bin/rake stats` and `STATS_DIRECTORIES`.

## Deprecations needing replacement plans

Rails 8.0 (`8.0`) deprecates:

- the Active Storage Azure backend
- `Benchmark.ms`
- addition or `since` between `Time` and `ActiveSupport::TimeWithZone`

Rails 8.1 (`8.1`) makes `to_time` always preserve the receiver timezone and deprecates `config.active_support.to_time_preserves_timezone`. It also deprecates `String#mb_chars`, `ActiveSupport::Multibyte::Chars`, and `ActiveSupport::Configurable`.

## Regular-expression timeout

Rails 8.0 sets Ruby's global `Regexp.timeout` to one second by default. Audit intentionally expensive regular expressions and override the timeout deliberately if they cannot complete within that limit.

## Cache-store removals

Rails 7.2 (`7.2`) removes cache-store options `:pool_size` and `:pool_timeout`, drops cache format version 6.1, and stops allowing an already-created `Dalli::Client` as a `MemCacheStore` argument.

## Query-string compatibility

Rails 8.1 (`8.1`) treats a leading `[` in a root parameter name literally rather than stripping it, and semicolons no longer separate query pairs. Remove reliance on the deprecated `config.action_dispatch.ignore_leading_brackets` setting.

```ruby
ActionDispatch::ParamBuilder.from_query_string("[foo]=bar")
# => { "[foo]" => "bar" }

ActionDispatch::QueryParser.each_pair("foo=bar;baz=quux").to_a
# => [["foo", "bar;baz=quux"]]
```

New applications enable verbose redirect logs in development. Existing applications can opt in:

```ruby
config.action_dispatch.verbose_redirect_logs = true
```

## Active Record upgrade audit

Review these items in the detailed Active Record reference before an upgrade:

- transaction blocks exited with `return`, `break`, or `throw`
- positional `serialize` arguments and keyword-style `enum`
- obsolete connection cleanup and checkout methods
- adapter minimum versions and renamed pool settings
- finder calls that lack deterministic order
- polymorphic associations with `class_name:`
- bulk inserts on associations with unpersisted members
- `update_all` relations using `WITH`, `WITH RECURSIVE`, or `DISTINCT`

## Active Job upgrade audit

Review the detailed Active Job reference for the transition from symbolic to boolean transactional enqueue configuration, removed argument and scheduling forms, public `klass` on custom serializers, and gem-supplied Sidekiq and SuckerPunch adapters.
