# Validation, Authentication, and Security

Validation rules, authentication and authorization, request forgery protection, encryption, and credentials.

## Additional JSON Schema constraints (2026-02)

Numeric schema types support `multipleOf`, while array schema types support `uniqueItems`.

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

## Cache password-reset prefix removal (2025-07)

The `prefix` option has been removed from cache-backed password reset repositories; remove it from password broker configuration.

## Callback-based signed URL exclusions (12.0.0)

Signed URL validation can use a closure to choose which query-string parameters to ignore.

## Capitalized validation placeholders (2025-10)

Validator message replacement now recognizes capitalized placeholder forms, allowing custom messages to control placeholder capitalization without post-processing.

## Fluent password-rule semantics (2025-12)

The fluent `Password` rule now correctly handles `required()` and `sometimes()` for missing values, nullable empty values, and rule-array usage.

## Fluent string and conditional validation (2026-03-laravel-12)

Laravel adds a fluent string validation rule builder and fills out the conditional validation rule builders.

```php
'name' => [Rule::string()->min(3)->max(100)],
```

## JSON schema contract (2025-11)

Laravel's JSON schema facilities now expose a contract alongside schema-generation improvements, allowing extensions to depend on an abstraction rather than a concrete implementation.

## JSON Schema dependencies (2025-12)

Laravel's JSON Schema facilities can now express dependencies between schema members instead of requiring dependent requirements to be modeled outside the schema.

## JSON Schema deserialization and composition (2026-06)

Illuminate JSON Schema can deserialize array schemas and multi-type unions, and schemas may use `anyOf` composition.

## Line-break rejection in email addresses (2026-05)

Email addresses containing line breaks are now rejected instead of reaching mail handling.

## Nested policy discovery (12.0.0)

Policy auto-discovery now follows parallel nested model and policy namespaces; for example, `App\Models\Admin\User` can discover `App\Policies\Admin\UserPolicy`.

## Ordinal positions in validation messages (2025-09)

Validation messages support the `:ordinal-position` placeholder for wildcard array items, with safe handling when the Intl extension is unavailable.

```php
'photos.*.description.required' => 'Describe the :ordinal-position photo.',
```

## Password reset mail subject (13.0-upgrade)

The default password reset subject is now `Reset your password` instead of `Reset Password Notification`; update exact mail assertions and translation overrides.

## Password reset token expiry units (12.0-upgrade)

`DatabaseTokenRepository` now expects its `$expires` constructor argument in seconds rather than minutes; custom instantiation must convert existing minute values.

## Precognitive wildcard validation (2026-01)

Precognitive requests now support wildcard paths in array validation rules.

## Remember-cookie payloads (2026-01)

Remember cookies now store a MAC of the user's password hash instead of the hash itself. Custom code that reads or creates these cookies must not expect the raw password hash.

## Request forgery protection (13.0-upgrade)

The CSRF middleware is now `PreventRequestForgery` and also validates request origin through `Sec-Fetch-Site`. `VerifyCsrfToken` and `ValidateCsrfToken` remain deprecated aliases; update direct middleware references and use the new `preventRequestForgery(...)` configuration API.

## Requiring values within an array (2025-05)

`Rule::contains()` builds a validation rule requiring an array input to contain specified values, as in `'features' => ['array', Rule::contains(['search', 'exports'])]`.

## Rotated-key MAC validation (2026-04)

Decryption validates the MAC across all configured decryption keys, allowing ciphertext from a rotated key to be authenticated against the matching key.

## Session regeneration during login (2025-10)

`Auth::login()` now regenerates the session. Manual authentication flows and their tests should expect the session identifier to rotate during login.

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

## Unsetting JSON Schema flags (2026-05)

Fluent JSON Schema boolean flags can now be unset after being enabled, which helps when refining or reusing a schema definition.

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
