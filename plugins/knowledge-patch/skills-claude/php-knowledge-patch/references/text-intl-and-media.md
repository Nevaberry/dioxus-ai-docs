# Text, Internationalization, and Media

## Text, CSV, and serialization inputs

### Explicit CSV escape arguments (8.4-migration)

Relying on the default `escape` argument is deprecated for `fgetcsv()`,
`fputcsv()`, `str_getcsv()`, and their `SplFileObject` equivalents. Pass it
explicitly unless the `SplFileObject` already received an explicit value
through `setCsvControl()`.

```php
$row = fgetcsv($stream, null, ',', '"', '\\');
```

### Standard input validation (8.4-migration)

Invalid `round()` modes throw `ValueError` instead of behaving as
`PHP_ROUND_HALF_UP`. CSV delimiter, enclosure, and escape widths are validated,
as are `php_uname()` modes and `unserialize()`'s `allowed_classes` option.

### Byte-oriented character APIs (8.5-migration)

Restrict `chr()` to integers from 0 through 255 and `ord()` to one-byte
strings.

## Date, Intl, locale, and formatting

### Named Intl calendar operations (8.4-migration)

Replace multi-argument Intl calendar setters and constructors with
`setDate()`, `setDateTime()`, `createFromDate()`, or
`createFromDateTime()`.

### Intl and gettext validation (8.4-migration)

Empty gettext domains, invalid Intl locales, and invalid `ResourceBundle`
offsets raise `ValueError`. Validate caller input or catch the exception where
fallback is intentional.

Malformed mbstring conversion maps and encodings likewise raise `ValueError`
rather than relying on warnings or permissive coercion.

### Deprecated date and Intl facilities (8.5-migration)

RFC 7231 Date constants and `intl.error_level` are deprecated. Use manual Intl
error checks or `intl.use_exceptions` rather than relying on that INI setting.

### Collation, Unicode, and PCRE build behavior (8.5-migration)

Intl regular collation sort handles numeric strings like standard
`SORT_REGULAR`. mbstring uses Unicode 17.0 data. PCRE is built without
`PCRE2_EXTRA_ALLOW_LOOKAROUND_BSK`, so revise patterns that depend on that
extension.

### Locale formatting behavior (8.5-migration)

A `printf`-family formatter without explicit precision treats precision as
zero instead of resetting it. Passing integer `0` as the locales argument to
`setlocale()` is unsupported and throws `TypeError`.

### Locale-aware list formatting (8.5.0)

`IntlListFormatter`, available with ICU 67 or newer, formats localized AND,
OR, or unit lists in wide, short, or narrow forms using its `TYPE_*` and
`WIDTH_*` constants.

## mbstring and regular expressions

### Malformed-text indices (8.4-migration)

For strings with encoding errors, `mb_substr()` interprets character indices
consistently with other mbstring functions, so offsets from `mb_strpos()` can
be reused. SJIS-Mac indices refer to Unicode code points produced by
conversion, including characters that expand to multiple code points.

### PCRE 10.44 compatibility (8.4-migration)

The bundled PCRE2 10.44 recognizes `{,3}` as a quantifier rather than literal
text, and some character classes change meaning in UCP mode. Audit patterns
that relied on the former behavior.

### PCRE syntax additions (8.4.0)

PCRE2 supports variable-length lookbehind, spaces between braces in
Perl-compatible items, and named captures up to 128 characters. The `r` and
`(?r)` modifiers, combined with `i`, prevent ASCII and non-ASCII characters
from mixing in caseless matches.

## Validation, randomness, hashing, and compression

### Random numbers and legacy constants (8.4-migration)

Replace `lcg_value()` with `Random\Randomizer::getFloat()`. The
`SUNFUNCS_RET_*` constants are deprecated.

### Invalid hash and DBA inputs (8.4-migration)

Passing invalid options to hash functions is deprecated. Passing `null` or
`false` to `dba_key_split()` is also deprecated. Validate these inputs instead
of relying on fallback behavior.

### Hash and fileinfo deprecations (8.5-migration)

The `MHASH_*` constants are deprecated. The ignored `context` argument of
`finfo_buffer()` is deprecated, and `finfo_close()` is deprecated because its
object cleans itself up automatically.

### Exception-based filtering (8.5.0)

`FILTER_THROW_ON_FAILURE` makes validation failure throw rather than return a
failure value. It cannot be combined with `FILTER_NULL_ON_FAILURE`; that
combination throws `ValueError`.

```php
$id = filter_var($input, FILTER_VALIDATE_INT, FILTER_THROW_ON_FAILURE);
```

### Stricter compression and internationalization input (8.5-migration)

`bzcompress()` validates block size 1–9 and work factor 0–250. Intl time-zone
and locale operations reject documented invalid states with exceptions.

## Graphics and image metadata

### GD range validation and cleanup (8.4-migration, 8.5-migration)

Invalid GD quality, speed, scale, and filter ranges raise `ValueError`.
`imagedestroy()` is deprecated because image objects are freed automatically.

### Image formats and dimension units (8.5.0)

EXIF supports `OffsetTime*` tags and HEIF/HEIC. `getimagesize()` recognizes
HEIF/HEIC and, with ext-libxml, SVG. Its result includes `width_unit` and
`height_unit`; these default to pixels but may differ. SVG is also recognized
by `image_type_to_extension()` and `image_type_to_mime_type()`.
