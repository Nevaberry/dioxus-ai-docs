# Types and Standard Libraries

Batch attribution: `5.9.0`, `6.0.0`, `7.0-native-port`.

## Contents

- [Repair `ArrayBuffer` and typed-array relationships](#repair-arraybuffer-and-typed-array-relationships)
- [Stabilize generic inference explicitly](#stabilize-generic-inference-explicitly)
- [Let methods that ignore `this` contribute earlier](#let-methods-that-ignore-this-contribute-earlier)
- [Target the ES2025 library surface](#target-the-es2025-library-surface)
- [Select built-in `Temporal` declarations](#select-built-in-temporal-declarations)
- [Use `Map` and `WeakMap` upsert methods](#use-map-and-weakmap-upsert-methods)
- [Rely on iterable DOM declarations from `dom`](#rely-on-iterable-dom-declarations-from-dom)
- [Preserve complete Unicode code points in template inference](#preserve-complete-unicode-code-points-in-template-inference)

## Repair `ArrayBuffer` and typed-array relationships

`ArrayBuffer` is no longer a supertype of several typed arrays, including
Node.js `Buffer` subtypes. Existing code can therefore report new errors around
`ArrayBufferLike`, `BufferSource`, or `Uint8Array<ArrayBufferLike>`.

For Node.js `Buffer` failures, update `@types/node` first. Otherwise expose the
actual backing buffer type or pass the backing buffer when an API specifically
requires `ArrayBuffer`:

```ts
declare function consume(buffer: ArrayBuffer): void;

const data: Uint8Array<ArrayBuffer> = new Uint8Array([0, 1, 2]);
consume(data.buffer);
```

Do not erase the distinction with a broad cast when the API can accept a typed
array or `ArrayBufferLike` directly.

## Stabilize generic inference explicitly

Generic type-argument inference now prevents some type variables from escaping
their intended scope. Calls that previously inferred through that leak can gain
errors or receive a different inferred type. Add explicit type arguments at the
call site when the intended relationship is unambiguous:

```ts
declare function choose<T>(factory: () => T, use: (value: T) => void): void;

choose<number>(() => 1, value => value.toFixed());
```

Prefer a local annotation or explicit type argument over widening the generic
constraint solely to recover an old inference artifact.

## Let methods that ignore `this` contribute earlier

A method with unannotated parameters is no longer treated as contextually
sensitive merely because it has an implicit `this`. If its body does not use
`this`, it can participate in generic inference earlier, even when a consumer
method appears before the producer:

```ts
declare function callIt<T>(obj: {
  produce: (x: number) => T;
  consume: (y: T) => void;
}): void;

callIt({
  consume(y) {
    y.toFixed();
  },
  produce(x: number) {
    return x * 2;
  }
});
```

Here `y` is inferred as `number`. If a method really depends on `this`, annotate
that relationship instead of relying on the earlier inference path.

## Target the ES2025 library surface

Both `target` and `lib` accept `es2025`. The target adds no new syntax
transformations, while the library declares newer APIs such as `RegExp.escape`.
It also moves `Promise.try`, iterator methods, and set methods out of `esnext`
and into the stable ES2025 library group.

```json
{
  "compilerOptions": {
    "target": "es2025"
  }
}
```

As with any library declaration, ensure the runtime or a polyfill supplies the
APIs the program calls.

## Select built-in `Temporal` declarations

The compiler supplies `Temporal` declarations through any of these choices:

- `target: "esnext"`;
- `lib: ["esnext"]`; or
- the granular `lib: ["esnext.temporal"]` entry alongside other required
  libraries.

```ts
const tomorrow = Temporal.Now.instant().add({ hours: 24 });
```

## Use `Map` and `WeakMap` upsert methods

The `esnext` library declares `getOrInsert` and `getOrInsertComputed` on both
`Map` and `WeakMap`. The computed form invokes its callback only when the key is
missing and passes that missing key to the callback:

```ts
const lengths = new Map<string, number>();
const length = lengths.getOrInsertComputed("answer", key => key.length);
```

Use the non-computed form when the fallback value is already available; use the
computed form when creating it is expensive or depends on the key.

## Rely on iterable DOM declarations from `dom`

`lib.dom.d.ts` now includes declarations formerly split across `dom.iterable`
and `dom.asynciterable`. A project can iterate DOM collections with only
`lib: ["dom"]`. The two older library names remain accepted for compatibility
but point to empty files, so they no longer add declarations.

## Preserve complete Unicode code points in template inference

When an empty placeholder is inferred through a template-literal type, the
native checker consumes a full Unicode code point rather than one UTF-16 code
unit. Supplementary characters such as emoji are therefore not split into
surrogate halves:

```ts
type Head<S extends string> = S extends `${infer H}${string}` ? H : never;
type Emoji = Head<"😀abc">; // "😀"
```

Review type-level string utilities whose expected output was based on UTF-16
code units, especially tests that use supplementary characters.
