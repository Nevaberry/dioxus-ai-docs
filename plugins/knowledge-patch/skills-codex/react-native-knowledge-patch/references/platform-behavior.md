# Platform behavior

## Android system UI and target behavior

### Edge-to-edge layouts

With `targetSdk` 35, Android 15 forces edge-to-edge rendering. Layouts must
account for system-bar insets; `react-native-safe-area-context` already handles
this case. React Native 0.81 targets Android 16/API 36, where edge-to-edge is
mandatory. The `edgeToEdgeEnabled` Gradle property can extend the behavior to
earlier Android versions.

Android 16 also enables predictive back by default. Migrate custom native
`onBackPressed()` handling or use a temporary opt-out during transition.

### Navigation-bar contrast

React Native 0.86.0 respects the Android theme's
`enforceNavigationBarContrast` attribute when configuring the navigation bar.
Check the theme before trying to override unexpected contrast in JavaScript.

### Status bars in modal windows

In 0.86.0, `StatusBar` configuration also applies to Android modal windows.
Recheck modal-specific workarounds that separately configured the status bar.

## Android hardware input

From 0.86.0, `BackHandler` `hardwareBackPress` callbacks receive an event
object. Its `timeStamp` comes from the native event. Return the usual boolean to
indicate whether the callback handled the back action.

```js
BackHandler.addEventListener('hardwareBackPress', event => {
  console.log(event.timeStamp);
  return false;
});
```

Android also channels play/pause hardware events in 0.86.0. React Native 0.84
adds Android `onKeyDown` and `onKeyUp` handling for hardware keyboards and TV
remotes.

## Android native values for input components

`Pressable.android_ripple.color` accepts `PlatformColor` in 0.86.0:

```jsx
<Pressable
  android_ripple={{color: PlatformColor('?attr/colorAccent')}}
/>
```

`TextInput.autoComplete` also gains an expanded set of Android autofill hints
backed by `androidx.autofill` 1.3.0. Prefer the platform hint matching the field
rather than maintaining a custom autofill bridge.

React Native 0.84 additionally permits `PlatformColor` values in
animated interpolations and output ranges.

## Android native window lifecycle

Native modules can implement `ExtraWindowEventListener` in 0.86.0 to receive
creation and destruction events for extra windows such as modal dialogs. Use it
when module state must follow the window rather than only the host Activity.

## Image dimension semantics

On iOS under the Old Architecture, the `Image` load event reports pixel
dimensions from 0.78 instead of logical dimensions.

On Android, `Image.getSize` and `Image.getSizeWithHeaders` return true source
dimensions from 0.86.0 rather than Fresco's downsampled dimensions. Revisit
logic that compares these values across platforms or release versions.

## Android memory-page compatibility

React Native 0.77 makes the framework compatible with devices that use 16 KB
memory pages. This does not certify an app's other native code or dependencies;
audit every bundled native binary.
