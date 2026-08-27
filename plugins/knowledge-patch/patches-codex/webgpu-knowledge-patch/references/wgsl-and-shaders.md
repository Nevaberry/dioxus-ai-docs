# WGSL language and shader behavior

## Validation and layout

### Explicit member alignment cannot be undersized

An `@align(n)` annotation must satisfy the member's required-alignment rule
for every structure (`chrome-133`). An explicit value smaller than the
required alignment now fails shader validation:

```wgsl
struct Invalid {
  @align(4) value: vec4<f32>,
}
```

Remove the annotation or raise it to a valid alignment.

### Standard uniform-buffer layout

The `uniform_buffer_standard_layout` language extension gives uniform buffers
the same layout constraints as storage buffers (`chrome-144`). It removes the
special 16-byte alignment requirement for array elements and nested-structure
offsets.

Detect it through `navigator.gpu.wgslLanguageFeatures`, then declare:

```wgsl
requires uniform_buffer_standard_layout;

struct Inner {
  x: f32,
}
struct Uniforms {
  inner: Inner,
  y: f32, // Offset 4 is valid with the extension.
}
```

Host-side layouts must match the shader path actually selected.

## Subgroups

### Current feature names and enablement

The removed `"chromium-experimental-subgroups"` and
`"chromium-experimental-subgroup-uniform-control-flow"` names must not be
requested (`chrome-133`). Request `"subgroups"` instead. `"subgroups-f16"` is
deprecated; subgroup operations on `f16` require both `"shader-f16"` and
`"subgroups"`.

Shaders using subgroup built-ins and operations must declare
`enable subgroups;` (`chrome-134`). Compute and fragment shaders can then use
`subgroup_invocation_id`, `subgroup_size`, and operations such as
`subgroupAdd()`, `subgroupBallot()`, `subgroupBroadcast()`, and
`subgroupShuffle()`.

```wgsl
enable subgroups;

@compute @workgroup_size(64)
fn main(
  @builtin(subgroup_invocation_id) lane: u32,
  @builtin(subgroup_size) width: u32,
) {
}
```

Do not hard-code a width. Check `GPUAdapterInfo.subgroupMinSize` and
`subgroupMaxSize`.

### Subgroup identity

The `subgroup_id` language extension adds `@builtin(subgroup_id)` and
`@builtin(num_subgroups)` (`chrome-144`). Check the WGSL extension separately,
request the adapter's `"subgroups"` device feature, use `enable subgroups;`,
and declare `requires subgroup_id;`.

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

Subgroups need not always be full, so use the reported width for index math.

### Subgroup-scoped uniformity

When `navigator.gpu.wgslLanguageFeatures` contains
`"subgroup_uniformity"`, uniformity analysis for subgroup and quad built-ins
operates at subgroup scope rather than workgroup scope (`chrome-145`).
`@builtin(subgroup_id)` can then satisfy uniform-control-flow requirements;
invocation-varying branches remain invalid.

## Compute-shader data and indexing

### Uniform workgroup loads from atomics

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

### Linear invocation and workgroup indices

The `linear_indexing` extension adds two `u32` compute built-ins
(`chrome-147-148`):

- `global_invocation_index` flattens the invocation position across the
  complete dispatch.
- `workgroup_index` flattens the workgroup position and is shared by all of
  that workgroup's invocations.

Detect the extension, then use:

```wgsl
requires linear_indexing;

@compute @workgroup_size(64)
fn main(
  @builtin(workgroup_index) groupIndex: u32,
  @builtin(global_invocation_index) invocationIndex: u32,
) {
}
```

## Resource handles and sampling

### Local texture and sampler aliases

The `texture_and_sampler_let` language extension permits texture and sampler
handles in local `let` bindings (`chrome-146`):

```wgsl
@group(0) @binding(0) var source: texture_2d<f32>;

@fragment
fn main() -> @location(0) vec4f {
  let localSource = source;
  return textureLoad(localSource, vec2i(1, 1), 0);
}
```

Without the extension, continue referring to module-scope handle variables.

### Explicit-level sampling of 1D textures

`textureSampleLevel()` accepts 1D textures (`chrome-140`). Vertex shaders can
therefore sample a 1D lookup texture at an explicit mip level:

```wgsl
let color = textureSampleLevel(lutTexture, lutSampler, coordinate, 0.0);
```

## Fragment primitive indices

The optional adapter feature `"primitive-index"` enables the fragment-shader
`@builtin(primitive_index)` value as `u32` (`chrome-142`). Request the device
feature and explicitly enable the WGSL extension:

```wgsl
enable primitive_index;

@fragment
fn main(@builtin(primitive_index) index: u32)
    -> @location(0) vec4f {
  return select(vec4f(0, 0, 1, 1), vec4f(1, 0, 0, 1), index == 1);
}
```

Indices start at zero, advance per primitive, and reset for each drawn
instance.

## Inter-stage limits

`maxInterStageShaderComponents` was deprecated in favor of
`maxInterStageShaderVariables` and scheduled for removal in Chrome 135
(`chrome-133`). Stop requesting or branching on the component limit.

## Immediate address space

Immediate shader inputs use a module-scope `var<immediate>` declaration. The
shipped language gate is `immediate_address_space` (`chrome-149-150`):

```wgsl
requires immediate_address_space;
var<immediate> color: vec4f;
```

Each entry point may statically use at most one immediate variable. Its type
must be concrete, constructible, host-shareable, and contain no arrays. See
the browser API reference for layout sizing, pass writes, and bundle state.
