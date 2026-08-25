# Graphics, media, and NativeImage

Use this reference for offscreen rendering, external and shared textures, image
color handling, system image APIs, and desktop-capture audio.

## Offscreen rendering

### GPU shared-texture rendering

Electron 34.0.0 adds GPU-accelerated shared-texture offscreen rendering.

### HDR output

Electron 39.0.0 offscreen rendering supports `RGBAF16` output in the scRGB HDR
color space.

### Shared-texture paint payload

In Electron 39.0.0, a shared-texture offscreen `paint` event emits a structured
object. `sharedTextureHandle`, `planes`, and `modifier` are grouped under its
`handle` property rather than appearing at the top level. Update destructuring
and native interop code accordingly.

### External textures as VideoFrames

Electron 40.0.0 can import an external shared texture as a `VideoFrame`.

### Imported YUV formats

- Electron 41.0.0 supports imported shared textures in NV12 format; this is
  also available in Electron 40.
- Electron 42.0.0 adds the `nv16` pixel format and the `p010le` 10-bit YUV pixel
  format.

### Explicit offscreen scale

Electron 42.0.0 changes offscreen rendering's default device scale factor from
the primary display's scale to a constant `1.0`. Set a different value
explicitly when required:

```js
const window = new BrowserWindow({
  webPreferences: {
    offscreen: { deviceScaleFactor: 2 },
  },
});
```

## NativeImage bitmap and color behavior

### `toBitmap()` migration

Electron 36.0.0 deprecates `NativeImage.getBitmap()`. Use
`NativeImage.toBitmap()` instead. Both APIs are equivalent aliases that return
a newly allocated bitmap copy.

### Input color normalization

Electron 43.0.0 normalizes an image with a color profile to sRGB when it is
passed to `nativeImage`. Pixel values from visually identical images should be
similar after their color spaces have been applied.

### Bitmap output color space

In Electron 43, `NativeImage.toBitmap()` and its deprecated `getBitmap()` alias
normalize output to sRGB by default. Pass `colorSpace` to retain the source
color space or request a different conversion:

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

Treat source normalization and bitmap output conversion as separate stages
when asserting exact pixel values.

## Named native images

### SF Symbols

Electron 40.0.0 lets `nativeImage.createFromNamedImage()` accept SF Symbol
names. This support is also available in Electron 39.

### HSL options object

Electron 42.0.0 deprecates passing an `hslShift` array directly as the second
argument to `nativeImage.createFromNamedImage()`. Pass an options object:

```js
nativeImage.createFromNamedImage(imageName, {
  hslShift: [0, 1, -1],
});
```

## CSS corner smoothing

The custom `-electron-corner-smoothing` property is available in Electron
37.0.0 and originally landed in Electron 36. It turns rounded corners into a
continuous, squircle-like curve. It accepts `0%` through `100%`; `system-ui`
resolves to 60% on macOS and 0% elsewhere.

```css
.box {
  border-radius: 24px;
  -electron-corner-smoothing: system-ui;
}
```

The smoothing affects borders, outlines, and shadows as well as the filled
corner.

## Desktop-capture audio

### macOS permission description

On macOS 14.2 and later, Electron 39.0.0 applications using `desktopCapturer`
must define `NSAudioCaptureUsageDescription` in `Info.plist`. Without it, the
new CoreAudio Tap path produces a dead audio stream without an error or warning.

An application can temporarily retain the older behavior by disabling the
feature before startup:

```js
app.commandLine.appendSwitch(
  'disable-features',
  'MacCatapLoopbackAudioForScreenShare',
);
```

### Restricting the application's own audio

In the 41.10.5-43.4.1 batch, Electron 43.4.0 honors
`getDisplayMedia({ audio: { restrictOwnAudio: true } })` for requests handled by
`setDisplayMediaRequestHandler()`. Loopback audio then excludes the
application's own playback instead of silently including it.
