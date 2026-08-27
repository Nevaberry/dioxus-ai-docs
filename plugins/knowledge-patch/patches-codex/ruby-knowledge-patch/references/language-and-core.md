# Language and Core Behavior

## Migrate mutable string code

With deprecation warnings enabled, mutating a string literal in a file without
a `frozen_string_literal` comment warns (since 3.4.0).
`--disable-frozen-string-literal` opts out. Unary `+` duplicates a string when
mutating the original would trigger the warning, making it suitable for owned
mutable buffers:

```ruby
buffer = +"value"
buffer << "!"
```

Mutating the string returned by `Symbol#to_s` also warns under
`-W:deprecated`; that returned string is intended to become frozen. Duplicate
it before changing it:

```ruby
name = :user.to_s.dup
name << "!"
```

For binary construction, `String#append_as_bytes` concatenates without
encoding validation or conversion:

```ruby
packet = +"".b
packet.append_as_bytes("\xFF".b)
```

String trimming methods accept selector arguments (since 4.0.0): `strip`,
`strip!`, `lstrip`, `lstrip!`, `rstrip`, and `rstrip!`.

## Rewrite changed syntax and coercion

Index assignment no longer permits explicit block passing or keyword
arguments (since 3.4.0). Rewrite forms such as these:

```ruby
items[0, &block] = value
items[0, mode: :fast] = value
```

Leading `||`, `&&`, `and`, and `or` now continue the preceding line, like a
leading fluent dot (since 4.0.0):

```ruby
if ready
   && authorized
  run
end
```

`*nil` no longer calls `nil.to_a`, matching `**nil`, which does not call
`nil.to_hash`.

`Float()` and `String#to_f` accept a decimal point with no following fractional
digits, including before an exponent (since 3.4.0):

```ruby
Float("1.E-1") # => 0.1
"1.E-1".to_f   # => 0.1
```

Previously, the first expression raised `ArgumentError` and the second
returned `1.0`.

## Update reflection and inspection

`Binding#local_variables` no longer includes numbered parameters (since
4.0.0), and ordinary local-variable get, set, and defined APIs reject them.
Use these dedicated APIs for numbered parameters and `it`:

- `Binding#implicit_parameters`
- `Binding#implicit_parameter_get`
- `Binding#implicit_parameter_defined?`

`Proc#parameters` reports an anonymous optional parameter as `[:opt]`, not
`[:opt, nil]`.

`Kernel#inspect` honors an `instance_variables_to_inspect` method, allowing a
class to omit selected state from the default representation:

```ruby
class Config
  def initialize
    @host, @password = "db.example", "secret"
  end

  private def instance_variables_to_inspect = [:@host]
end

Config.new.inspect # omits @password
```

## Account for numeric and range semantics

`Integer#**` and `Rational#**` preserve sufficiently large exact results as
`Integer` or `Rational`, rather than returning `Float::INFINITY` or
`Float::NAN` (since 3.4.0). Only extremely large results raise.

`Range#step` uses `+` consistently for numeric and nonnumeric types. This
enables time stepping such as:

```ruby
(Time.utc(2022, 2, 24)..).step(86_400)
```

`Range#size` raises `TypeError` for a non-iterable range. Later boundary fixes
make `Range#to_set` size-check endless ranges, allow `Range#overlap?` to handle
unbounded ranges, and correct `Range#max` for beginless integer ranges (since
4.0.0).

`Enumerator.produce` accepts `size:` as an integer, `Float::INFINITY`, a
callable, or `nil`. Without `size:`, its size remains `Float::INFINITY`:

```ruby
enum = Enumerator.produce(1, size: Float::INFINITY, &:succ)
enum.size # => Float::INFINITY
```

`Math.log1p` and `Math.expm1` are available.

## Enable targeted warnings

The `strict_unused_block` warning reports a block passed to a method that does
not use it. The `performance` category reports redefinition of specially
optimized core methods (since 3.4.0):

```ruby
Warning[:strict_unused_block] = true
Warning[:performance] = true
```

## Replace removed or deprecated Ruby interfaces

The following interfaces are removed as of 3.4.0:

- `Refinement#refined_class`
- mutation through `DidYouMean::SPELL_CHECKERS`
- deprecated Net::HTTP proxy, response-code, and receiver constants

As of 4.0.0, `ObjectSpace._id2ref` is deprecated, while
`Process::Status#&` and `Process::Status#>>` are removed.

