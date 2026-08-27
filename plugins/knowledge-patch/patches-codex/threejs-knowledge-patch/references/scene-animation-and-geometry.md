# Scene, animation, materials, and geometry

Core objects, animation, lighting, materials, geometry, math, and physics-facing data.

## 3D texture copies across GPU backends (r175)

`copyTextureToTexture()` now works with 3D textures in both the WebGL and WebGPU backends; the WebGL backend's former 3D support is restored.

## Alpha-to-coverage shadows (r176)

`WebGLRenderer` now supports `alphaToCoverage` when rendering shadows.

## AnimationAction creation and reversal behavior (r184)

Creating an `AnimationAction` now preserves interpolant settings, and reversing `timeScale` no longer causes a jump.

## AnimationClipCreator default name (r175)

`AnimationClipCreator` now uses an empty string as the default clip name when no name is supplied.

## Automatic ExtrudeGeometry shape cleanup (r175)

`ExtrudeGeometry` now cleans shape data automatically before extrusion, changing how unclean input contours are handled.

## Automatic flat shading without normals (r183)

The WebGL renderer and TSL normal-node path now force flat shading for geometry that has no normal attribute.

## BatchedMesh opacity and wireframes (r183)

`BatchedMesh` now supports per-instance opacity and wireframe materials.

## BatchedMesh optimization updates (r182)

`BatchedMesh.optimize()` now updates its index and attributes correctly. Applications that worked around stale geometry data after optimization should recheck those workarounds.

## BatchedMesh selection (r181)

`SelectionBox` now supports selecting `BatchedMesh` content.

## BezierInterpolant (r183)

r183 adds `BezierInterpolant` as an animation interpolant for Bézier-interpolated values.

## Built-in renderer contexts (r182)

TSL adds a global renderer-context node together with `builtinShadowContext()` and `builtinAOContext()` for accessing built-in shadow and ambient-occlusion contexts.

## Camera scale no longer affects the view matrix (r183)

Camera scale is now excluded from the view matrix, so scaling a camera no longer scales its view transform.

## CapsuleGeometry height and segmentation (r176)

`CapsuleGeometry` renames its `length` parameter to `height` and adds a `heightSegments` parameter, allowing separate control over tessellation along the capsule's height.

## Clamped plane-line intersections (r184)

`Plane.intersectLine()` adds `clampToLine`, allowing callers to request a result clamped to the supplied line.

## Closed Catmull-Rom extrusion paths (r182)

`ExtrudeGeometry` now honors `CatmullRomCurve3.closed`. Extrusions along a closed Catmull-Rom path can therefore produce different geometry after upgrading.

## Collada polygon and joint instances (r184)

`ColladaLoader` now supports the `polygons` primitive and `instance_joint`.

## Constant and variable node helpers (r173)

The WebGPU surface introduces `.toConst()`, `Const()`, and `Var()` for creating constant and variable nodes.

## Corrected copy semantics (r184)

`Object3D.copy()` now preserves `pivot`, and `RenderTarget.copy()` preserves multiview state.

## Decoder and transcoder URL defaults (r185)

`DRACOLoader` and `KTX2Loader` now use relative file URLs by default. `DRACOLoader.setDecoderConfig()` is deprecated, and decoder URLs for glTF use are now exported.

## Direction-aware bone transforms (r184)

`SkinnedMesh.applyBoneTransform()` can now take a `Vector4`, supporting both direction and position transformations.

## Dynamically sized ArrayCamera (r173)

`WebGPURenderer` now permits dynamic resizing of an `ArrayCamera` camera array, so the array no longer has to remain fixed after setup.

## Expanded EAC texture support (r182)

Both `WebGLRenderer` and `WebGPURenderer` support additional EAC texture formats in r182.

## Expanded material lighting (r183)

`MeshLambertMaterial` and `MeshPhongMaterial` now use `scene.environment` for image-based lighting. `MeshPhysicalMaterial` also applies clearcoat when lit by rectangular area lights.

## Exported device-pixel ratio node (r180)

`screenDPR` is now exported for use in TSL graphs.

## Float light-probe generation (r179)

`LightProbeGenerator.fromCubeRenderTarget()` now supports render targets using `FloatType`.

## GLBufferAttribute normalization (r178)

`GLBufferAttribute` now exposes a `normalized` property, so externally managed buffer attributes can carry normalization metadata.

## Indirect compute dispatch (r181)

`WebGPURenderer` adds `dispatchWorkgroupsIndirect`, enabling compute workgroup counts to come from an indirect GPU buffer.

## Indirect drawing offset (r182)

`BufferGeometry` adds an `indirectOffset` parameter for indirect drawing, allowing geometry to select an offset within indirect draw data.

## Instance velocity (r183)

`InstanceNode` now supports velocity data for instanced rendering workflows.

## Interleaved Gradient Noise relocation (r181)

Interleaved Gradient Noise moved from TSL into `PostProcessingUtils`; update imports that use the utility directly.

## ISO gain-map metadata (r183)

`UltraHDRLoader` now supports ISO 21496-1 gain-map metadata.

## LightProbeGrid (r184)

`LightProbeGrid` adds position-dependent diffuse global illumination.

## LightProbeGrid indirect bounces (r185)

`LightProbeGrid.bake()` gains an indirect-bounces option.

## Line-segment distance queries (r179)

`Line3` adds a method for computing the closest squared distance between two line segments, so applications no longer need a separate implementation for that query.

## Material copy semantics (r182)

`Material.copy()` now includes `allowOverride`, so copied materials preserve the override behavior introduced in r175. `ShaderMaterial.copy()` also carries properties that it previously omitted.

## Material override control (r175)

`Material` adds `allowOverride`, letting a material control whether an override material may replace it.

```js
material.allowOverride = false;
```

## Matrix buffer attributes and tangent handling (r182)

`bufferAttribute()` now supports `mat3` and `mat4` values. TSL also stops auto-generating tangent attributes, so geometry must provide tangents when a node graph requires them.

## Mesh and Sprite count (r177)

`Mesh` and `Sprite` now expose a `count` property. Code targeting r177 can set or inspect the count directly on either object type.

## New geometry addons (r185)

r185 adds the `LoftGeometry` addon and `TileCreasedNormalsPlugin`.

## Normal-map unpacking (r182)

`NormalMapNode` gains basic support for unpacking normals, making packed normal data usable in node graphs.

## Object3D static and pivot data (r183)

`Object3D.static` is now preserved by `copy()` and JSON serialization. `Object3D` also gains `pivot`, with support in exporters and in glTF import and export.

## PBR and PMREM output changes (r182)

Energy conservation was corrected for intermediate metalness, mixed iridescent materials, and sheen. PMREM's GGX VNDF sampling was also refined to match Blender roughness, so physically based lighting can change after upgrading.

## Perspective volume rendering (r185)

`VolumeShader` now supports perspective cameras.

## Physics addon changes (r182)

`AmmoPhysics` adds restitution support, `Octree` adds a `Box3` interface, and the physics helpers now report errors when `getShape()` is used with unsupported geometry types.

## PMREM and PBR lighting changes (r181)

`PMREMGenerator` now uses GGX VNDF importance sampling. Both renderers add multi-scattering energy compensation for direct lighting and improve rough-reflection mixing for IBL, while `WebGLRenderer` replaces its analytical DFG approximation with a LUT; PBR output can therefore change after upgrading.

## PMREM scene capture options (r174)

`PMREMGenerator.fromScene()` now accepts `size` and `position` options, allowing control over the generated environment map's resolution and capture point.

```js
const target = pmremGenerator.fromScene(
  scene,
  0,
  0.1,
  100,
  { size: 512, position: new THREE.Vector3(0, 1, 0) }
);
```

## Quaternion slerp extrapolation (r183)

Quaternion slerp methods now extrapolate when the interpolation factor lies outside the usual `[0, 1]` interval.

## Rapier heightfields (r176)

The `RapierPhysics` addon adds heightfield support.

## Raw pointer-lock movement (r175)

`PointerLockControls.lock()` gains an `unadjustedMovement` option, allowing callers to request unadjusted pointer motion.

## Rendering addon additions (r183)

`HalftoneShader` adds a diamond shape, `Sky`/`SkyMesh` add procedural clouds while dropping the legacy gamma-correction curve, and the WebGPU addons add `GodraysNode`.

## Reversed-depth additions (r183)

Core adds the `ReversedDepthFuncs` dictionary, viewport-depth view-Z functions support reversed depth, and `WebGPURenderer` gains basic reversed-depth-buffer support.

## Shadow node and renderer controls (r183)

`LightShadow` adds `biasNode`, and `NodeMaterial` adds `maskShadowNode`. The new renderer shadow-map setting landed under the final name `shadowMap.transmitted`; do not use the interim `color` or `colored` names.

## Shadow-camera layer precedence (r176)

`ShadowNode` now inherits `camera.layers` only when `shadow.camera.layers` has not been set, so an explicit shadow-camera layer mask is preserved.

## SkyMesh type flag migration (r182)

`SkyMesh` adds `isSkyMesh` and deprecates `isSky`; type checks should migrate to the new flag.

## Spot-light node controls (r177)

Custom attenuation can now be supplied through `spotLight.attenuationNode`, and `SpotLightShadow` adds an `aspect` property for configuring the shadow projection's aspect ratio.

## Sprite node size attenuation (r180)

`SpriteNodeMaterial.sizeAttenuation` is now honored only with perspective cameras. Orthographic-camera rendering no longer applies the setting.

## Sprite outlines and orthographic reflections (r184)

`OutlineNode` now supports sprites, and the `Reflector` addon supports orthographic cameras.

## Storage-backed instance attributes (r182)

`InstanceNode` now supports `StorageInstancedBufferAttribute`, allowing storage-backed per-instance data in node-material workflows.

## Storage-buffer member types (r177)

`StorageBufferNode` adds `getMemberType()`, allowing node code to query a storage-buffer member's type.

## StorageTexture manual mipmaps (r181)

`WebGPURenderer` now permits manual mipmap creation with `StorageTexture`.

## SVG gradients and material helpers (r185)

`SVGLoader` adds basic gradient support and material helpers.

## Texture dimensions and update ranges (r177)

`Texture` now exposes `width`, `height`, and `depth`, together with `updateRanges` for tracking partial texture updates.

## Timer connection lifecycle (r174)

`Timer` adds `connect()` and `disconnect()` so applications can explicitly manage its document connection and visibility-event lifecycle.

```js
timer.connect(document);
timer.disconnect();
```

## Timestamp query spelling (r173)

The WebGPU renderer property `timeStampQuerySet` was renamed to `timestampQuerySet`; integrations accessing it directly must use the corrected spelling.

## TorusGeometry angular controls (r183)

`TorusGeometry` adds `thetaStart` and `thetaLength` controls for selecting the generated angular span.

## VRML cameras (r183)

`VRMLLoader` now imports cameras from VRML assets.

## Wireframe matcap materials (r181)

`MeshMatcapMaterial` now supports wireframe rendering.
