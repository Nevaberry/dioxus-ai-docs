# UI components and styling

## New Architecture CSS properties

React Native 0.77 adds these New Architecture-only styling capabilities:

- `display: 'contents'`
- `boxSizing: 'content-box'`
- `mixBlendMode`
- `isolation: 'isolate'`
- `outlineWidth`, `outlineStyle`, `outlineSpread`, and `outlineColor`

`boxSizing` remains `border-box` by default. Outlines render outside the border
box and do not affect layout.

```jsx
<View style={{isolation: 'isolate'}}>
  <View style={{boxSizing: 'content-box', mixBlendMode: 'multiply'}} />
</View>
```

React Native 0.86 adds `plus-lighter` as a `mixBlendMode` value:

```jsx
<View style={{mixBlendMode: 'plus-lighter'}} />
```

## Stricter CSS string syntax

React Native 0.79 rejects unitless lengths in `box-shadow` and `filter` strings.
For example, replace `1 1 black` with `1px 1px black`. It also rejects
comma-separated `hwb()` colors: use `hwb(0 0% 100%)`, not
`hwb(0, 0%, 100%)`.

## Images

On Android, `Image` can load vector or shape drawable XML through a static
`require` or import from 0.78. XML drawables are build-time resources: they
cannot be loaded from the network, require explicit dimensions, and permit only
whole-image size or tint customization at runtime.

```jsx
<Image
  source={require('./img/my_icon.xml')}
  style={{width: 40, height: 40}}
/>
```

On iOS under the Old Architecture, the 0.78 `Image` load event changes its size
values from logical dimensions to pixel dimensions. Update persisted metadata,
comparisons, and layout calculations that consumed those values.

React Native 0.84 adds HEIC/HEIF image support. Android source-size corrections
in 0.86 are documented in [platform-behavior.md](platform-behavior.md).

## `Modal` and touch behavior

In 0.86, `Modal` forwards its `style` prop to the inner container `View`.
`transparent` and `backdropColor` keep precedence over conflicting forwarded
style values.

On both Android and iOS, a view with a non-invertible transform such as
`scaleX: 0` or `scaleY: 0` no longer receives touches in 0.86. Do not use a zero
scale when an invisible element must remain interactive.

## DOM-compatible native refs

From 0.82, native component refs implement a subset of DOM node APIs while
retaining React Native methods such as `measure`. Element refs expose traversal
and measurement members including `parentNode`, `children`,
`getBoundingClientRect()`, and `ownerDocument`. Text and document nodes are also
exposed.

```jsx
const element = ref.current;
const bounds = element.getBoundingClientRect();
const other = element.ownerDocument.getElementById('some-view');
```

Code to the documented subset. A native ref is not a browser node and does not
implicitly implement every Web DOM API.

## React 19.2 APIs

React Native 0.83 adds React's `<Activity>` and `useEffectEvent`. A hidden
`Activity` preserves child state, hides its output, unmounts effects, and defers
updates. From React Native 0.85, a `Pressable` inside a hidden Activity retains
its event listeners while hidden.

Account for effect teardown separately from preserved component state when
placing native resources or subscriptions inside an Activity.

## Shared animation backend

Starting with 0.85.1 on the experimental release channel, the Shared Animation
Backend lets `Animated` use the native driver for layout properties, including
Flexbox and position properties. The backend also supports Reanimated.

```jsx
const width = useAnimatedValue(100);
Animated.timing(width, {
  toValue: 300,
  duration: 500,
  useNativeDriver: true,
}).start();

<Animated.View style={{width}} />
```

This is experimental channel behavior. Pin the release and verify the backend
before assuming native-driver support for layout properties.

React Native 0.84 also permits `PlatformColor` values in animated
interpolations and output ranges.

## Interactive text accessibility

In 0.84, a `Text` with `onPress` or `onLongPress` automatically receives
`accessibilityRole="link"`. Set an explicit role when the interaction is not
semantically a link.

In 0.85, `AccessibilityInfo.setAccessibilityFocus` is deprecated. Use
`AccessibilityInfo.sendAccessibilityEvent` and select the appropriate event.
