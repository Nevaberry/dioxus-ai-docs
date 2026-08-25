# Resources and Engine Behavior

## Inherited options and autonaming

An explicit `protect: false` or `retainOnDelete: false` on a child overrides an
inherited `true`. A protected-delete error no longer stops unrelated deployment
work. Autonaming configuration became stable in 3.146.0 and applies to custom,
not component, resources. It can disable generated names globally or configure
the resources beneath a component without code changes.

Provider inheritance during registration honors the `provider` option without
incorrectly carrying default providers between resource packages. A component's
providers also apply to parented invokes.

## Imports and reads

A program resource with the `import` option can be adopted and updated in one
deployment, and the import ID survives later updates. The engine honors imports
inserted by resource transforms. An import identifier that differs from the
provider's canonical ID no longer makes the resource delete on a later update.

Import files may provide inputs and outputs. Supplying outputs imports the state
directly and skips the provider read. Provider resources can appear alongside
the imported resources that use them.

PCL `read` blocks query resources by ID without registration. `customTimeouts`
includes a `read` timeout.

## Resource hooks

Go, Node.js, and Python support lifecycle hooks; hooks pass through component
`Construct`, and transforms can set them. `ResourceHookArgs` includes type and
name. Destroy operations involving delete hooks must run the program;
after-delete hooks also run for components.

`OnError` hooks implement retry policy. All provider errors reach error hooks;
a successful hook command retries, while a failing after-hook fails the
deployment. Hook calls receive resource options. Node.js and Python hook secrets
remain secret `Output` values.

## Replacement

`pulumi state taint` and `untaint` set or clear forced replacement for the next
update. `replaceWith`, introduced in batch `replace-with` at v3.207.0, replaces a
custom resource when any referenced resource is replaced even without an
infrastructure dependency. Relationships can be transitive or mutual; Go,
Python, Node.js, and Java support it, while C# and YAML were not yet supported by
that release.

`replacement_trigger` replaces when any arbitrary trigger value changes. Engine
and Go support began in 3.208.0, followed by Node.js and Python. Replacement
triggers propagate through remote-component `Construct` calls.

## Diffs and failure behavior

Go `HideDiffs`, Node.js `hideDiffs`, and Python `hide_diffs` suppress selected
diff display. An `ignoreChanges` path absent from old state uses the new value
instead of erroring. Diffs nested in `Output` values are no longer ignored.

Failed resource registrations produce faulted outputs rather than unknowns.
Node.js and Python `Output.recover` handle exceptions during resolution.

## Refresh and dynamic providers

Providers can ask the engine to refresh affected resources after partial
failure. Node.js and Python dynamic-provider `read()` may return inputs so a
refresh preserves the values needed for future diffs. Refreshing stack
configuration includes its imported environments.

## Views, state values, and snippets

Engine views are enabled by default as of 3.176.0 and YAML views as of 3.177.0.
The builtin `Stash` resource keeps an arbitrary value in state. State accepts
floating-point NaN and infinity.

PCL snippets are retained in state for ad-hoc resources and can be targeted by
UUID with `TargetSnippets`. Stateful `pulumi do` create, delete, upsert, and
patch operations maintain these direct-resource entries.

## Component registration

Go and Node.js components send their inputs for diffing and state storage,
matching Python. Node.js can opt out with
`PULUMI_NODEJS_SKIP_COMPONENT_INPUTS`. Local Node.js components obtain version
metadata from `package.json`; Python component providers can set a version.
Node.js `initialize` receives resource options, name, and type.

## Invoke scheduling

Output-form invokes declare dependencies, allowing the engine to defer calls
until resources and remote-component children are created. During preview they
resolve unknown. Go also infers dependencies from invoke arguments. This final
dependency-gating behavior is recorded in `3.255.0-3.258.0`.
