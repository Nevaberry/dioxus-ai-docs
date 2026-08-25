# TSL and Node APIs

Use this reference for Three Shading Language graphs, node materials, shader helpers, node events, transpilation, and compute-oriented node APIs.

## Compute-enabled NodeMaterial

**Batch:** `r175`

`NodeMaterial` now supports `compute()` integrated into the material, so compute work can be associated directly with a node material.

## Constant and variable node helpers

**Batch:** `r173`

The WebGPU surface introduces `.toConst()`, `Const()`, and `Var()` for creating constant and variable nodes.

## Direction helper migrations

**Batch:** `migration-guide-r173-r185`

TSL renamed `directionToColor()` to `packNormalToRGB()` and `colorToDirection()` to `unpackRGBToNormal()`. WebGL shader code should replace deprecated `inverseTransformDirection()` with `transformNormalByInverseViewMatrix()` for normals or `transformDirectionByInverseViewMatrix()` for directions.

## Expanded TSL Transpiler syntax

**Batch:** `r174`

The TSL Transpiler now handles matrix types, boolean vectors, varyings, basic texture operations, and `discard`.

## Exported device-pixel ratio node

**Batch:** `r180`

`screenDPR` is now exported for use in TSL graphs.

## HemisphereLightNode normal rename

**Batch:** `r177`

`HemisphereLightNode` changed `normalView` to `normalWorld`; custom node code using the former name must migrate.

## InstanceNode partial updates

**Batch:** `r181`

`InstanceNode` now honors `updateRanges`, so marked partial updates are respected for instance data.

## Line2NodeMaterial line-width removal

**Batch:** `r179`

The unused `Line2NodeMaterial.lineWidth` property was removed. Code that still sets or reads that property must stop relying on it when upgrading.

## Line2NodeMaterial vertex-color rename

**Batch:** `r183`

`Line2NodeMaterial.useColor` was renamed to `Line2NodeMaterial.vertexColors`; update direct property access when upgrading.

## Matrix buffer attributes and tangent handling

**Batch:** `r182`

`bufferAttribute()` now supports `mat3` and `mat4` values. TSL also stops auto-generating tangent attributes, so geometry must provide tangents when a node graph requires them.

## NodeBuilder observer rename

**Batch:** `r173`

`NodeBuilder.monitor` was renamed to `NodeBuilder.observer`; update direct property access when migrating to r173.

## NodeMaterial masking and vertex setup

**Batch:** `r177`

`NodeMaterial` introduces `maskNode`. Its `setupVertex()` hook is also now executed when `vertexNode` is defined, which changes the setup lifecycle for custom node materials using an explicit vertex node.

## Normal-map unpacking

**Batch:** `r182`

`NormalMapNode` gains basic support for unpacking normals, making packed normal data usable in node graphs.

## Partial uniform-group updates

**Batch:** `r183`

Uniform groups now support partial updates instead of requiring every value in the group to be refreshed.

## PointsNodeMaterial replaces InstancedPointsNodeMaterial

**Batch:** `r173`

`PointsNodeMaterial` now replaces `InstancedPointsNodeMaterial`. Code using the older material should migrate its imports and construction to `PointsNodeMaterial`.

## Premultiplied alpha in NodeMaterial

**Batch:** `r178`

`NodeMaterial` shaders now honor `material.premultipliedAlpha`; enabling the flag now affects the generated shader output.

## SpriteNodeMaterial transparency default

**Batch:** `r174`

`SpriteNodeMaterial` now defaults `transparent` to `true`. Code that depended on opaque sprite-node materials must set `transparent` explicitly.

## Storage-backed instance attributes

**Batch:** `r182`

`InstanceNode` now supports `StorageInstancedBufferAttribute`, allowing storage-backed per-instance data in node-material workflows.

## Storage-buffer member types

**Batch:** `r177`

`StorageBufferNode` adds `getMemberType()`, allowing node code to query a storage-buffer member's type.

## StorageTextureNode reads and writes

**Batch:** `r183`

`StorageTextureNode` now supports TSL read and write operations.

## TSL 3D storage textures and gather operations

**Batch:** `r185`

TSL adds `storageTexture3D`, `textureGather`, and `textureGatherCompare`, together with the missing `StorageTexture3DNode` exports.

## TSL 3D texture reads

**Batch:** `r182`

TSL adds `texture3DLoad()` and `texture3DLevel()` for explicit 3D texture access.

## TSL alpha and blur helpers

**Batch:** `r177`

TSL adds `premult()` and `unpremult()`. `hashBlur()` also accepts `{ repeats, mask, premultipliedAlpha }` options.

## TSL alpha and step call changes

**Batch:** `r178`

`premult` was renamed to `premultiplyAlpha`. Chained `step()` calls also use corrected parameter ordering, so calls written around the previous inconsistent order must be updated.

## TSL API migrations

**Batch:** `r182`

`DFGApprox` was renamed to `DFGLUT`, and `nodeObject()` was removed for Node classes. Imports and node construction code using the former APIs must be updated.

## TSL before-event hooks

**Batch:** `r181`

TSL adds the `OnBefore*` event family for running node event logic before the corresponding lifecycle stages.

## TSL bit and float packing operations

**Batch:** `r182`

TSL adds bit-count-related functions and float packing and unpacking intrinsics, exposing these low-level operations directly to node code.

## TSL bitcasts

**Batch:** `r180`

TSL adds bitcast functions and corresponding transpiler support, so node and transpiled code can reinterpret bit patterns without numeric conversion.

## TSL blur API changes

**Batch:** `r180`

The blur-filter APIs were aligned, and `premultipliedGaussianBlur()` is now deprecated. Avoid introducing new calls to the deprecated helper and migrate existing blur code to the aligned API.

## TSL camera viewports

**Batch:** `r180`

TSL introduces `cameraViewport` alongside expanded camera-array support, exposing viewport information for camera-array workflows.

## TSL comparison, loop, and math changes

**Batch:** `r175`

TSL adds `samplerComparison`, permits a `while` condition in `Loop()`, and allows `max()` and `min()` to take any number of arguments. `modInt()` is deprecated and should be migrated away from.

## TSL constants and effect inputs

**Batch:** `migration-guide-r173-r185`

TSL renamed `PI2` to `TWO_PI`. `AfterImageNode.damp` is now a `Node<float>`, so `afterImage()` accepts a node constant or uniform instead of requiring a numeric value.

## TSL debug callback signature

**Batch:** `r176`

The `debug()` callback now receives `( builder, code )`; callbacks written against the previous signature must be updated.

## TSL diagnostics

**Batch:** `r183`

`DebugNode` callbacks now receive raw data, and TSL adds `StackTrace`.

## TSL function migrations

**Batch:** `r178`

`TriplanarTexturesNode` moves to `triplanarTextures()`, `EquirectUVNode` to `equirectUV()`, and `MatcapUVNode` to the `matcapUV` Fn constant. Affected `transformed*` names also lose that prefix.

## TSL function, compute, debug, and event support

**Batch:** `r179`

TSL adds sequential object parameters for `Fn({ ... })`, `computeKernel()`, and events. Stack `debug()` can now also be used outside the code flow.

## TSL geometry positions in vertex transforms

**Batch:** `migration-guide-r173-r185`

When assigning `material.positionNode`, `positionLocal` does not include internal transforms such as skinning. Use `positionGeometry` when the node needs vertices from the pre-transformed geometry.

## TSL isolate helper

**Batch:** `r181`

TSL introduces `isolate()` alongside corrected conditional caching, providing an explicit isolation boundary for node code affected by conditional cache reuse.

## TSL layout parameter member types

**Batch:** `r181`

TSL layout-function parameters now support member types, allowing layouts to describe structured parameter members directly.

## TSL math, scopes, and frame events

**Batch:** `r184`

TSL adds hyperbolic math nodes, `global` and `local` scope, global-context access from compute nodes, and the `OnFrameUpdate` and `OnBeforeFrameUpdate` events.

## TSL method renames

**Batch:** `r173`

TSL renamed `varying()` to `toVarying()` and `vertexStage()` to `toVertexStage()`; both old names must be replaced when upgrading.

## TSL mutation and control flow

**Batch:** `r176`

TSL adds `increment()`, `decrement()`, and switch/case support. Expressions are also supported in `loop( { update: ... } )`, including transpiled loop-update expressions.

## TSL naming and assignment changes

**Batch:** `r179`

TSL renamed `label()` to `setName()`. `assign()` also applies `toVar()` automatically, so explicit variable conversion before assignment is no longer required.

## TSL raymarching helpers

**Batch:** `r174`

TSL adds `RaymarchingBox` and `raymarchingTexture3D`; in the final r174 layout, `raymarchingTexture3D` is provided through the example/addon raymarching utility rather than core TSL.

## TSL removals and rename

**Batch:** `r185`

TSL removes the `string` and `arrayBuffer` definitions, and renames `directionToFaceDirection` to `negateOnBackSide`. Imports and node code using those names must be updated.

## TSL sampling and chromatic aberration

**Batch:** `r178`

TSL adds `sample()`, `textureBicubicLevel()`, and chromatic-aberration support for node graphs.

## TSL scene and scriptable-node migration

**Batch:** `r183`

`SceneNode` moved to TSL function-based APIs. The scriptable node and the `ScriptableNodeResources` export were removed, so code importing either surface must migrate or remove it.

## TSL stack helpers

**Batch:** `r176`

TSL adds `Stack()` and `.toStack()` for explicitly creating or converting to a stack.

## TSL subgroup reductions

**Batch:** `r180`

TSL adds `SubgroupFunctionNode`, including support for compute-reduction workflows using subgroup functions.

## TSL tangent frames and sub-builds

**Batch:** `r178`

TSL adds `tangentViewFrame`, `bitangentViewFrame`, and `subBuild()` to its node-building surface.

## TSL texture loads and boolean uniforms

**Batch:** `r179`

TSL texture nodes add `load()`, and `uniform()` now supports boolean values.

## TSL texture offsets

**Batch:** `r180`

TSL texture operations gain texture-offset support, allowing node graphs to address offset texels directly.

## TSL Transpiler extensions

**Batch:** `r178`

The TSL Transpiler now accepts `switch` statements and a simplified `Fn()` layout, and introduces a Linker and `WGSLEncoder`.

## TSL Transpiler structs

**Batch:** `r182`

The TSL Transpiler now supports struct definitions and declarations.

## TSL types and data helpers

**Batch:** `r173`

TSL adds `mat2`, `array()`, `struct()`, `atomicLoad`, and float matrix operations. Shader-node code can now express two-by-two matrices, arrays, structs, atomic loads, and matrix operations on floats directly.

## TSL uniform texture helpers

**Batch:** `r177`

TSL introduces `uniformTexture()` and `uniformCubeTexture()` for creating uniform-backed 2D and cube texture nodes.

## TSL varying interpolation

**Batch:** `r176`

Varying nodes add `varying.setInterpolation()`, allowing their interpolation behavior to be selected explicitly.

## Uniform TSL flow

**Batch:** `r180`

TSL introduces `uniformFlow()` for declaring uniform flow in node code.

## WebGL NodeMaterial compatibility

**Batch:** `r184`

`WebGLRenderer` adds a compatibility layer for `NodeMaterial`.

## WGSL global variables

**Batch:** `r184`

`WGSLNodeBuilder` adds `allowGlobalVariables` for node shaders that require global declarations.

