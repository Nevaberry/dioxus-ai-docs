# UI components and styling

## New Architecture CSS properties

React Native 0.77 adds `display: 'contents'`,
`boxSizing: 'content-box'`, `mixBlendMode` with `isolation: 'isolate'`, and the
`outlineWidth`, `outlineStyle`, `outlineSpread`, and `outlineColor` properties.
They require the New Architecture. `boxSizing` remains `border-box` by default;
outlines render outside the border box and do not affect layout.

```jsx
<View style={{isolation: 'isolate'}}>
  <View style={{boxSizing: 'content-box', mixBlendMode: 'multiply'}} />
</View>
```

React Native 0.86.0 adds `plus-lighter` as a `mixBlendMode` value:

```jsx
<View style={{mixBlendMode: 'plus-lighter'}} />
```

## Stricter CSS string syntax

React Native 0.79 rejects unitless lengths in `box-shadow` and `filter`.
Change values such as `1 1 black` to `1px 1px black`. It also rejects
comma-separated `hwb()` colors: use `hwb(0 0% 100%)`, not
`hwb(0, 0%, 100%)`. These changes are in batch `0.77-0.81`.

## Android XML drawables

Android `Image` can load vector or shape drawable XML through a static
`require` or import from 0.78. XML resources are build-time-only, cannot be
loaded from the network, require explicit dimensions, and permit only
whole-image size or tint customization at runtime.

```jsx
<Image source={require('./img/my_icon.xml')} style={{width: 40, height: 40}} />
```

## Modal styling

In 0.86.0, `Modal` forwards its `style` prop to the inner container `View`.
The `transparent` and `backdropColor` props retain precedence over that style.

## DOM-compatible native refs

From 0.82, native component refs expose a subset of DOM node APIs while
retaining legacy methods such as `measure`. Element refs support traversal and
measurement through APIs such as `parentNode`, `children`,
`getBoundingClientRect()`, and `ownerDocument`; text and document nodes are
also exposed.

```jsx
const element = ref.current;
const bounds = element.getBoundingClientRect();
const other = element.ownerDocument.getElementById('some-view');
```

This is a DOM-compatible subset, not the complete browser DOM.

## React 19.2 APIs

React Native 0.83 adds React's `<Activity>` and `useEffectEvent`. A hidden
Activity preserves state while hiding children, unmounting effects, and
deferring updates. From 0.85, a `Pressable` inside a hidden Activity retains
its event listeners. These details are from batch `0.82-0.85`.

## Experimental shared animation backend

Starting with 0.85.1 on the experimental release channel, the Shared Animation
Backend lets `Animated` use the native driver for layout properties, including
Flexbox and position properties; it also backs Reanimated. Pin the release
channel because this is experimental.

```jsx
const width = useAnimatedValue(100);
Animated.timing(width, {
  toValue: 300,
  duration: 500,
  useNativeDriver: true,
}).start();
<Animated.View style={{width}} />
```

## Interactive text accessibility

In 0.84, a `Text` with `onPress` or `onLongPress` automatically receives
`accessibilityRole="link"`. In 0.85,
`AccessibilityInfo.setAccessibilityFocus` is deprecated; use
`AccessibilityInfo.sendAccessibilityEvent`.

## Non-invertible transforms and touch handling

From 0.86.0 on Android and iOS, a view with a non-invertible transform such as
`scaleX: 0` or `scaleY: 0` no longer receives touches.
