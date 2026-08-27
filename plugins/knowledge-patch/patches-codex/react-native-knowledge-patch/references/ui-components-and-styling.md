# UI components and styling

## New Architecture CSS properties

React Native 0.77 adds the following New Architecture-only styling features:

- `display: 'contents'`
- `boxSizing: 'content-box'`
- `mixBlendMode` with `isolation: 'isolate'`
- `outlineWidth`, `outlineStyle`, `outlineSpread`, and `outlineColor`

`boxSizing` still defaults to `border-box`. Outlines render outside the border
box and do not affect layout.

```jsx
<View style={{isolation: 'isolate'}}>
  <View style={{boxSizing: 'content-box', mixBlendMode: 'multiply'}} />
</View>
```

React Native 0.86.0 also accepts `plus-lighter` for `mixBlendMode`:

```jsx
<View style={{mixBlendMode: 'plus-lighter'}} />
```

## CSS string parsing

From 0.79, lengths in `box-shadow` and `filter` strings require units. Change a
value such as `1 1 black` to `1px 1px black`. Comma-separated `hwb()` colors
are no longer accepted; use `hwb(0 0% 100%)`, not
`hwb(0, 0%, 100%)`.

## `Modal` layout and styling

In 0.86.0, `Modal` forwards its `style` prop to the inner container `View`.
The `transparent` and `backdropColor` props retain precedence, so account for
them when a forwarded background style appears not to apply.

## Native component refs and DOM APIs

From 0.82, native component refs implement a subset of DOM node APIs while
retaining legacy methods such as `measure`. Element refs include traversal and
measurement APIs such as `parentNode`, `children`, `getBoundingClientRect()`,
and `ownerDocument`; text and document nodes are exposed too.

```jsx
const element = ref.current;
const bounds = element.getBoundingClientRect();
const other = element.ownerDocument.getElementById('some-view');
```

Treat this as a supported subset, not a browser-complete DOM implementation.

## React Activity behavior

React Native 0.83 brings React 19.2's `<Activity>` and `useEffectEvent` APIs. A
hidden Activity preserves state while hiding its children, unmounting effects,
and deferring updates. From 0.85, a `Pressable` inside a hidden Activity keeps
its event listeners while hidden.

## Images

### Android XML drawables

Android `Image` can load vector or shape drawable XML through a static
`require` or import. XML resources are available only at build time, cannot be
loaded from the network, require explicit dimensions, and support only
whole-image size or tint customization at runtime.

```jsx
<Image
  source={require('./img/my_icon.xml')}
  style={{width: 40, height: 40}}
/>
```

### Source dimensions

On iOS under the Old Architecture, the 0.78 `Image` load event changes its size
from logical dimensions to pixel dimensions. Update consumers that persist or
compare those values.

In 0.86.0, Android `Image.getSize` and `Image.getSizeWithHeaders` return true
source dimensions instead of Fresco's downsampled dimensions. Code that used
the older, downsampled values for layout or caching must adjust.

### HEIC and HEIF

React Native 0.84 adds HEIC and HEIF image support.

## Animations

Starting with 0.85.1 on the experimental release channel, the
Shared Animation Backend allows `Animated` to use the native driver for layout properties,
including Flexbox and position properties. It also backs Reanimated. This is an
experimental integration surface; pin the release channel and version.

```jsx
const width = useAnimatedValue(100);
Animated.timing(width, {
  toValue: 300,
  duration: 500,
  useNativeDriver: true,
}).start();

<Animated.View style={{width}} />
```

## Accessibility behavior

In 0.84, a `Text` with `onPress` or `onLongPress` automatically receives
`accessibilityRole="link"`. Audit explicitly assigned roles if this changes the
announced semantics.

In 0.85, `AccessibilityInfo.setAccessibilityFocus` is deprecated. Use
`AccessibilityInfo.sendAccessibilityEvent` instead.

## Touches and transforms

From 0.86.0, a view with a non-invertible transform, such as `scaleX: 0` or
`scaleY: 0`, no longer receives touches on Android or iOS. Do not use a zero
scale for an invisible element that must remain an input target.
