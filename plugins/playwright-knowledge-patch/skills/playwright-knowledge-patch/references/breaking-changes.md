# Breaking Changes

## 1.50

- **toBeEditable scope narrowed**: `toBeEditable()` and `isEditable()` now throw if target is not `<input>`, `<select>`, or another editable element type.
- **Glob URL patterns**: `page.route()` glob patterns no longer support `?` and `[]`. Use regex instead.

## 1.52

- **route.continue() Cookie override removed**: `route.continue()` ignores the `Cookie` header. Use `browserContext.addCookies()` instead.

## 1.54

- Node.js 16 removed, Node.js 18 deprecated.

## 1.55

- **Chromium extension manifest v2 dropped**: Only manifest v3 extensions are supported.

## 1.56

- **backgroundPage deprecated**: `browserContext.on('backgroundpage')` no longer emits; `backgroundPages()` returns empty list.

## 1.57

- **page.accessibility removed**: Use [Axe](https://www.deque.com/axe/) for accessibility testing instead.

## 1.58

- **`_react` and `_vue` selectors removed**: Use standard locators.
- **`:light` selector suffix removed**: Use standard CSS.
- **`devtools` launch option removed**: Use `args: ['--auto-open-devtools-for-tabs']`.
- macOS 13 dropped for WebKit.

## 1.59

- Removed macOS 14 support for WebKit.
- Removed `@playwright/experimental-ct-svelte`.
