# Concurrency and IO

## Preserve structured exception context

`Exception#set_backtrace`, `Kernel#raise`, `Thread#raise`, and `Fiber#raise`
accept arrays of `Thread::Backtrace::Location` (since 3.4.0). Pass
`caller_locations` directly instead of converting locations to strings:

```ruby
error.set_backtrace(caller_locations)
```

`Thread#raise` and `Fiber#raise` also accept `cause:` in the same way as
`Kernel#raise` (since 4.0.0).

## Implement the scheduler protocol

A custom fiber scheduler may implement the optional
`Fiber::Scheduler#blocking_operation_wait` hook to move blocking work out of
its event loop (since 3.4.0).

The protocol later adds or restores these behaviors (since 4.0.0):

- `fiber_interrupt` may interrupt a fiber with an exception.
- `yield` lets the scheduler keep processing while signal exceptions are
  disabled.
- The asynchronous `io_close` hook is restored.
- Flushing an IO write buffer invokes `io_write`.

Exercise buffered writes, close paths, exception interruption, and signal
handling when validating a scheduler.

## Load code and store local state in Ractors

`require` is allowed inside a Ractor and performs the load on the main Ractor
(since 3.4.0). `Ractor._require` exposes this behavior directly.
`Ractor.main?` identifies the main Ractor.

Use `Ractor.[]` and `Ractor.[]=` for Ractor-local state. Use
`Ractor.store_if_absent` for atomic initialization:

```ruby
Ractor.new do
  require "json"
  Ractor.store_if_absent(:parser) { JSON }
end
```

## Migrate Ractor messaging and lifecycle

`Ractor::Port` supplies `receive`, `send`/`<<`, `close`, and `closed?` (since
4.0.0). It replaces `Ractor.yield` and `Ractor#take`, which are removed along
with `Ractor#close_incoming` and `Ractor#close_outgoing`:

```ruby
port = Ractor::Port.new
Ractor.new(port) { |out| out << 1 }
port.receive # => 1
```

Each Ractor has a `default_port` backing `Ractor.send` and `Ractor.receive`.
`Ractor.select` accepts only Ractors and Ports and treats Ractor termination as
selectable. Ractors also provide `join` and `value`.

Create cross-Ractor callables with `Ractor.shareable_proc` or
`Ractor.shareable_lambda`.

## Handle file and IO behavior

`File::Stat#birthtime` is available on Linux through `statx` when both the
kernel and filesystem support it (since 4.0.0). Do not assume every Linux
filesystem reports a birth time.

`IO.select` accepts `Float::INFINITY` as its timeout. The deprecated leading
`|` process-creation behavior has been removed from `Kernel#open` and IO class
methods; use an explicit process API instead.

