# Sessions and Framework Integrations

## Contents

- [Session lifecycle](#session-lifecycle)
- [Qwik](#qwik)
- [SvelteKit](#sveltekit)
- [Express](#express)

## Session lifecycle

### Prevent session response caching

GET requests to the session endpoint automatically receive cache-prevention headers. Consume those responses directly; do not add a separate cache-control wrapper merely to obtain fresh session state.

### Clean up expired database sessions

Whenever Auth.js reads a database-backed `Session`, it checks `expires`. If the row is already expired, Auth.js deletes it as part of that read.

Do not depend on expired session rows remaining available after access. Use separate audit storage if historical session records are required.

## Qwik

### Read and protect on the server

The integration prepares the session automatically. Read it from `event.sharedMap` in server code:

```ts
export const onRequest: RequestHandler = (event) => {
  const session = event.sharedMap.get("session")
  if (!session || new Date(session.expires) < new Date()) {
    throw event.redirect(302, "/")
  }
}
```

Use `useSession()` in client code.

### Sign in and sign out

`useSignIn()` and `useSignOut()` return actions. Bind either action to a server-side `<Form>` or call its `.submit()` method from the client.

For sign-in, submit `providerId` and `options.redirectTo`:

```tsx
const signIn = useSignIn()

<Form action={signIn}>
  <input type="hidden" name="providerId" value="github" />
  <input type="hidden" name="options.redirectTo" value="/dashboard" />
  <button>Sign in</button>
</Form>
```

For sign-out, submit `redirectTo` rather than `options.redirectTo`.

## SvelteKit

### Install and read the server session

The Auth.js `handle` installs `event.locals.auth()`. Call it from page or layout server loads and from `+server.ts` endpoints.

Return the session from a load function to expose it through page data:

```ts
export const load: PageServerLoad = async (event) => {
  const session = await event.locals.auth()
  if (!session?.user?.userId) redirect(303, "/login")
  return { session }
}
```

### Wire authentication form actions

The server-rendered `SignIn` and `SignOut` components from `@auth/sveltekit/components` require matching default form actions at `/signin` and `/signout`.

```ts
// src/routes/signin/+page.server.ts
export const actions: Actions = { default: signIn }

// src/routes/signout/+page.server.ts
export const actions: Actions = { default: signOut }
```

If the routes differ, pass `signInPage` and `signOutPage` to the components. For purely client-side controls, import the corresponding handlers from `@auth/sveltekit/client`.

## Express

Use the integration primitives in application-owned middleware and routes:

- Call `getSession(req)` to read the session.
- Call `signIn(req, res)` to authenticate from an application route.
- Call `signOut(req, res)` to end the session from an application route.

Populate `res.locals.session` once when downstream handlers share session state:

```ts
app.use(async (req, res, next) => {
  res.locals.session = await getSession(req)
  next()
})

app.post("/auth/signin", async (req, res) => {
  await signIn(req, res)
  res.redirect("/dashboard")
})
```
