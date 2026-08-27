# Graphics, Media, and NativeImage

## Offscreen rendering

### GPU shared textures

Electron 34.0.0 adds GPU-accelerated shared-texture offscreen rendering.

At 39.0.0, the shared-texture `paint` event payload became structured:
`sharedTextureHandle`, `planes`, and `modifier` are grouped beneath `handle`
instead of appearing at the top level.

### HDR output

Since 39.0.0, Offscreen Rendering supports `RGBAF16` output in the scRGB HDR
color space.

### Device scale factor

Since 42.0.0, offscreen rendering defaults to a constant device scale factor of
`1.0` rather than inheriting the primary display's scale. Set the desired value
explicitly when output needs another scale:

```js
const window = new BrowserWindow({
  webPreferences: {
    offscreen: { deviceScaleFactor: 2 },
  },
});
```

## Imported shared textures

Since 40.0.0, Electron can import an external shared texture as a `VideoFrame`.

Imported textures support these additional formats:

- NV12 since Electron 40, including 41.0.0.
- `nv16` and the 10-bit YUV `p010le` format since 42.0.0.

## Desktop capture audio

### macOS usage description

Since 39.0.0, apps using `desktopCapturer` on macOS 14.2 or later must define
`NSAudioCaptureUsageDescription` in `Info.plist`. Without it, the newer CoreAudio
Tap path can yield a dead audio stream without an error or warning. To retain the
old path temporarily, disable the feature before startup:

```js
app.commandLine.appendSwitch(
  'disable-features',
  'MacCatapLoopbackAudioForScreenShare',
);
```

### Restricting the application's own audio

The 41.10.5-43.4.1 patch batch includes Electron 43.4.0 support for
`getDisplayMedia({ audio: { restrictOwnAudio: true } })` in requests handled by
`setDisplayMediaRequestHandler()`. Loopback capture then excludes the
application's own playback instead of silently including it.

## NativeImage bitmap migration

At 36.0.0, `NativeImage.getBitmap()` was deprecated in favor of
`NativeImage.toBitmap()`. They are equivalent aliases and each returns a newly
allocated bitmap copy.

## NativeImage color handling

### Profile normalization

Since 43.0.0, images with color profiles passed to `nativeImage` have their pixel
values normalized to sRGB. Pixel values from visually identical images should be
similar after their respective profiles are applied.

### Selecting bitmap color space

The `breaking-changes` guidance clarifies that Electron 43
`NativeImage.toBitmap()` and the deprecated `getBitmap()` alias convert to sRGB
by default. Pass `colorSpace` to retain the source space or request another
conversion:

```js
const { nativeImage } = require('electron');
const image = nativeImage.createFromPath('photo.png');
const p3Bitmap = image.toBitmap({
  colorSpace: {
    primaries: 'p3',
    transfer: 'srgb',
    matrix: 'rgb',
    range: 'full',
  },
});
```

## Named native images

Since Electron 39, including 40.0.0,
`nativeImage.createFromNamedImage()` accepts SF Symbol names.

At 42.0.0, passing an `hslShift` array as the second argument was deprecated.
Pass an options object instead:

```js
nativeImage.createFromNamedImage(imageName, {
  hslShift: [0, 1, -1],
});
```
