# Concurrency and Ractors

## Structured backtraces and exception causes

Since 3.4.0, `Exception#set_backtrace`, `Kernel#raise`, `Thread#raise`, and
`Fiber#raise` accept arrays of `Thread::Backtrace::Location`. This avoids
converting structured locations through backtrace strings.

```ruby
error.set_backtrace(caller_locations)
```

Since 4.0.0, `Thread#raise` and `Fiber#raise` also accept the `cause:` keyword
in the same way as `Kernel#raise`.

## Fiber scheduler protocol

### Offloading blocking work

A custom scheduler may implement the optional
`Fiber::Scheduler#blocking_operation_wait` hook (since 3.4.0) to move blocking
work out of its event loop.

### Interrupt, yield, close, and write behavior

Since 4.0.0, schedulers may implement:

- `fiber_interrupt` to interrupt a fiber with an exception.
- `yield` to continue processing while signal exceptions are disabled.

The asynchronous `io_close` hook is restored. Flushing an IO write buffer now
invokes the scheduler's `io_write` hook.

## Loading and local Ractor state

Since 3.4.0, `require` is allowed inside a Ractor and performs the load on the
main Ractor. `Ractor._require` exposes the same behavior directly.

The following facilities are also available:

- `Ractor.main?` tests whether execution is on the main Ractor.
- `Ractor.[]` and `Ractor.[]=` manage Ractor-local state.
- `Ractor.store_if_absent` initializes Ractor-local state atomically.

```ruby
Ractor.new do
  require "json"
  Ractor.store_if_absent(:parser) { JSON }
end
```

## Ports and lifecycle

Since 4.0.0, `Ractor::Port` provides:

- `receive`
- `send` and `<<`
- `close`
- `closed?`

Ports replace `Ractor.yield` and `Ractor#take`, which are removed together with
`Ractor#close_incoming` and `Ractor#close_outgoing`.

```ruby
port = Ractor::Port.new
Ractor.new(port) { |out| out << 1 }
port.receive # => 1
```

Ractors gain `join` and `value`. Each Ractor has a `default_port` backing
`Ractor.send` and `Ractor.receive`. `Ractor.select` accepts only Ractors and
Ports and treats Ractor termination as a selectable event.

Use `Ractor.shareable_proc` and `Ractor.shareable_lambda` to create callable
objects that can be shared between Ractors.

## Ruby Box isolation

The experimental `Ruby::Box` (since 4.0.0) isolates definitions loaded into one
box from other boxes. The isolated state includes:

- monkey patches
- global and class variables
- class and module definitions
- loaded Ruby libraries
- loaded native libraries

Enable the feature through the environment:

```sh
RUBY_BOX=1 ruby app.rb
```
