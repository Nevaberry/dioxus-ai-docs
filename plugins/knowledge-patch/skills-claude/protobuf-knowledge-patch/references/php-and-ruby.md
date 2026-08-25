# PHP, Ruby, and JRuby runtimes

## JSON numeric parsing (`30.0-migration`)

Ruby and PHP reject nonnumeric strings such as `""`, `"12abc"`, and `"abc"`
for numeric protobuf fields. These inputs only produced warnings in the prior
v29.x behavior, so callers must now validate or reject them before parsing.

## PHP JSON validation (`34.0-announcement`)

PHP JSON parsing rejects:

- out-of-range values;
- non-integer numeric values for integer fields;
- duplicate fields belonging to one oneof;
- non-string values for string fields.

JSON serialization rejects `Infinity` and `NaN` when encountered as number
values. Treat all of these as input/output contract changes, not merely warning
changes.

## PHP renamed runtime types (`34.0-announcement`)

| Removed type | Replacement |
| --- | --- |
| `Google\Protobuf\Field_Kind` | `Google\Protobuf\Field\Kind` |
| `Google\Protobuf\Field_Cardinality` | `Google\Protobuf\Field\Cardinality` |
| `Google\Protobuf\Internal\RepeatedField` | `Google\Protobuf\RepeatedField` |

## PHP defaults and type checking (`34.0-announcement`)

The runtime honors proto2 and Editions scalar-field defaults rather than
silently ignoring them. Pure-PHP type checks now match upb-PHP, including
rejection of `null` for string fields. Audit code that used absence or `null` as
a stand-in for a declared default.

## PHP runtime baseline (`34.0-migration`)

The runtime requires PHP 8.2 or newer.

## Typed generated setters (`34.0`)

Generated PHP setters have PHP type hints, and redundant `GPBUtil` checks were
removed. Reflection code, subclasses, and callers that depended on untyped
setter signatures must adapt to the declared types.

## PHP JSON default emission (`34.0`)

JSON serialization can be configured to emit fields whose values equal their
defaults. Select the option when a consumer requires explicit default-valued
members; otherwise preserve the normal omission behavior.

## PHP reflection presence (`34.0`)

PHP field descriptors implement `hasPresence()`. The broken
`hasOptionalKeyword()` helper was removed. Use semantic presence instead of
trying to infer it from an optional keyword or a descriptor label.

## Ruby interpreter baseline (`31.0`)

Ruby 3.0 support was removed; the runtime requires Ruby 3.1 or newer.

## Ruby RBS generation (`34.0`)

Ruby code generation can emit RBS files so generated protobuf types participate
in RBS-based type checking. Add those artifacts to the type-checking build when
using RBS.

## Ruby 4.0 (`34.0`)

The Ruby runtime supports Ruby 4.0.

## Ruby UTF-8 timing (`30.0-migration`)

Ruby surfaces UTF-8 enforcement errors earlier when a protobuf `string` field
contains invalid UTF-8. Do not depend on delayed failure during serialization.

## JRuby FFI implementation (`30.0`)

JRuby uses its FFI implementation by default. Applications that depended on the
previous implementation must test and migrate explicitly. This did not trigger
a Ruby package-major bump because JRuby is not officially supported.
