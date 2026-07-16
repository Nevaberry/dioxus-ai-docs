# Signal Forms and Forms Changes

Batch attribution: 21-signal-forms, 21.0.0, 22.0.0.

## Create a typed field tree

Signal Forms arrived experimentally in Angular 21 under `@angular/forms/signals` and is stable in Angular 22. `form()` turns a writable signal into a callable, type-safe field tree. The `FormField` directive binds one field to a native control and synchronizes the control, field state, and model in both directions.

```ts
import {Component, signal} from '@angular/core';
import {form, FormField, required} from '@angular/forms/signals';

@Component({
  imports: [FormField],
  template: `<input [formField]="loginForm.email" />`,
})
export class Login {
  model = signal({email: '', password: ''});
  loginForm = form(this.model, path => required(path.email));
}
```

Nested object fields use property paths; array fields use indices. Calling a field returns its state. For example, `loginForm.email().value.set('a@b.example')` updates both the original model signal and a bound control.

## Design the model shape first

Every bindable field must exist in the model initially.

- `undefined` and an optional property mean the field is absent.
- Use `''` for an empty text control.
- A `null` complex object has no navigable child fields. Prefer a stable object with empty leaf values.
- Variable-length arrays are supported.
- A dynamically shaped value can be treated atomically by a custom control.

Array object items receive stable field identities, preserving interaction and validation state across reordering. Track the field identity—not its value or index—when rendering:

```html
@for (emailField of emailsForm.emails; track emailField) {
  <input [formField]="emailField" />
}
```

## Read field and aggregate state

`FieldState` exposes:

- `value`, a writable signal;
- `valid()` and `invalid()`;
- `errors()` and, in Angular 22, `getError()`;
- `pending()`;
- `touched()` and `dirty()`;
- `disabled()`, `hidden()`, and `readonly()`.

A validation error contains `kind`, an optional `message`, and a `fieldTree` reference. During asynchronous validation, `valid()` and `invalid()` can both be `false`. `dirty()` records user modification and remains true even if the value is later restored.

Calling an object field or the root form returns the same interface aggregated over interactive descendants. One invalid, pending, touched, or dirty child propagates that state to its ancestors.

## Configure field availability

Schema rules `disabled()`, `hidden()`, and `readonly()` can use reactive conditions. Read the current field with `value()` or another field with `valueOf(path)`.

```ts
orderForm = form(orderModel, path => {
  disabled(
    path.couponCode,
    ({valueOf}) => valueOf(path.total) < 50,
  );
  hidden(
    path.shippingAddress,
    ({valueOf}) => !valueOf(path.requiresShipping),
  );
  readonly(path.orderId);
});
```

`FormField` reflects disabled and readonly state onto native controls. Hidden state does not hide markup; render it explicitly with `@if`.

All three states make a field non-interactive and exclude it from ancestor validation, touched, and dirty aggregation. They do not clear its value.

## Attach schema validation

The schema callback runs once to attach reactive rules to a `SchemaPathTree`. Built-in rules include:

- `required` and `email`;
- `min` and `max`;
- `minLength` and `maxLength`;
- `pattern`.

Options can supply custom messages and conditional `when` logic. Numeric limits can come from reactive functions. `required` considers `null` and `''` empty, but not `[]`; use `minLength` to require a non-empty array.

### Validate array items and cross-field constraints

Use `applyEach()` to validate each array item. Use `validate()` for a custom or cross-field rule.

```ts
orderForm = form(orderModel, path => {
  applyEach(path.items, item => {
    required(item.name);
    min(item.quantity, 1);
  });

  validate(path.confirmEmail, ({value, valueOf}) =>
    value() === valueOf(path.email)
      ? null
      : {
          kind: 'emailMismatch',
          message: 'Email addresses must match',
        },
  );
});
```

A custom validator returns `{kind, message?}` or `null`/`undefined`. Its context includes `value()`, `valueOf(path)`, state and field-tree accessors, and reactive path keys.

`validateTree()` validates an entire subtree and can attach an error to a selected descendant by using its `fieldTree`. Every synchronous rule runs after each interactive value change. Asynchronous rules start only after all synchronous rules pass.

### Validate through HTTP or Standard Schema

`validateHttp()` builds an asynchronous validator from a reactive `request`, `onSuccess`, and `onError`. It sets `pending()` while the request runs and maps both successful responses and failures to an error or `null`.

`validateStandardSchema()` accepts a Standard Schema-compatible validator such as Zod or Valibot. It can also take a function that returns a reactive schema.

```ts
form(model, path => {
  validateHttp(path.username, {
    request: ({value}) =>
      `/api/users/available?name=${value()}`,
    onSuccess: (response: {taken: boolean}) =>
      response.taken
        ? {kind: 'usernameTaken', message: 'Already taken'}
        : null,
    onError: () => ({
      kind: 'networkError',
      message: 'Could not validate',
    }),
  });

  validateStandardSchema(
    path.profile,
    () => profileSchema(),
  );
});
```

Angular 22 adds `reloadValidation` for manually rerunning asynchronous validation and a `debounce` option for `validateAsync` and `validateHttp`.

## Submit and reset

`FormRoot` binds a field tree to `<form [formRoot]="myForm">`. It prevents native submission, adds `novalidate`, and invokes the form's configured submission action. Angular 22 allows `FormRoot` without submission options.

`submit()` first marks every field touched, then runs the action only when the form is valid. Call it directly to submit without `FormRoot` or to override the form's configured action.

```ts
registrationForm = form(
  registrationModel,
  path => required(path.email),
  {
    submission: {
      action: async () => api.register(registrationModel()),
    },
  },
);

submit(registrationForm, {
  action: async () => save(registrationModel()),
});

registrationForm().reset({email: ''});
```

Calling the root state's `reset()` clears touched and dirty state. Passing a value also replaces the form model.

## Custom controls and UI integration

Signal Forms bind custom components through signal-based APIs without requiring a `ControlValueAccessor`. Angular 22 adds `ngNoCva` for a control that must explicitly opt out of `ControlValueAccessor` integration.

Angular 22 also integrates Signal Forms with Angular Material and Angular Aria. Use their supported adapters rather than manually mirroring state between a field tree and those component systems.

## Zoneless Reactive Forms note

This Signal Forms model is signal-driven, but classic Reactive Forms still do not notify zoneless change detection when operations such as `setValue()`, `patchValue()`, or `FormArray.push()` run. If a template consumes classic form state, bridge a form Observable to `markForCheck()` or a template-read signal. See [Core Reactivity](core-reactivity.md).
