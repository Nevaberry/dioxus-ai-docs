# I/O, Networking, and Standard Library

## Socket connection behavior

### Fast fallback

Since 3.4.0, Happy Eyeballs v2 is enabled for `Socket.tcp` and
`TCPSocket.new`. It can be disabled:

- Globally with `RUBY_TCP_NO_FAST_FALLBACK=1`.
- Globally with `Socket.tcp_fast_fallback = false`.
- Per call with `fast_fallback: false`.

```ruby
TCPSocket.new(host, port, fast_fallback: false)
```

### Connection timeouts

Since 4.0.0, `Socket.tcp` and `TCPSocket.new` accept `open_timeout:` for the
initial connection.

```ruby
TCPSocket.new(host, port, open_timeout: 5)
```

A user-specified timeout in `TCPSocket.new` consistently raises
`IO::TimeoutError`. OS-level timeouts can still raise `Errno::ETIMEDOUT`, and
`Socket.tcp` retains additional cases that can also raise it.

## URI and HTTP compatibility

### RFC 3986 parser

Since 3.4.0, the URI library uses an RFC 3986-compliant default parser instead
of the older RFC 2396 parser. Validation and interpretation of edge-case URIs
can therefore change.

### Net::HTTP content type

Since 4.0.0, Net::HTTP does not automatically assign
`Content-Type: application/x-www-form-urlencoded` to body-bearing requests.
Set it explicitly when required by the receiving service.

Deprecated Net::HTTP proxy, response-code, and receiver constants were removed
in 3.4.0.

## IO and filesystem behavior

### Select timeout and process opening

Since 4.0.0, `IO.select` accepts `Float::INFINITY` as its timeout.

The deprecated leading-`|` process creation behavior is removed from
`Kernel#open` and IO class methods. Use an explicit process-opening API rather
than treating a pipe-prefixed string as a subprocess.

### Linux birth time

`File::Stat#birthtime` is available on Linux since 4.0.0 through `statx` when
both the kernel and filesystem support it.

## Core and packaged libraries

### Pathname and Set

Since 4.0.0, `Pathname` moves from a default gem to a core class, and `Set`
moves from an autoloaded standard-library class to core.

Related Set changes:

- `Set#inspect` renders as `Set[1, 2, 3]`.
- Arguments to `Set#to_set` and `Enumerable#to_set` are deprecated.
- `SortedSet` is no longer autoloaded; install and require the `sorted_set` gem
  explicitly.

### Default gems becoming bundled gems

Since 4.0.0, these libraries move from default gems to bundled gems:

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

Ruby 4.0 ships RubyGems 4.0.3 and Bundler 4.0.3.

### CGI packaging

Since 4.0.0, the full CGI library is no longer a default gem. Only
`cgi/escape` remains. It provides:

- escape and unescape helpers
- HTML helpers
- URI-component helpers
- element helpers
