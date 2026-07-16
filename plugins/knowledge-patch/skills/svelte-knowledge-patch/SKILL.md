---
name: svelte-knowledge-patch
description: Svelte current compatibility guidance. Use for Svelte work.
license: MIT
version: null
metadata:
  author: Nevaberry
---

# Svelte Knowledge Patch

Use this patch when writing, reviewing, upgrading, or troubleshooting Svelte and
SvelteKit applications. Start with the migration notes, then read every topic
reference relevant to the code being changed.

## Reference index

| Reference | Topics |
| --- | --- |
| [SvelteKit routing and runtime](references/kit-routing-and-runtime.md) | Error boundaries, paths, typed route parameters, navigation, prerendering, environment guards, CSP, service workers, rerouting, and instrumentation |
| [Remote forms](references/remote-forms.md) | Deep-partial values, schemas, preflight, submission and reset state, validation issues, redirect targets, and streamed uploads |
| [Remote queries and commands](references/remote-queries-and-commands.md) | Optional inputs, URL context, explicit awaiting, refreshes, invalidation, cache policy, transport errors, and live reconnects |
| [Runes and components](references/runes-and-components.md) | Dependency tracking, state and props, stable IDs, attachments, snippets, template declarations, contexts, and asynchronous rendering |
| [Svelte 5 migration](references/svelte-5-migration.md) | Staged dependency and syntax migration |
| [Tooling, build, and deployment](references/tooling-build-and-deployment.md) | Clientless and inline builds, precompression, generated typings, Vite, CLI scaffolding, configuration, TypeScript, CSP hydration, Cloudflare, and Deno |

## Migration and behavior changes

### Upgrade in stages

Move a Svelte 3 application to Svelte 4 before adopting Svelte 5. Then update
`svelte` and related packages such as `vite-plugin-svelte`. Existing component
syntax can coexist with Svelte 5, and application upgrades do not need to wait
for every component dependency to migrate.

Run the optional syntax migration only after the dependency upgrade:

```sh
npx sv migrate svelte-5
```

Read [Svelte 5 migration](references/svelte-5-migration.md) before changing an
older application.

### Await remote calls explicitly

A remote function call in a template does not delay rendering merely because it
was invoked. Add `await` when its completion must gate output:

```svelte
<p>{await getSummary()}</p>
```

Do not rely on implicit blocking. See
[Remote queries and commands](references/remote-queries-and-commands.md).

### Track reactive reads precisely

- Treat reactive reads after an `await` written directly in `$derived(...)` as
  dependencies. Reads hidden in a called helper are not covered by that rule.
- Expect `$effect` to subscribe only to values read synchronously during its
  latest execution. Reads after `await` or in timers are not tracked.
- Read a proxy property, not just the proxy object, when an effect must react to
  that property's mutations.
- Do not expect destructuring from a `$state` proxy to stay reactive.
- Do not expect `$derived` results to be deep-proxied.

### Preserve state ownership

A fallback object supplied while destructuring `$props()` is an ordinary object,
not a state proxy. Mutating parent-owned state can update the parent, but warns
unless the prop is explicitly bindable. Design child-to-parent writes as bindings
or callbacks instead of silently mutating ownership.

Class fields initialized with `$state` compile to non-enumerable accessors. Do
not serialize or spread such instances expecting those fields to appear; expose
serializable values explicitly.

### Treat prerender conflicts as build errors

- A prerendered root `+server.js` must return HTML.
- A prerenderable route containing both `+page` and `+server` is ambiguous and
  fails early; pages otherwise take precedence during prerendering.
- Configure `prerender.handleInvalidUrl` for malformed crawl targets.

### Account for navigation ordering

During navigation, SvelteKit blurs the active element before updating the
component. `blur` and `focusout` handlers therefore see outgoing data. Snapshot
restoration happens after `afterNavigate` callbacks.

### Recheck generated and build configuration

Generated TypeScript configuration no longer injects `types: ['node']`. Add Node
types yourself only when project code needs them. Preserve explicit Vite 8
`codeSplitting`; SvelteKit no longer replaces it unnecessarily.

If the root route tree sets `csr = false`, SvelteKit can omit the client build
entirely. Do not assume client artifacts exist in a fully server-rendered build.

## Runes and component quick reference

### Coordinate asynchronous UI

Use `$effect.pending()` to count promises pending in the current boundary; child
boundaries are excluded. Use `$state.eager(value)` for immediate feedback that
must not wait for synchronized asynchronous updates.

```svelte
{#if $effect.pending()}
	<p>Saving…</p>
{/if}

<a aria-current={$state.eager(pathname) === '/' ? 'page' : null} href="/">
	Home
</a>
```

### Use derived state for optimistic UI

A `$derived` binding declared with `let` can be reassigned. Its optimistic value
lasts until a dependency changes and the derived expression recalculates.

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

Use `$props.id()` for component-instance IDs shared by server rendering and
hydration:

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
behavior with the symbol from `createAttachmentKey()`.

### Respect snippet constraints

Snippet parameters support defaults and destructuring, but not rest parameters.
Top-level snippets can be exported from `<script module>` when they have no
direct or transitive dependency on instance-script declarations. Use
`createRawSnippet` only for programmatic snippet construction.

Template scope also accepts `let` and `const` declaration tags, including
multiple declarators whose later initializers refer to earlier ones:

```svelte
{let count = $state(0), doubled = $derived(count * 2)}
<button onclick={() => count++}>{doubled}</button>
```

Read [Runes and components](references/runes-and-components.md) for complete
tracking, ownership, attachment, snippet, and asynchronous-rendering details.

## SvelteKit remote-data quick reference

### Type remote inputs and form values narrowly

Remote `query`, `command`, and `prerender` inputs may be optional when their
declared type allows omission. Remote form `.value()` and `.set(...)` accept
deep-partial nested shapes. Optional schema fields work with
`exactOptionalPropertyTypes`.

Model checkbox-like boolean fields as optional when unchecked HTML controls are
omitted. Empty file inputs are likewise omitted from remote form payloads.

### Refresh and consume remote results safely

Remote queries can refresh related queries. Navigation with `invalidateAll`
resets remote query state before the next route begins. Failed calls are safely
consumed by reading `current` or `error`; preserving an HTTP status and body is
expected for transport failures.

Remote responses use `cache-control: private, no-store`. Do not put personalized
results in shared caches by overriding that policy casually.

### Drive form UI from built-in state

Use a remote form's `submitted` property rather than duplicating submission
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
- Include `ws:`, `wss:`, and `trusted-types-eval` in CSP source lists when the
  application policy requires them.
- Use `$service-worker`'s `base` in development as well as production.
- Initialize server observability from `instrumentation.server.ts`; SvelteKit can
  emit OpenTelemetry traces.
- Expect support for asynchronous rerouting, streamed form uploads,
  CSP-compatible hydration, automatic Cloudflare adapter setup, and Deno.

Read [SvelteKit routing and runtime](references/kit-routing-and-runtime.md) and
[Tooling, build, and deployment](references/tooling-build-and-deployment.md)
before changing adapters, build output, runtime hooks, or security policy.
