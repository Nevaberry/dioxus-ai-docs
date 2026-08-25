# Sessions and Framework Integrations

## Session freshness and expiry

GET requests to the session endpoint automatically receive headers that
prevent caching. Consumers can rely on that endpoint to return fresh session
state without wrapping it in additional cache-control headers.

When Auth.js reads a database-backed `Session`, it checks `expires`. If the
record has expired, Auth.js deletes the row as part of the read.

## Qwik

### Read and protect with the prepared session

The Qwik integration prepares the session automatically. Server code reads it
from `event.sharedMap`; client code uses the `useSession()` action. A server
request handler can protect a route directly from the shared session.

```ts
export const onRequest: RequestHandler = (event) => {
  const session = event.sharedMap.get("session")
  if (!session || new Date(session.expires) < new Date()) {
    throw event.redirect(302, "/")
  }
}
```

### Submit sign-in and sign-out actions

`useSignIn()` and `useSignOut()` return actions usable in a server-side
`<Form>` or through `.submit()` on the client. A sign-in submission uses the
`providerId` and `options.redirectTo` fields. A sign-out submission uses
`redirectTo`.

```tsx
const signIn = useSignIn()

<Form action={signIn}>
  <input type="hidden" name="providerId" value="github" />
  <input type="hidden" name="options.redirectTo" value="/dashboard" />
  <button>Sign in</button>
</Form>
```

## SvelteKit

### Read the server session

Installing the Auth.js SvelteKit `handle` adds `event.locals.auth()`. It is
available in page and layout server loads and in `+server.ts` endpoints. Return
the result from a load function when client-facing page data needs the session.

```ts
export const load: PageServerLoad = async (event) => {
  const session = await event.locals.auth()
  if (!session?.user?.userId) redirect(303, "/login")
  return { session }
}
```

### Wire authentication controls

The server-side `SignIn` and `SignOut` components from
`@auth/sveltekit/components` require matching default form actions at
`/signin` and `/signout`. Change those paths with `signInPage` and
`signOutPage` when needed.

```ts
// src/routes/signin/+page.server.ts
export const actions: Actions = { default: signIn }

// src/routes/signout/+page.server.ts
export const actions: Actions = { default: signOut }
```

For purely client-side controls, import the corresponding handlers from
`@auth/sveltekit/client`.

## Express

Use `getSession(req)` from middleware and call `signIn(req, res)` or
`signOut(req, res)` from application-owned routes. When several handlers need
the session, resolve it once into `res.locals.session`.

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
