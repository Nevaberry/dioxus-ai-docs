# WGSL language and shaders

## Validation and layout

### Explicit member alignment

WGSL rejects a struct member whose `@align` is smaller than its required
alignment (`chrome-133`). The rule applies to every struct, not only buffers:

```wgsl
struct Invalid {
  @align(4) value: vec4<f32>,
}
```

Remove an undersized annotation or raise it to a valid alignment.

### Standard uniform-buffer layout

The `uniform_buffer_standard_layout` language extension gives uniform buffers
the storage-buffer layout constraints, removing the special 16-byte alignment
requirement for array elements and nested-structure offsets (`chrome-144`).
Detect the extension and declare it:

```js
if (!navigator.gpu.wgslLanguageFeatures.has(
  "uniform_buffer_standard_layout"
)) {
  throw new Error("Standard uniform layout unavailable");
}
```

```wgsl
requires uniform_buffer_standard_layout;

struct Inner {
  x: f32,
}
struct Uniforms {
  inner: Inner,
  y: f32, // Offset 4 is allowed.
}
@group(0) @binding(0) var<uniform> uniforms: Uniforms;
```

Buffer producers must match whichever layout the shader declares.

## Subgroups

### Features and declarations

The removed experimental feature names
`"chromium-experimental-subgroups"` and
`"chromium-experimental-subgroup-uniform-control-flow"` must not be requested
(`chrome-133`). Request `"subgroups"` instead. `"subgroups-f16"` was
deprecated; subgroup operations on `f16` require both `"shader-f16"` and
`"subgroups"`:

```js
const device = await adapter.requestDevice({
  requiredFeatures: ["shader-f16", "subgroups"],
});
```

Shaders using subgroup built-ins declare `enable subgroups;`
(`chrome-134`). Compute and fragment stages can use
`subgroup_invocation_id`, `subgroup_size`, and operations including
`subgroupAdd()`, `subgroupBallot()`, `subgroupBroadcast()`, and
`subgroupShuffle()`.

Never assume a fixed width. Read `subgroupMinSize` and `subgroupMaxSize` from
adapter info before choosing an algorithm.

### Subgroup identity

The `subgroup_id` language extension supplies `@builtin(subgroup_id)` and
`@builtin(num_subgroups)` (`chrome-144`). Check the language extension
separately from the adapter's `"subgroups"` device feature, request the device
feature, and use both declarations:

```wgsl
enable subgroups;
requires subgroup_id;

@compute @workgroup_size(64)
fn main(
  @builtin(subgroup_id) group: u32,
  @builtin(num_subgroups) groupCount: u32,
  @builtin(subgroup_invocation_id) lane: u32,
  @builtin(subgroup_size) width: u32,
) {
  let localIndex = lane + width * group;
}
```

Subgroups are not guaranteed to be full.

### Subgroup-scoped uniformity

When `navigator.gpu.wgslLanguageFeatures` contains `"subgroup_uniformity"`,
uniformity analysis for subgroup and quad built-ins occurs at subgroup scope
(`chrome-145`). A value such as `subgroup_id` can satisfy uniform-control-flow
requirements, but an invocation-varying branch remains invalid. Detect the
extension before compiling a shader that relies on this analysis.

### Uniform load from an atomic

`workgroupUniformLoad()` accepts a pointer to an atomic value in workgroup
memory (`chrome-137`). It performs an atomic load and returns the value to
every invocation in the workgroup:

```wgsl
var<workgroup> counter: atomic<u32>;

@compute @workgroup_size(1)
fn main() {
  atomicStore(&counter, 42u);
  let value = workgroupUniformLoad(&counter);
}
```

## Optional built-ins and handle bindings

### Primitive index

The adapter feature `"primitive-index"` enables fragment-stage
`@builtin(primitive_index)` as a `u32` (`chrome-142`). Indices start at zero,
advance per primitive, and reset for each drawn instance. Request the device
feature and explicitly enable the shader extension:

```wgsl
enable primitive_index;

@fragment
fn main(@builtin(primitive_index) index: u32)
    -> @location(0) vec4f {
  return select(vec4f(0, 0, 1, 1), vec4f(1, 0, 0, 1), index == 1);
}
```

### Linear compute indices

The `linear_indexing` language extension adds the `u32` compute built-ins
`global_invocation_index` and `workgroup_index` (`chrome-147-148`). The first
flattens an invocation's position across the dispatch; the second flattens the
workgroup position and is shared within that workgroup:

```wgsl
requires linear_indexing;

@compute @workgroup_size(64)
fn main(
  @builtin(workgroup_index) groupIndex: u32,
  @builtin(global_invocation_index) invocationIndex: u32,
) {
}
```

Detect `"linear_indexing"` through `navigator.gpu.wgslLanguageFeatures`.

### Local texture and sampler aliases

The `texture_and_sampler_let` language extension permits texture and sampler
handles in local `let` bindings (`chrome-146`):

```wgsl
@group(0) @binding(0) var source: texture_2d<f32>;

@fragment
fn main() -> @location(0) vec4f {
  let local_source = source;
  return textureLoad(local_source, vec2i(1, 1), 0);
}
```

Without this language support, use the module-scope resource name directly.

## Texture sampling

`textureSampleLevel()` accepts 1D textures (`chrome-140`). This enables
explicit-mip sampling from stages such as vertex shaders:

```wgsl
let color = textureSampleLevel(lutTexture, lutSampler, coordinate, 0.0);
```

## Immediate address-space data

Immediate data is a small immutable range unified across all shader stages
without a bind group or separate device-feature enablement
(`chrome-149-150-guide`). A module-scope `var<immediate>` must have a concrete,
constructible, host-shareable type containing no arrays. Each entry point may
statically use at most one such variable.

The shipped language form requires the `"immediate_address_space"` WGSL
extension and `requires immediate_address_space;` (`chrome-149-150`):

```js
if (!navigator.gpu.wgslLanguageFeatures.has("immediate_address_space")) {
  throw new Error("Immediate data unavailable");
}
```

```wgsl
requires immediate_address_space;
var<immediate> values: vec4<f32>;
```

The shipped encoder method is `setImmediates()`, superseding the earlier guide
spelling `setImmediateData()`. An automatic pipeline layout infers the needed
`immediateSize`; an explicit `GPUPipelineLayoutDescriptor` sets
`immediateSize`, which must cover the shader variable and stay within
`maxImmediateSize` (default 64 bytes).

`setImmediates(rangeOffset, data, dataOffset?, size?)` writes the range's
32-bit slots and uses a four-byte-aligned range offset and copied byte count.
As with `writeBuffer()`, `dataOffset` and `size` count typed-array elements for
typed arrays and bytes for other data. At every draw or dispatch, all
non-padding slots statically used by active stages must have been written since
encoding began. Struct padding contributes to `immediateSize` but its slots
need not be written.

Pipeline layouts share immediate values only when their `immediateSize` values
match. Render bundles snapshot values during bundle encoding. Executing a
bundle clears the render pass's immediate-slot state, and state also resets
before and after every individual bundle; set the needed values again before
a later pass draw.
