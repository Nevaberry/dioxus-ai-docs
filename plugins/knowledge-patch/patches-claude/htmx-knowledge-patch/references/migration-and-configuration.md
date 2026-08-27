# Migration and Configuration

## Upgrade separately distributed extensions

Since `2.0.0`, extensions are versioned outside the core repository. Most 1.x
extensions still work, but the SSE extension has a breaking change and must be
upgraded. Replace the removed `hx-sse` and `hx-ws` attributes with the
attributes provided by the corresponding extensions.

Audit each extension independently rather than assuming its version follows
the installed core package.

## Choose the module-specific build

Use the distribution that matches the consumer:

| Consumer | Distribution |
| --- | --- |
| Direct browser script | `/dist/htmx.js` |
| ECMAScript module | `/dist/htmx.esm.js` |
| AMD | `/dist/htmx.amd.js` |
| CommonJS | `/dist/htmx.cjs.js` |

The ESM distribution exposes htmx as its default export:

```js
import htmx from "htmx.org/dist/htmx.esm.js";
```

## Review changed request and scrolling defaults

Requests are same-origin-only by default, `DELETE` values are sent as URL
parameters, and swap scrolling is instant. Restore the corresponding earlier
behavior only when the application depends on it:

```js
htmx.config.methodsThatUseUrlParams = ["get"];
htmx.config.selfRequestsOnly = false;
htmx.config.scrollBehavior = "smooth";
```

When setting `selfRequestsOnly` to `false`, also validate cross-origin
destinations and configure CORS as described in
[Requests and validation](requests-and-validation.md#allowlist-cross-origin-destinations).

## Use htmx in Shadow DOM

htmx behavior is supported inside Shadow DOM, so Web Components can place
htmx attributes within their shadow roots.

## Prefer stability when planning upgrades

The maintenance policy favors preserving APIs, implementation quirks, and
defaults so upgrades remain low-risk. Behavioral improvements generally use a
new configuration option rather than silently changing a default. A working
1.x installation does not need to move to 2.x merely to stay current.

## Explore new behavior through extensions

New functionality is generally explored in extensions before it is considered
for core. Core additions are expected mainly when browser capabilities create
a new opportunity. The extensions API may expand to support features that
remain outside core.

## Upgrade on the cadence that suits the project

Releases are planned roughly quarterly and are not expected to impose
recurring major-feature migrations. Follow them selectively when the project
needs a particular bug fix instead of upgrading on every release.
