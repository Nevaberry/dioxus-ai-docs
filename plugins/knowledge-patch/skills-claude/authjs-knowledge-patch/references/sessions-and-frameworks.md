# Sessions and Framework Integrations

## Session lifecycle

### Session endpoint cache prevention

GET requests to the session endpoint automatically include cache-prevention headers. Consumers receive fresh session state without wrapping that endpoint in additional cache-control handling.

### Expired database sessions

When Auth.js reads a database-backed `Session`, it checks `expires`. If the row is already expired, Auth.js deletes it.

## Qwik

### Read and protect with the session

The Qwik integration prepares the session automatically. Server code reads it from `event.sharedMap`; client code uses the `useSession()` action. A request handler can protect a server route directly from the shared session.

```ts
export const onRequest: RequestHandler = (event) => {
  const session = event.sharedMap.get("session")
  if (!session || new Date(session.expires) < new Date()) {
    throw event.redirect(302, "/")
  }
}
```

### Sign in and sign out

`useSignIn()` and `useSignOut()` return actions. Use either action as a server-side `<Form>` action or invoke its `.submit()` method on the client.

Sign-in submissions use `providerId` and `options.redirectTo`. Sign-out submissions use `redirectTo`.

```tsx
const signIn = useSignIn()

<Form action={signIn}>
  <input type="hidden" name="providerId" value="github" />
  <input type="hidden" name="options.redirectTo" value="/dashboard" />
  <button>Sign in</button>
</Form>
```

## SvelteKit

### Server session access

Install the Auth.js SvelteKit `handle` to make `event.locals.auth()` available in page and layout server loads and in `+server.ts` endpoints. Return the result from a load function when the client needs the session through page data.

```ts
export const load: PageServerLoad = async (event) => {
  const session = await event.locals.auth()
  if (!session?.user?.userId) redirect(303, "/login")
  return { session }
}
```

### Authentication form actions

The server-side `SignIn` and `SignOut` components from `@auth/sveltekit/components` require matching default form actions at `/signin` and `/signout`. Change those locations through `signInPage` and `signOutPage` when necessary.

```ts
// src/routes/signin/+page.server.ts
export const actions: Actions = { default: signIn }

// src/routes/signout/+page.server.ts
export const actions: Actions = { default: signOut }
```

For purely client-side controls, import the corresponding handlers from `@auth/sveltekit/client`.

## Express

The Express integration exposes `getSession(req)` for middleware and `signIn(req, res)` and `signOut(req, res)` for application-owned routes. If several downstream handlers need the session, resolve it once and put it in `res.locals`.

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
