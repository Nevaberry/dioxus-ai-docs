---
name: svelte-knowledge-patch
description: Svelte
version: null
license: MIT
metadata:
  author: Nevaberry
---


# Svelte Knowledge Patch

Use this patch when writing, reviewing, migrating, or troubleshooting Svelte
and SvelteKit applications. Start with the migration and behavior changes,
then open every topic reference relevant to the work.

## Reference index

| Reference | Topics |
| --- | --- |
| [SvelteKit routing and runtime](references/kit-routing-and-runtime.md) | Error boundaries, paths, typed parameters, prerendering, navigation, environment guards, CSP, service workers, rerouting, instrumentation, and CSRF |
| [Remote forms](references/remote-forms.md) | Deep-partial values, schemas, preflight, redirect targets, submission and reset state, validation issues, and streamed uploads |
| [Remote queries and commands](references/remote-queries-and-commands.md) | Optional inputs, URL context, explicit awaiting, refreshes, invalidation, cache policy, transport failures, and live reconnects |
| [Runes and components](references/runes-and-components.md) | Dependency tracking, state and props, stable IDs, attachments, snippets, template declarations, contexts, and asynchronous rendering |
| [Svelte 5 migration](references/svelte-5-migration.md) | Staged dependency and syntax migration |
| [Tooling, build, and deployment](references/tooling-build-and-deployment.md) | Clientless and inline builds, precompression, generated typings, Vite, CLI scaffolding, configuration, hydration, Cloudflare, and Deno |

## Migration and behavior changes

### Upgrade in stages

Move a Svelte 3 application to Svelte 4 before adopting Svelte 5. Update
`svelte` and related packages such as `vite-plugin-svelte` before migrating
syntax. Existing component syntax can coexist with Svelte 5, so an application
upgrade does not need to wait for all component dependencies to migrate.

Run the optional app-wide syntax migration afterward:

```sh
npx sv migrate svelte-5
```

Read [Svelte 5 migration](references/svelte-5-migration.md) before changing an
older application.

### Update moved environment imports

Import `defineEnvVars` from its dedicated package entry point:

```js
import { defineEnvVars } from '@sveltejs/kit/env';
```

Replace imports from older entry points while upgrading SvelteKit.

### Await remote calls explicitly

Calling a remote function in a template does not itself delay rendering. Add
`await` when completion must gate the output:

```svelte
<p>{await getSummary()}</p>
```

Do not rely on implicit blocking. See
[Remote queries and commands](references/remote-queries-and-commands.md).

### Recheck generated and build configuration

Generated TypeScript configuration no longer injects `types: ['node']`. Add
Node types only when project code needs them. Preserve an explicit Vite 8
`codeSplitting` setting; SvelteKit no longer replaces it unnecessarily.

If the root route tree sets `csr = false`, SvelteKit can omit the client build
entirely. Do not assume client artifacts exist in a fully server-rendered
build.

### Treat prerender conflicts as build errors

- A prerendered root `+server.js` must return HTML.
- A prerenderable route containing both `+page` and `+server` is ambiguous and
  fails early; pages otherwise take precedence during prerendering.
- Configure `prerender.handleInvalidUrl` for malformed crawl targets.

## Runes and component quick reference

### Track reactive reads precisely

- Reactive reads after an `await` written directly in `$derived(...)` remain
  dependencies. This does not cover an `await` hidden in a called helper.
- `$effect` subscribes only to reactive values read synchronously during its
  latest execution. Reads after `await` or inside timers are not tracked.
- Read a proxy property, rather than only the proxy object, when an effect must
  react to that property's mutations.
- Destructuring a `$state` proxy captures ordinary, non-reactive values.
- A `$derived` result is returned as-is and is not deep-proxied.

### Preserve state ownership

A fallback object supplied while destructuring `$props()` is ordinary data,
not a state proxy. Mutating parent-owned state can update the parent but warns
unless the prop is explicitly bindable. Mark a prop bindable before using it
for intentional child-to-parent writes.

Class fields initialized with `$state` compile to non-enumerable accessors. Do
not serialize or spread such instances expecting those fields to appear;
expose serializable values explicitly.

### Coordinate asynchronous UI

Use `$effect.pending()` to count pending promises in the current boundary;
child boundaries are excluded. Use `$state.eager(value)` for immediate feedback
that should not wait for synchronized asynchronous updates.

```svelte
{#if $effect.pending()}
	<p>Saving…</p>
{/if}

<a aria-current={$state.eager(pathname) === '/' ? 'page' : null} href="/">
	Home
</a>
```

### Use derived state for optimistic UI

A `$derived` binding declared with `let` can be reassigned. Its optimistic
value lasts until a dependency changes and recalculates the expression.

```svelte
<script>
	let { post } = $props();
	let likes = $derived(post.likes);
	const like = () => likes += 1;
</script>
```

Destructuring directly from `$derived(...)` creates individually reactive
bindings:

```js
let { a, b } = $derived(makeValues());
```

### Generate hydration-stable IDs

Use `$props.id()` for component-instance IDs that agree between server
rendering and hydration:

```svelte
<script>const uid = $props.id();</script>
<label for="{uid}-name">Name</label>
<input id="{uid}-name" />
```

### Prefer attachments for element lifecycle behavior

Apply an attachment with `{@attach ...}`. It receives the mounted element and
may return cleanup logic:

```svelte
<script>
	const autofocus = (node) => {
		node.focus();
		return () => {};
	};
</script>

<input {@attach autofocus} />
```

Adapt an existing action with `fromAction`. For parameterized actions, pass a
function that returns the argument. Library-authored spread props can attach
behavior with the symbol returned by `createAttachmentKey()`.

### Respect snippet and template constraints

Snippet parameters support defaults and destructuring, but not rest
parameters. Top-level snippets can be exported from `<script module>` only
when they have no direct or transitive dependency on instance-script
declarations. Use `createRawSnippet` for programmatic snippet creation.

Template scope accepts `let` and `const` declaration tags, including multiple
declarators whose later initializers refer to earlier ones:

```svelte
{let count = $state(0), doubled = $derived(count * 2)}
<button onclick={() => count++}>{doubled}</button>
```

Read [Runes and components](references/runes-and-components.md) for the full
tracking, ownership, attachment, snippet, context, and async-rendering details.

## Remote-data quick reference

### Type remote inputs and forms narrowly

Remote `query`, `command`, and `prerender` inputs may be optional when their
declared type permits omission. Remote form `.value()` and `.set(...)` accept
deep-partial nested shapes. Optional schema fields work with
`exactOptionalPropertyTypes`.

Model checkbox-like booleans as optional when unchecked HTML controls are
omitted. Empty file inputs are also omitted from remote form payloads.

### Refresh and consume results safely

Remote queries can refresh related queries. Navigation with `invalidateAll`
resets remote query state before the next route begins. Reading `current` or
`error` safely consumes a failed call, and transport failures preserve their
HTTP status and body.

Remote responses use `cache-control: private, no-store`. Do not override that
policy casually for personalized results.

### Drive form UI from built-in state

Use a remote form's `submitted` property instead of duplicating submission
state. Resetting a form clears issues and touched fields. Branch-level
`issues()` returns `undefined` when only a descendant field has an issue.

Read [Remote forms](references/remote-forms.md) and
[Remote queries and commands](references/remote-queries-and-commands.md) before
implementing remote data flows.

## Routing, runtime, and deployment quick reference

- Pass query and hash suffixes through `$app/paths.resolve()`.
- Rely on matcher-narrowed route parameters in `$app/types`, `$app/state`, and
  hooks rather than recasting them.
- Call `preloadCode` during initial loading when early route-code fetches help.
- Guard runtime-only environment validation with `building` from
  `$app/environment`.
- During navigation, blur handlers see outgoing data; snapshot restoration
  follows `afterNavigate` callbacks.
- Include `ws:`, `wss:`, and `trusted-types-eval` in CSP source lists when the
  application policy requires them.
- Use `$service-worker`'s `base` in development as well as production.
- Initialize server observability from `instrumentation.server.ts`; SvelteKit
  can emit OpenTelemetry traces.
- Account for asynchronous rerouting, streamed form uploads, CSP-compatible
  hydration, automatic Cloudflare adapter setup, and Deno support.

Read [SvelteKit routing and runtime](references/kit-routing-and-runtime.md) and
[Tooling, build, and deployment](references/tooling-build-and-deployment.md)
before changing adapters, build output, runtime hooks, or security policy.
