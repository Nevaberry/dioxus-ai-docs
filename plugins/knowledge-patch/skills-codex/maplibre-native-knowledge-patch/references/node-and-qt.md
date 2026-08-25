# Node and Qt Bindings

Use this reference for Node runtime compatibility, offscreen rendering,
resource hooks and logging, plus Qt 3 linking, QML, deployment, and Android
multi-ABI selection.

## Node runtime and renderer compatibility

The `node-6.1.0` line requires Node.js 18 or newer because the package moved
back to `@mapbox/node-pre-gyp`; Node.js 16 is unsupported. Linux and Windows
also use the drawable renderer from this line, with the legacy renderer
removed.

The stable 6.4.1 binding supports Node.js 20, 22, and 24. Node.js 26 support
belongs to the 6.5 prerelease line and must not be assumed for the stable
package.

## Node map data and sprite metadata

Node 6.1 supports PMTiles-backed map data. Sprites can expose `textFitWidth`
and `textFitHeight`, making text-fit metadata available to Node rendering.

## Node rendering and buffer lifetime

`Map.render` accepts these optional values:

| Option | Meaning | Default |
| --- | --- | --- |
| `zoom` | zoom level | `0` |
| `width`, `height` | output pixels | `512`, `512` |
| `center` | `[longitude, latitude]` | `[0, 0]` |
| `bearing` | counter-clockwise from north | `0` |
| `pitch` | camera pitch | `0` |
| `classes` | style classes | none |

The callback receives a raw four-channel pixel buffer asynchronously.
`release()` permanently disables later renders, but calling it within the
render callback is safe because the returned buffer remains retained for that
callback.

```js
const mbgl = require('@maplibre/maplibre-gl-native');
const map = new mbgl.Map();

map.load(require('./style.json'));
map.render({ width: 256, height: 256, center: [24.94, 60.17], zoom: 10 },
  (error, rgba) => {
    if (error) throw error;
    map.release();
    // rgba contains raw four-channel pixel data.
  });
```

## Node resource request hook

The `Map` constructor's `request({ url, kind }, callback)` hook routes every
style resource through application code. The resource kinds are:

| Kind | Code |
| --- | ---: |
| `Unknown` | 0 |
| `Style` | 1 |
| `Source` | 2 |
| `Tile` | 3 |
| `Glyphs` | 4 |
| `SpriteImage` | 5 |
| `SpriteJSON` | 6 |

The handler must understand every custom URL scheme used by the style. A
successful response needs uncompressed byte `data` and may include `modified`
and `expires` dates plus an `etag`. Call the callback with no arguments for a
no-content result. Constructor `ratio` controls high-density rendering scale.

```js
const fs = require('node:fs');
const path = require('node:path');
const mbgl = require('@maplibre/maplibre-gl-native');

const map = new mbgl.Map({
  request({ url }, callback) {
    fs.readFile(path.join('base/path', url), (error, data) => {
      if (error) return callback(error);
      callback(null, { data });
    });
  },
  ratio: 2
});
```

## Node log events

The imported module is an `EventEmitter`. Its `message` events can contain
`class`, `severity`, `code`, and `text`, exposing native style and resource
failures.

```js
const mbgl = require('@maplibre/maplibre-gl-native');

mbgl.on('message', (message) => {
  console.error(message.class, message.severity, message.code, message.text);
});
```

## Qt 3 libraries and CMake targets

Qt 3 places the API in the `QMapLibre` namespace and splits installation into
`QMapLibre`, `QMapLibreLocation`, and `QMapLibreWidgets`. The CMake package
exposes `Core`, `Location`, and `Widgets` components with `QMapLibre::*`
targets.

The release supports static builds and use as a CMake subproject. It was built
with Qt 6.5–6.7 on all supported platforms, and with Qt 5.15.2 on macOS,
Linux, and Windows.

Find the package by setting `QMapLibre_DIR` to
`<install>/lib/cmake/QMapLibre` or adding the installation prefix to
`CMAKE_PREFIX_PATH`. A Widgets deployment must include both `QMapLibre` and
`QMapLibreWidgets` libraries.

```cmake
find_package(QMapLibre COMPONENTS Widgets REQUIRED)
target_link_libraries(MyApplication PRIVATE QMapLibre::Widgets)
```

## Qt 3 QML and deployment

QML applications use `import MapLibre 3.0` and configure styles through
`maplibre.map.styles`. Deploy `plugins/geoservices` and `qml/MapLibre`
together with the core and Location libraries.

Linking the Location component exposes `qmaplibre_location_setup_plugins`,
which installs both plugin trees:

```cmake
find_package(QMapLibre COMPONENTS Location REQUIRED)
target_link_libraries(MyApplication PRIVATE QMapLibre::Location)
qmaplibre_location_setup_plugins(MyApplication)
```

For undeployed development runs, set `QML_IMPORT_PATH=<install>/qml` and
`QT_PLUGIN_PATH=<install>/plugins` if Qt cannot find them. Set
`QSG_RHI_BACKEND=opengl` to force the Qt 3 renderer.

## Qt Android multi-ABI packages

For a multi-ABI Android build, select the ABI-specific CMake package beneath
one `QMapLibre_Android_DIR`; do not reuse another architecture's
`QMapLibre_DIR`.

```cmake
if(ANDROID AND DEFINED ENV{QMapLibre_Android_DIR})
    set(QMapLibre_DIR
        "$ENV{QMapLibre_Android_DIR}/${ANDROID_ABI}/lib/cmake/QMapLibre")
endif()
```

## Empty Qt styles

Qt 3 permits constructing a `Style` with an empty URL. A placeholder URL is
not required solely for construction.
