# Signal Forms and Forms Changes

## Create a field tree (`21-signal-forms`)

`form()` from `@angular/forms/signals` turns a writable model signal into a callable, type-safe field tree. `FormField` binds a field to a native control and synchronizes the control, field state, and model in both directions.

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

Nested objects use property paths and arrays use indices. Calling a field returns its state; for example, `loginForm.email().value.set('a@b.example')` updates both the original model and its bound control.

Signal Forms was experimental in v21 and is stable in v22 (`22.0.0`).

## Shape the model for fields

Every bindable field must exist initially. An optional or `undefined` property means no field exists; use `''` for an empty text control. A `null` complex object has no navigable children, so use a static object with empty leaf values.

Variable-length arrays are supported. Dynamically shaped values can instead be treated atomically by a custom control. Array object items have stable field identities so interaction and validation state survives reordering; track by field identity, not value or index:

```html
@for (emailField of emailsForm.emails; track emailField) {
  <input [formField]="emailField" />
}
```

## Read field and aggregate state

`FieldState` exposes:

- writable `value`;
- `valid()`, `invalid()`, `errors()`, and `pending()`;
- `touched()` and `dirty()`; and
- `disabled()`, `hidden()`, and `readonly()`.

A validation error includes `kind`, an optional `message`, and a `fieldTree` reference. During asynchronous validation both `valid()` and `invalid()` may be false. `dirty()` records user modification and stays true even if the value later returns to its original value.

Calling an object field or root form returns the same interface aggregated over interactive descendants. One invalid, pending, touched, or dirty child propagates that state to ancestors.

## Declare availability rules

Schemas apply `disabled()`, `hidden()`, and `readonly()` with reactive conditions. Read the current field through `value()` and another field through `valueOf(path)`:

```ts
orderForm = form(orderModel, path => {
  disabled(path.couponCode, ({valueOf}) => valueOf(path.total) < 50);
  hidden(path.shippingAddress, ({valueOf}) => !valueOf(path.requiresShipping));
  readonly(path.orderId);
});
```

`FormField` reflects disabled and readonly onto native controls. Hidden state must be rendered explicitly with `@if`. All three states make the field non-interactive and exclude it from ancestor validation, touched, and dirty aggregation without clearing its value.

## Built-in and custom validation

The schema callback runs once and attaches reactive rules to `SchemaPathTree` paths. Built-ins include `required`, `email`, `min`, `max`, `minLength`, `maxLength`, and `pattern`. Options support custom messages and conditional `when`; numeric limits can be reactive functions.

`required` treats `null` and `''` as empty, but not `[]`; use `minLength` for a non-empty array.

Use `applyEach()` for array items and `validate()` for custom or cross-field validation:

```ts
orderForm = form(orderModel, path => {
  applyEach(path.items, item => {
    required(item.name);
    min(item.quantity, 1);
  });

  validate(path.confirmEmail, ({value, valueOf}) =>
    value() === valueOf(path.email)
      ? null
      : {kind: 'emailMismatch', message: 'Email addresses must match'},
  );
});
```

A custom validator returns `{kind, message?}` or `null`/`undefined`. Its context supplies `value()`, `valueOf(path)`, state accessors, field-tree accessors, and reactive path keys.

`validateTree()` validates a whole subtree and can place an error on a chosen descendant through its `fieldTree`. All synchronous rules run on each interactive value change; asynchronous rules begin only when every synchronous rule passes.

## HTTP and Standard Schema validation

`validateHttp()` builds an asynchronous validator from reactive `request`, `onSuccess`, and `onError` callbacks. It sets `pending()` while the request runs and maps success or failure to an error or `null`.

`validateStandardSchema()` accepts Standard Schema-compatible validators such as Zod or Valibot, including a function returning a reactive schema.

```ts
form(model, path => {
  validateHttp(path.username, {
    request: ({value}) => `/api/users/available?name=${value()}`,
    onSuccess: (r: {taken: boolean}) =>
      r.taken ? {kind: 'usernameTaken', message: 'Already taken'} : null,
    onError: () => ({kind: 'networkError', message: 'Could not validate'}),
  });

  validateStandardSchema(path.profile, () => profileSchema());
});
```

In v22, `reloadValidation` manually reruns asynchronous validation; `validateAsync` and `validateHttp` accept `debounce`, and `FieldState.getError()` retrieves a matching error (`22.0.0`).

## Submit and reset

`FormRoot` binds a field tree to `<form [formRoot]="myForm">`, prevents native submission, adds `novalidate`, and invokes the configured submission action. `submit()` first marks every field touched and runs only while the form is valid. Call it directly when there is no `FormRoot` or to override the configured action.

```ts
registrationForm = form(
  registrationModel,
  path => required(path.email),
  {submission: {action: async () => api.register(registrationModel())}},
);

submit(registrationForm, {
  action: async () => save(registrationModel()),
});

registrationForm().reset({email: ''});
```

Root `reset()` clears touched and dirty state; passing a value also replaces the form model. In v22, `FormRoot` may be used without submission options.

## Custom controls and UI integration

Signal Forms can bind signal-based custom components without implementing `ControlValueAccessor` (`21.0.0`). In v22, `ngNoCva` explicitly opts a control out of `ControlValueAccessor` integration (`22.0.0`).

Stable Signal Forms integrates with Angular Material and Angular Aria. Use the supplied integrations rather than adapting every Material or Aria control manually.

## Radio value synchronization

Radio inputs remain synchronized when their bound values change (`22.1.2`). A group whose option values are updated now keeps the form control and checked state aligned; remove workarounds that manually re-check radios after a value update.
