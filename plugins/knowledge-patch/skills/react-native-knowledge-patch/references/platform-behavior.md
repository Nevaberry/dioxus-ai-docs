# Platform behavior

## Android hardware events

In 0.86, `BackHandler` `hardwareBackPress` callbacks receive an event object.
Its `timeStamp` originates in the native event.

```js
BackHandler.addEventListener('hardwareBackPress', event => {
  console.log(event.timeStamp);
  return false;
});
```

Android also channels hardware play/pause events. Do not assume every hardware
event has the old argument-free callback shape.

React Native 0.84 adds Android `onKeyDown` and `onKeyUp` handling for hardware
keyboards and TV remotes.

## Platform-native input values

In 0.86, `Pressable.android_ripple.color` accepts `PlatformColor`:

```jsx
<Pressable
  android_ripple={{color: PlatformColor('?attr/colorAccent')}}
/>
```

`TextInput.autoComplete` also supports an expanded collection of Android
autofill hints backed by `androidx.autofill` 1.3.0. Prefer the React Native hint
values over setting native autofill properties ad hoc.

## Navigation and status bars

React Native 0.86 respects the Android theme's
`enforceNavigationBarContrast` attribute when configuring the navigation bar.
Check the theme value before compensating in JavaScript for contrast behavior.

`StatusBar` configuration now also applies to modal windows on Android. Remove
modal-specific workarounds that would double-apply or fight the shared status
bar configuration.

## Android image source dimensions

In 0.86, `Image.getSize` and `Image.getSizeWithHeaders` return the true source
dimensions on Android instead of Fresco's downsampled dimensions. Audit caches,
aspect-ratio calculations, snapshot expectations, and comparisons that encoded
the downsampled result.

For Android XML drawables and the Old Architecture iOS load-event dimension
change, see [ui-components-and-styling.md](ui-components-and-styling.md).
