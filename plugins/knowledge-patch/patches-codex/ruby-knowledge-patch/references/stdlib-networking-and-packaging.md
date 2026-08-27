# Standard Library, Networking, and Packaging

## Add package integrity data

`gem push` accepts `--attestation` for storing a Sigstore build-artifact
signature (since 3.4.0). Bundler can write checksums into fresh lockfiles with
the `lockfile_checksums` setting or add them to an existing lockfile:

```sh
bundle config set lockfile_checksums true
bundle lock --add-checksums
```

## Audit standard-library dependencies

`Pathname` moves from a default gem to a core class, and `Set` moves from an
autoloaded standard-library class to core (since 4.0.0).

Set behavior also changes:

- `Set#inspect` renders as `Set[1, 2, 3]`.
- Arguments to `Set#to_set` and `Enumerable#to_set` are deprecated.
- `SortedSet` is no longer autoloaded; install and require the `sorted_set` gem
  explicitly.

These libraries move from default gems to bundled gems:

- `ostruct`
- `pstore`
- `benchmark`
- `logger`
- `rdoc`
- `win32ole`
- `irb`
- `reline`
- `readline`
- `fiddle`

Ruby 4.0.0 ships RubyGems 4.0.3 and Bundler 4.0.3.

The full CGI library is no longer a default gem. Only `cgi/escape` remains,
providing escape/unescape, HTML, URI-component, and element helpers. Add the
full CGI gem explicitly when other CGI facilities are required.

## Set HTTP request metadata explicitly

Net::HTTP no longer automatically assigns
`Content-Type: application/x-www-form-urlencoded` to requests merely because
they have a body (since 4.0.0). Set that header explicitly when the body uses
that encoding.

## Validate URI parsing changes

The URI library defaults to an RFC 3986-compliant parser instead of the older
RFC 2396 parser (since 3.4.0). Re-test edge-case URIs because validation and
interpretation can change.

## Control connection racing and timeouts

Happy Eyeballs v2 is enabled for `Socket.tcp` and `TCPSocket.new` (since
3.4.0). Disable fast fallback globally with either setting:

```sh
RUBY_TCP_NO_FAST_FALLBACK=1 ruby app.rb
```

```ruby
Socket.tcp_fast_fallback = false
```

Or disable it for one connection:

```ruby
TCPSocket.new(host, port, fast_fallback: false)
```

`Socket.tcp` and `TCPSocket.new` accept `open_timeout:` for initial connection
setup (since 4.0.0):

```ruby
TCPSocket.new(host, port, open_timeout: 5)
```

When the caller specifies a timeout, `TCPSocket.new` consistently raises
`IO::TimeoutError`. An OS-level timeout may still raise
`Errno::ETIMEDOUT`, and `Socket.tcp` retains additional cases that can raise
`Errno::ETIMEDOUT`.

## Update Unicode-sensitive behavior

String and regular-expression Unicode data is updated to Unicode 17.0.0,
including Emoji 17.0 (since 4.0.0). Re-test classification, matching, and
display code that depends on Unicode tables.

## Refresh snapshots and diagnostic parsers

Formatting changes since 3.4.0 include:

- Backtrace method labels use single quotes and include a permanent class
  name.
- Extra `rescue` and `ensure` frames are omitted.
- `Hash#inspect` renders symbol keys as `{user: 1}` and spaces other
  associations as `{"user" => 1}`.

Later diagnostics (since 4.0.0) make wrong-arity `ArgumentError` output show
both caller and callee snippets, and backtrace labels include the receiver
class or module. Backtraces no longer expose `internal` frames; C-implemented
methods are attributed like other Ruby source methods.

These changes can affect snapshot tests and any parser that consumes formatted
exceptions, backtraces, or inspected values.

