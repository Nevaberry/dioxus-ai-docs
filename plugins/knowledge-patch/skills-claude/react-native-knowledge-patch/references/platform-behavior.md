# Platform behavior

## Android hardware events

In 0.86.0, `BackHandler` `hardwareBackPress` callbacks receive an event object
whose `timeStamp` comes from the native event. Android also channels play and
pause hardware events.

```js
BackHandler.addEventListener('hardwareBackPress', event => {
  console.log(event.timeStamp);
  return false;
});
```

React Native 0.84 also adds Android `onKeyDown` and `onKeyUp` handling for
hardware keyboards and TV remotes. That addition belongs to batch
`0.82-0.85`.

## Platform-native input values

In 0.86.0, `Pressable.android_ripple.color` accepts `PlatformColor`, and
`TextInput.autoComplete` supports a wider set of Android autofill hints backed
by `androidx.autofill` 1.3.0.

```jsx
<Pressable android_ripple={{color: PlatformColor('?attr/colorAccent')}} />
```

React Native 0.84 additionally permits `PlatformColor` values in animated
interpolations and output ranges.

## Image formats and dimensions

React Native 0.84 adds HEIC and HEIF image support.

On iOS under the Old Architecture, the 0.78 `Image` load event changes its size
information from logical dimensions to pixel dimensions. Adjust consumers that
persist or compare those values. This behavior belongs to batch `0.77-0.81`.

On Android in 0.86.0, `Image.getSize` and `Image.getSizeWithHeaders` return the
true source dimensions rather than Fresco's downsampled dimensions.

## Android navigation-bar contrast

React Native 0.86.0 respects the Android theme's
`enforceNavigationBarContrast` attribute when it configures the navigation
bar.

## Status bars in modal windows

From 0.86.0, Android `StatusBar` configuration also applies to modal windows.
