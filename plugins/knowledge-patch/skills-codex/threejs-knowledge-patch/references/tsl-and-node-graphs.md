# TSL and node graphs

TSL syntax, node-material APIs, shader construction, storage, and compute helpers.

## Compute-enabled NodeMaterial (r175)

`NodeMaterial` now supports `compute()` integrated into the material, so compute work can be associated directly with a node material.

## Expanded TSL Transpiler syntax (r174)

The TSL Transpiler now handles matrix types, boolean vectors, varyings, basic texture operations, and `discard`.

## InstanceNode partial updates (r181)

`InstanceNode` now honors `updateRanges`, so marked partial updates are respected for instance data.

## New TSL coordinate, fog, and post-processing helpers (r183)

TSL adds `clipSpace`, `exponentialHeightFogFactor()`, and the `retroPass` post-processing helper.

## NodeMaterial masking and vertex setup (r177)

`NodeMaterial` introduces `maskNode`. Its `setupVertex()` hook is also now executed when `vertexNode` is defined, which changes the setup lifecycle for custom node materials using an explicit vertex node.

## Partial uniform-group updates (r183)

Uniform groups now support partial updates instead of requiring every value in the group to be refreshed.

## Premultiplied alpha in NodeMaterial (r178)

`NodeMaterial` shaders now honor `material.premultipliedAlpha`; enabling the flag now affects the generated shader output.

## SpriteNodeMaterial transparency default (r174)

`SpriteNodeMaterial` now defaults `transparent` to `true`. Code that depended on opaque sprite-node materials must set `transparent` explicitly.

## StorageTextureNode reads and writes (r183)

`StorageTextureNode` now supports TSL read and write operations.

## TSL 3D storage textures and gather operations (r185)

TSL adds `storageTexture3D`, `textureGather`, and `textureGatherCompare`, together with the missing `StorageTexture3DNode` exports.

## TSL 3D texture reads (r182)

TSL adds `texture3DLoad()` and `texture3DLevel()` for explicit 3D texture access.

## TSL alpha and blur helpers (r177)

TSL adds `premult()` and `unpremult()`. `hashBlur()` also accepts `{ repeats, mask, premultipliedAlpha }` options.

## TSL alpha and step call changes (r178)

`premult` was renamed to `premultiplyAlpha`. Chained `step()` calls also use corrected parameter ordering, so calls written around the previous inconsistent order must be updated.

## TSL before-event hooks (r181)

TSL adds the `OnBefore*` event family for running node event logic before the corresponding lifecycle stages.

## TSL bit and float packing operations (r182)

TSL adds bit-count-related functions and float packing and unpacking intrinsics, exposing these low-level operations directly to node code.

## TSL bitcasts (r180)

TSL adds bitcast functions and corresponding transpiler support, so node and transpiled code can reinterpret bit patterns without numeric conversion.

## TSL blur API changes (r180)

The blur-filter APIs were aligned, and `premultipliedGaussianBlur()` is now deprecated. Avoid introducing new calls to the deprecated helper and migrate existing blur code to the aligned API.

## TSL camera viewports (r180)

TSL introduces `cameraViewport` alongside expanded camera-array support, exposing viewport information for camera-array workflows.

## TSL comparison, loop, and math changes (r175)

TSL adds `samplerComparison`, permits a `while` condition in `Loop()`, and allows `max()` and `min()` to take any number of arguments. `modInt()` is deprecated and should be migrated away from.

## TSL debug callback signature (r176)

The `debug()` callback now receives `( builder, code )`; callbacks written against the previous signature must be updated.

## TSL diagnostics (r183)

`DebugNode` callbacks now receive raw data, and TSL adds `StackTrace`.

## TSL function, compute, debug, and event support (r179)

TSL adds sequential object parameters for `Fn({ ... })`, `computeKernel()`, and events. Stack `debug()` can now also be used outside the code flow.

## TSL isolate helper (r181)

TSL introduces `isolate()` alongside corrected conditional caching, providing an explicit isolation boundary for node code affected by conditional cache reuse.

## TSL layout parameter member types (r181)

TSL layout-function parameters now support member types, allowing layouts to describe structured parameter members directly.

## TSL math, scopes, and frame events (r184)

TSL adds hyperbolic math nodes, `global` and `local` scope, global-context access from compute nodes, and the `OnFrameUpdate` and `OnBeforeFrameUpdate` events.

## TSL mutation and control flow (r176)

TSL adds `increment()`, `decrement()`, and switch/case support. Expressions are also supported in `loop( { update: ... } )`, including transpiled loop-update expressions.

## TSL naming and assignment changes (r179)

TSL renamed `label()` to `setName()`. `assign()` also applies `toVar()` automatically, so explicit variable conversion before assignment is no longer required.

## TSL raymarching helpers (r174)

TSL adds `RaymarchingBox` and `raymarchingTexture3D`; in the final r174 layout, `raymarchingTexture3D` is provided through the example/addon raymarching utility rather than core TSL.

## TSL sampling and chromatic aberration (r178)

TSL adds `sample()`, `textureBicubicLevel()`, and chromatic-aberration support for node graphs.

## TSL scene and scriptable-node migration (r183)

`SceneNode` moved to TSL function-based APIs. The scriptable node and the `ScriptableNodeResources` export were removed, so code importing either surface must migrate or remove it.

## TSL stack helpers (r176)

TSL adds `Stack()` and `.toStack()` for explicitly creating or converting to a stack.

## TSL subgroup reductions (r180)

TSL adds `SubgroupFunctionNode`, including support for compute-reduction workflows using subgroup functions.

## TSL tangent frames and sub-builds (r178)

TSL adds `tangentViewFrame`, `bitangentViewFrame`, and `subBuild()` to its node-building surface.

## TSL texture loads and boolean uniforms (r179)

TSL texture nodes add `load()`, and `uniform()` now supports boolean values.

## TSL texture offsets (r180)

TSL texture operations gain texture-offset support, allowing node graphs to address offset texels directly.

## TSL Transpiler extensions (r178)

The TSL Transpiler now accepts `switch` statements and a simplified `Fn()` layout, and introduces a Linker and `WGSLEncoder`.

## TSL Transpiler structs (r182)

The TSL Transpiler now supports struct definitions and declarations.

## TSL types and data helpers (r173)

TSL adds `mat2`, `array()`, `struct()`, `atomicLoad`, and float matrix operations. Shader-node code can now express two-by-two matrices, arrays, structs, atomic loads, and matrix operations on floats directly.

## TSL uniform texture helpers (r177)

TSL introduces `uniformTexture()` and `uniformCubeTexture()` for creating uniform-backed 2D and cube texture nodes.

## TSL varying interpolation (r176)

Varying nodes add `varying.setInterpolation()`, allowing their interpolation behavior to be selected explicitly.

## Uniform TSL flow (r180)

TSL introduces `uniformFlow()` for declaring uniform flow in node code.

## WebGL NodeMaterial compatibility (r184)

`WebGLRenderer` adds a compatibility layer for `NodeMaterial`.

## WGSL global variables (r184)

`WGSLNodeBuilder` adds `allowGlobalVariables` for node shaders that require global declarations.
