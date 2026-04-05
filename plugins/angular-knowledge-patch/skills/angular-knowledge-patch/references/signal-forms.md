# Signal Forms (experimental, v21+)

New forms library in `@angular/forms/signals`. Schema-based validation, auto two-way binding, full type safety. No `ControlValueAccessor` needed for custom controls.

## Full example

```typescript
import {
  form,
  FormField,
  required,
  email,
  submit,
} from '@angular/forms/signals';

@Component({
  imports: [FormField],
  template: `
    <input type="email" [formField]="loginForm.email" />
    @if (loginForm.email().touched() && loginForm.email().invalid()) {
      @for (error of loginForm.email().errors(); track error) {
        <p>{{ error.message }}</p>
      }
    }
    <input type="password" [formField]="loginForm.password" />
    <button [disabled]="loginForm().invalid()" (click)="onSubmit($event)">
      Login
    </button>
  `,
})
export class LoginComponent {
  loginModel = signal({ email: '', password: '' });
  loginForm = form(this.loginModel, (schema) => {
    required(schema.email, { message: 'Email is required' });
    email(schema.email, { message: 'Invalid email' });
    required(schema.password, { message: 'Password is required' });
  });

  onSubmit(event: Event) {
    event.preventDefault();
    submit(this.loginForm, {
      action: async () => {
        await this.authService.login(this.loginModel());
      },
    });
  }
}
```

## Key concepts

- `form(modelSignal, schemaFn?)` creates a field tree from a signal
- Access fields: `loginForm.email` (FieldTree), `loginForm.email()` (FieldState)
- FieldState properties: `.value()`, `.touched()`, `.valid()`, `.invalid()`, `.errors()`, `.dirty()`, `.pending()`
- Update fields: `loginForm.email().value.set('new')`

## Built-in validators

`required`, `email`, `min`, `max`, `minLength`, `maxLength`

### Conditional validation

```typescript
required(path, { when: ({ valueOf }) => valueOf(otherPath) });
```
