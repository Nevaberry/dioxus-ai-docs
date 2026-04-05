# Content Security Policy (CSP)

## Overview

Astro 6.0 includes built-in CSP support. Astro auto-generates hashes for inline scripts and styles.

**History**: Introduced as top-level `csp` in 6.0-beta, moved to `security.csp` in 6.0 stable.

## Simple Mode

```js
export default defineConfig({
  security: { csp: true },
});
```

Provides default protection with auto-generated hashes. Works with responsive images out of the box.

## Full Configuration

```js
export default defineConfig({
  security: {
    csp: {
      algorithm: 'SHA-512', // default: SHA-256
      directives: ["default-src 'self'", "img-src 'self' https://cdn.example.com"],
      styleDirective: { hashes: ['sha384-hash'] },
      scriptDirective: { hashes: ['sha384-hash'] },
    },
  },
});
```

## Configuration Options

| Option | Type | Default | Description |
|---|---|---|---|
| `algorithm` | `string` | `'SHA-256'` | Hash algorithm for script/style hashes |
| `directives` | `string[]` | — | Additional CSP directives |
| `styleDirective` | `object` | — | Extra hashes/resources for style-src |
| `scriptDirective` | `object` | — | Extra hashes/resources for script-src |

## Migration from Beta

If upgrading from 6.0-beta, move the config:

```js
// 6.0-beta (deprecated)
export default defineConfig({ csp: true });

// 6.0 stable
export default defineConfig({ security: { csp: true } });
```
