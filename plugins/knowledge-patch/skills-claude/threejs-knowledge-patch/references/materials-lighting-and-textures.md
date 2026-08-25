# Materials, Lighting, and Textures

Use this reference when working with materials, lights, shadows, textures, color management, blending, and physically based rendering.

## 3D texture copies across GPU backends

**Batch:** `r175`

`copyTextureToTexture()` now works with 3D textures in both the WebGL and WebGPU backends; the WebGL backend's former 3D support is restored.

## Alpha-to-coverage shadows

**Batch:** `r176`

`WebGLRenderer` now supports `alphaToCoverage` when rendering shadows.

## Automatic flat shading without normals

**Batch:** `r183`

The WebGL renderer and TSL normal-node path now force flat shading for geometry that has no normal attribute.

## CCDIKSolver blending

**Batch:** `r174`

`CCDIKSolver` now supports `blendFactor`, allowing IK corrections to be applied partially instead of always at full strength.

## ColorManagement method renames

**Batch:** `migration-guide-r173-r185`

`ColorManagement.fromWorkingColorSpace()` became `workingToColorSpace()`, and `toWorkingColorSpace()` became `colorSpaceToWorking()`.

## Expanded EAC texture support

**Batch:** `r182`

Both `WebGLRenderer` and `WebGPURenderer` support additional EAC texture formats in r182.

## Expanded material lighting

**Batch:** `r183`

`MeshLambertMaterial` and `MeshPhongMaterial` now use `scene.environment` for image-based lighting. `MeshPhysicalMaterial` also applies clearcoat when lit by rectangular area lights.

## GLBufferAttribute normalization

**Batch:** `r178`

`GLBufferAttribute` now exposes a `normalized` property, so externally managed buffer attributes can carry normalization metadata.

## LightProbeGrid

**Batch:** `r184`

`LightProbeGrid` adds position-dependent diffuse global illumination.

## LightProbeGrid indirect bounces

**Batch:** `r185`

`LightProbeGrid.bake()` gains an indirect-bounces option.

## Material copy semantics

**Batch:** `r182`

`Material.copy()` now includes `allowOverride`, so copied materials preserve the override behavior introduced in r175. `ShaderMaterial.copy()` also carries properties that it previously omitted.

## Material JSON deserialization

**Batch:** `r185`

`MaterialLoader` adds `registerMaterial()`, and `Material` adds `fromJSON()`. Material implementations can now be registered with the loader and deserialized through the material API.

## Material map serialization

**Batch:** `r180`

`Material.toJSON()` now includes map properties that were previously omitted. Serialized material output can gain additional texture-map fields after upgrading.

## Material override control

**Batch:** `r175`

`Material` adds `allowOverride`, letting a material control whether an override material may replace it.

```js
material.allowOverride = false;
```

## Mesh and Sprite count

**Batch:** `r177`

`Mesh` and `Sprite` now expose a `count` property. Code targeting r177 can set or inspect the count directly on either object type.

## MeshGouraudMaterial deprecation

**Batch:** `r173`

The `MeshGouraudMaterial` addon is deprecated in r173 and should not be selected for new code.

## PBR and PMREM output changes

**Batch:** `r182`

Energy conservation was corrected for intermediate metalness, mixed iridescent materials, and sheen. PMREM's GGX VNDF sampling was also refined to match Blender roughness, so physically based lighting can change after upgrading.

## PMREM and PBR lighting changes

**Batch:** `r181`

`PMREMGenerator` now uses GGX VNDF importance sampling. Both renderers add multi-scattering energy compensation for direct lighting and improve rough-reflection mixing for IBL, while `WebGLRenderer` replaces its analytical DFG approximation with a LUT; PBR output can therefore change after upgrading.

## PMREM scene capture options

**Batch:** `r174`

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

## RoomEnvironment lighting shift

**Batch:** `migration-guide-r173-r185`

`RoomEnvironment` changed its scene position, so PMREMs generated from it produce different lighting after the upgrade.

## Shadow node and renderer controls

**Batch:** `r183`

`LightShadow` adds `biasNode`, and `NodeMaterial` adds `maskShadowNode`. The new renderer shadow-map setting landed under the final name `shadowMap.transmitted`; do not use the interim `color` or `colored` names.

## Shadow rendering changes

**Batch:** `r182`

`WebGLRenderer` modernizes its shadow-mapping path, while `WebGPURenderer` adds PCF filtering based on Vogel-disk sampling and interleaved gradient noise. Existing shadow output can therefore change after upgrading.

## Shadow-camera layer precedence

**Batch:** `r176`

`ShadowNode` now inherits `camera.layers` only when `shadow.camera.layers` has not been set, so an explicit shadow-camera layer mask is preserved.

## SkyMesh type flag migration

**Batch:** `r182`

`SkyMesh` adds `isSkyMesh` and deprecates `isSky`; type checks should migrate to the new flag.

## Spot-light node controls

**Batch:** `r177`

Custom attenuation can now be supplied through `spotLight.attenuationNode`, and `SpotLightShadow` adds an `aspect` property for configuring the shadow projection's aspect ratio.

## Sprite node size attenuation

**Batch:** `r180`

`SpriteNodeMaterial.sizeAttenuation` is now honored only with perspective cameras. Orthographic-camera rendering no longer applies the setting.

## Sprite outlines and orthographic reflections

**Batch:** `r184`

`OutlineNode` now supports sprites, and the `Reflector` addon supports orthographic cameras.

## SVG gradients and material helpers

**Batch:** `r185`

`SVGLoader` adds basic gradient support and material helpers.

## Texture dimensions and update ranges

**Batch:** `r177`

`Texture` now exposes `width`, `height`, and `depth`, together with `updateRanges` for tracking partial texture updates.

## VideoFrameTexture

**Batch:** `r173`

`VideoFrameTexture` is a new texture class for the WebCodecs API. Instances expose `isVideoFrameTexture` for type detection.

## Wireframe matcap materials

**Batch:** `r181`

`MeshMatcapMaterial` now supports wireframe rendering.

