# Signal Forms and Forms Changes

## Field trees and binding

Signal Forms arrived experimentally in `@angular/forms/signals`. `form()` turns
a writable model signal into a callable, type-safe field tree. `FormField` binds
a tree field to a native control and synchronizes the control, field state, and
model in both directions. Nested objects use property paths and arrays use
indices. Calling a field returns its state; setting that state's `value` updates
the model and bound control. (`21-signal-forms`)

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

Every bindable field must exist in the initial model. An optional property or
`undefined` means no field exists; text controls should use `''`, and a `null`
complex object has no children. Prefer static objects with empty leaf values.
Variable-length arrays are supported, as are dynamic values treated atomically
by a custom control. (`21-signal-forms`)

Array object items have stable field identities, preserving interaction and
validation state through reordering. Track by field identity, not value or
index. (`21-signal-forms`)

```html
@for (emailField of emailsForm.emails; track emailField) {
  <input [formField]="emailField" />
}
```

Signal Forms can bind custom components through signal-based APIs without a
`ControlValueAccessor` implementation (`21.0.0`).

## Field and aggregate state

`FieldState` exposes writable `value` plus `valid()`, `invalid()`, `errors()`,
`pending()`, `touched()`, `dirty()`, `disabled()`, `hidden()`, and `readonly()`.
An error contains `kind`, optional `message`, and a `fieldTree` reference. During
asynchronous validation both `valid()` and `invalid()` can be false. Once user
modification makes `dirty()` true, changing back to the original value does not
clear it. (`21-signal-forms`)

Object fields and the root form aggregate the same state over interactive
descendants: one invalid, pending, touched, or dirty child propagates upward.
(`21-signal-forms`)

## Disabled, hidden, and readonly rules

Schemas can apply reactive `disabled()`, `hidden()`, and `readonly()` rules. A
condition can read the current field through `value()` or another path through
`valueOf(path)`. `FormField` reflects disabled and readonly to a native control;
render hidden state explicitly with `@if`. All three states make a field
non-interactive and exclude it from ancestor validation, touched, and dirty
state without clearing its value. (`21-signal-forms`)

```ts
orderForm = form(orderModel, path => {
  disabled(path.couponCode, ({valueOf}) => valueOf(path.total) < 50);
  hidden(path.shippingAddress, ({valueOf}) => !valueOf(path.requiresShipping));
  readonly(path.orderId);
});
```

## Synchronous validation

The schema callback runs once and attaches reactive rules to `SchemaPathTree`
paths. Built-ins include `required`, `email`, `min`, `max`, `minLength`,
`maxLength`, and `pattern`. Options support custom messages and conditional
`when` logic; numeric limits may be reactive functions. `required` considers
`null` and `''` empty, but not `[]`; use `minLength` for a nonempty array.
(`21-signal-forms`)

Use `applyEach()` for every array item and `validate()` for a custom or
cross-field rule. A custom validator returns `{kind, message?}` or
`null`/`undefined`; its context includes `value()`, `valueOf(path)`, state and
field-tree accessors, and reactive path keys. (`21-signal-forms`)

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

`validateTree()` validates an entire subtree and can attach its error to a
chosen descendant with `fieldTree`. All synchronous rules run on each
interactive value change. Asynchronous validation starts only after every
synchronous rule passes. (`21-signal-forms`)

## HTTP, asynchronous, and Standard Schema validation

`validateHttp()` builds an asynchronous validator from reactive `request`,
`onSuccess`, and `onError` callbacks. It sets `pending()` while active and maps
both responses and failures to an error or `null`. `validateStandardSchema()`
accepts Standard Schema-compatible validators such as Zod and Valibot, including
a function returning a reactive schema. (`21-signal-forms`)

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

Angular 22 adds `reloadValidation` for manually rerunning asynchronous
validation, a `debounce` option for `validateAsync` and `validateHttp`, and
`FieldState.getError()`. (`22.0.0`)

## Submission and reset

`FormRoot` binds a tree to `<form [formRoot]="myForm">`, prevents native
submission, adds `novalidate`, and invokes the configured action. `submit()`
first touches every field and runs its action only for a valid form. Call it
directly to submit without `FormRoot` or override the configured action. Root
`reset()` clears touched and dirty state; a passed value also replaces the
model. (`21-signal-forms`)

```ts
registrationForm = form(
  registrationModel,
  path => required(path.email),
  {submission: {action: async () => api.register(registrationModel())}},
);

submit(registrationForm, {action: async () => save(registrationModel())});
registrationForm().reset({email: ''});
```

In Angular 22, `FormRoot` may be used without submission options and `ngNoCva`
opts a control out of `ControlValueAccessor` integration. Signal Forms are
stable and integrate with Angular Material and Angular Aria. (`22.0.0`)

## Radio value synchronization

Radio inputs stay synchronized when their bound values change, keeping a radio
group's control and checked state aligned as option values update (`22.1.2`).
