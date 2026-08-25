# Validation and Testing

## Alternative validation rule sets (2025-04)

`Rule::anyOf()` accepts multiple rule sets and considers the attribute valid when any one complete set passes.

```php
'destination' => Rule::anyOf([
    ['email'],
    ['url'],
]),
```

## Bcrypt input-length enforcement (12.0.0)

Bcrypt hashing can be configured to enforce its 72-byte input limit, preventing longer values from producing insecure hashes.

## Binary file response assertions (2026-03-laravel-12)

HTTP tests can use response assertions with `BinaryFileResponse` instances, so file-download responses no longer need to bypass the normal assertion flow.

## Capitalized validation placeholders (2025-10)

Validator message replacement now recognizes capitalized placeholder forms, allowing custom messages to control placeholder capitalization without post-processing.

## Fake DNS validation (2026-07)

DNS lookups performed by validation rules can be faked in tests.

## Fluent password-rule semantics (2025-12)

The fluent `Password` rule now correctly handles `required()` and `sometimes()` for missing values, nullable empty values, and rule-array usage.

## Fluent string and conditional validation (2026-03-laravel-12)

Laravel adds a fluent string validation rule builder and fills out the conditional validation rule builders.

```php
'name' => [Rule::string()->min(3)->max(100)],
```

## Optional Faker dependency (2025-09)

Laravel can run without `fakerphp/faker` installed. Applications that do not use factories or generated fake data no longer need to carry Faker as a dependency.

## Ordinal positions in validation messages (2025-09)

Validation messages support the `:ordinal-position` placeholder for wildcard array items, with safe handling when the Intl extension is unavailable.

```php
'photos.*.description.required' => 'Describe the :ordinal-position photo.',
```

## Parallel-test maintenance state (2026-06)

An `array` maintenance-mode driver is available for parallel testing.

## PHPUnit 12.2 support (2025-06)

Laravel 12 supports PHPUnit 12.2, allowing application test dependency constraints to move beyond PHPUnit 11.

## PHPUnit 12.4 support (2025-10)

Laravel 12 supports PHPUnit 12.4, allowing application test dependency constraints to move beyond the previously supported 12.2 release.

## Precognitive wildcard validation (2026-01)

Precognitive requests now support wildcard paths in array validation rules.

## Requiring values within an array (2025-05)

`Rule::contains()` builds a validation rule requiring an array input to contain specified values, as in `'features' => ['array', Rule::contains(['search', 'exports'])]`.

## Rotated-key MAC validation (2026-04)

Decryption validates the MAC across all configured decryption keys, allowing ciphertext from a rotated key to be authenticated against the matching key.

## Strict boolean and numeric validation (2025-07)

The `boolean:strict` rule accepts only actual booleans, while `numeric:strict` requires an integer or float instead of accepting numeric strings.

```php
'enabled' => ['boolean:strict'],
'amount' => ['numeric:strict'],
```

## Strict form requests (2026-04)

Form requests now have a strict mode, including `failOnUnknownFields` handling for query parameters. `FormRequest::flushState()` resets the global strict state between tests.

## Strict integers in fluent numeric rules (2026-03-laravel-12)

The fluent `Numeric` validation rule can require strict integers rather than accepting loosely integer-like input.

```php
'quantity' => [Rule::numeric()->integer(strict: true)],
```

## Stringifying fluent password rules (2026-05)

A fluent `Password` rule can be converted to its equivalent password-rule string, allowing it to be reused where a string representation is required.

## SVG image validation (12.0-upgrade)

The `image` validation rule excludes SVG files by default. Opt in with `'image:allow_svg'` or `File::image(allowSvg: true)`.

## Test-time isolation (2026-07)

Fake time is reset globally after each test, preventing time state from leaking into later tests.

## Updated test and component dependencies (2025-12)

Laravel 12 supports PHPUnit 12.5. Reflection facilities have also been split from `illuminate/support` into a dedicated Illuminate Reflection component.

## Uploaded-file encoding validation (2025-11)

The new `encoding` validation rule checks the character encoding of uploaded files.

```php
'import' => ['required', 'file', 'encoding:UTF-8'],
```

## Validating the presence of array keys (2025-05)

The `in_array_keys` validation rule requires an array to contain at least one listed key, as in `'contact' => ['array', 'in_array_keys:email,phone']`.

## Validator outcome callbacks (2026-02)

Validators provide `whenFails()` and `whenPasses()` for registering work that depends on the validation result.

## Version-specific UUID validation (12.0.0)

The `uuid` validation rule can optionally constrain the UUID version, including version 2 and the maximum defined UUID version.

```php
'id' => ['required', 'uuid:7'],
```
