---
name: sveltekit
description: >
  Expert-level SvelteKit development skill for building full-stack web applications.
  Use this skill whenever working with SvelteKit — whether creating a new project,
  designing routes, implementing load functions, writing server endpoints, handling
  forms, managing state, configuring adapters, or debugging SvelteKit-specific patterns.
  Also trigger for: +page.svelte, +layout.svelte, +server.js, +page.server.js,
  +page.js, +layout.server.js, src/hooks.server.js, svelte.config.js, form actions,
  SSR/CSR/prerender decisions, $app/* imports, $env/* imports, adapter selection,
  filesystem routing questions, and any mention of "SvelteKit", "SvelteKit app", or
  "SvelteKit project". Do not confuse with plain Svelte (component-only); SvelteKit
  adds routing, SSR, adapters, and server-side capabilities.
---

# SvelteKit Development Skill

SvelteKit is Svelte's full-stack framework — filesystem-based routing, SSR/CSR/prerendering, server endpoints, form actions, adapters for any deployment target. Built on Vite; uses Svelte 5 runes by default.

## Version and migration baseline

Use the project's installed SvelteKit/Svelte/Vite versions as the source of truth. For new
projects, use the current SvelteKit 2 + Svelte 5 toolchain and a supported Node LTS. In existing
projects, do not mix Svelte 4 examples into rune-mode components. `$app/stores` is deprecated in
modern SvelteKit; prefer `$app/state` and use the official `sv migrate app-state` migration when
upgrading. Check the [SvelteKit migration guide](https://svelte.dev/docs/kit/migrating-to-sveltekit-2)
before changing framework APIs.

## Mental Model

Every route is a **directory** under `src/routes/`. Files with `+` prefix are special. The key insight: SvelteKit blurs the server/client boundary — the same `load` function can run on server or client depending on context.

```
src/routes/
├ +layout.svelte          ← wraps all pages
├ +layout.server.js       ← server-only layout load
├ +page.svelte            ← root page (/)
├ blog/
│  ├ +page.svelte         ← /blog
│  ├ +page.js             ← universal load (server + client)
│  └ [slug]/
│     ├ +page.svelte      ← /blog/:slug
│     ├ +page.server.js   ← server-only load + form actions
│     └ +error.svelte     ← error boundary for this subtree
└ api/
   └ items/
      └ +server.js        ← REST endpoint (GET/POST/PUT/DELETE)
```

## Route Files — Decision Tree

| Need | File | Exports |
|------|------|---------|
| Page UI | `+page.svelte` | component |
| Load data (public/safe) | `+page.js` | `load`, page options |
| Load data (DB/secrets) | `+page.server.js` | `load`, `actions`, page options |
| Shared layout | `+layout.svelte` | component with `{@render children()}` |
| Layout data | `+layout.server.js` or `+layout.js` | `load` |
| REST API / webhook | `+server.js` | `GET`, `POST`, `PUT`, `DELETE`, `PATCH` |
| Error boundary | `+error.svelte` | component |

**Rule of thumb**: prefer `+page.server.js` when touching DB, secrets, or writing data. Use `+page.js` when fetch-only and safe to run client-side.

## Load Functions

### Universal (`+page.js` / `+layout.js`)
Runs on server for initial request, then in browser on navigation. Can use `fetch` (enhanced by SvelteKit — includes cookies, relative URLs).

```js
// +page.js
export const prerender = false;
export const ssr = true;
export const csr = true;

/** @type {import('./$types').PageLoad} */
export async function load({ params, fetch, url, data, parent }) {
  const res = await fetch(`/api/posts/${params.slug}`);
  if (!res.ok) error(404, 'Not found');
  return { post: await res.json() };
}
```

### Server-only (`+page.server.js` / `+layout.server.js`)
Only runs on server. Can access `locals`, `cookies`, DB clients, env secrets.

```js
// +page.server.js
import { error, redirect, fail } from '@sveltejs/kit';
import { db } from '$lib/server/db';

/** @type {import('./$types').PageServerLoad} */
export async function load({ params, locals, cookies }) {
  if (!locals.user) redirect(302, '/login');
  const post = await db.posts.findUnique({ where: { slug: params.slug } });
  if (!post) error(404, 'Post not found');
  return { post };
}
```

### Key load function properties
- `params` — route params (`{ slug: 'hello-world' }`)
- `url` — URL object
- `route.id` — route identifier string
- `fetch` — enhanced fetch (carries cookies, works SSR)
- `locals` — set in `handle` hook; server-only
- `cookies` — cookie API; server-only
- `parent()` — await parent layout data (creates dependency)
- `depends('custom:key')` — manual invalidation target

## Receiving Data in Components

```svelte
<!-- +page.svelte (Svelte 5) -->
<script>
  /** @type {import('./$types').PageProps} */
  let { data } = $props();  // typed via generated $types
</script>

<h1>{data.post.title}</h1>
```

For layouts, also destructure `children`:
```svelte
<script>
  let { data, children } = $props();
</script>
{@render children()}
```

## Form Actions

Defined in `+page.server.js`, invoked via native `<form method="POST">`.

```js
// +page.server.js
import { fail, redirect } from '@sveltejs/kit';

export const actions = {
  // named action: ?/create
  create: async ({ request, locals }) => {
    const data = await request.formData();
    const title = data.get('title');
    if (!title) return fail(422, { error: 'Title required', values: { title } });
    await db.create({ title, userId: locals.user.id });
    redirect(303, '/posts');
  },
  // default action (no ?/name needed)
  default: async ({ request }) => { /* ... */ }
};
```

```svelte
<!-- +page.svelte -->
<script>
  import { enhance } from '$app/forms';
  let { form } = $props(); // action return value
</script>

<form method="POST" action="?/create" use:enhance>
  <input name="title" value={form?.values?.title ?? ''} />
  {#if form?.error}<p>{form.error}</p>{/if}
  <button>Create</button>
</form>
```

`use:enhance` — progressive enhancement: submits via fetch, updates `form` prop, re-runs load without full page reload.

## Server Endpoints (`+server.js`)

```js
// src/routes/api/items/+server.js
import { json, error } from '@sveltejs/kit';

export async function GET({ url, locals }) {
  const items = await db.items.findMany();
  return json(items);
}

export async function POST({ request, locals }) {
  if (!locals.user) error(401, 'Unauthorized');
  const body = await request.json();
  const item = await db.items.create({ data: body });
  return json(item, { status: 201 });
}
```

## Hooks

```js
// src/hooks.server.js
import { redirect } from '@sveltejs/kit';

/** @type {import('@sveltejs/kit').Handle} */
export async function handle({ event, resolve }) {
  // Auth guard example
  event.locals.user = await getUserFromSession(event.cookies.get('session'));
  
  if (event.url.pathname.startsWith('/admin') && !event.locals.user?.admin) {
    redirect(302, '/login');
  }
  
  const response = await resolve(event, {
    transformPageChunk: ({ html }) => html.replace('%lang%', 'pt-BR')
  });
  
  response.headers.set('X-Custom', 'value');
  return response;
}

/** @type {import('@sveltejs/kit').HandleFetch} */
export async function handleFetch({ request, fetch }) {
  // Intercept server-side fetch calls
  return fetch(request);
}
```

Declare `App.Locals` shape in `src/app.d.ts`:
```ts
declare global {
  namespace App {
    interface Locals {
      user: { id: string; admin: boolean } | null;
    }
    interface Error { message: string; code?: string; }
  }
}
```

## Environment Variables

```js
// Server-only (never sent to client)
import { DATABASE_URL, SECRET_KEY } from '$env/static/private';
import { env } from '$env/dynamic/private';

// Public (safe for client)
import { PUBLIC_API_URL } from '$env/static/public';
import { env } from '$env/dynamic/public';
```

**Rule**: `$env/static/*` = tree-shakeable build-time constants; `$env/dynamic/*` = runtime values (needed for edge/serverless). Never import `private` in `+page.js`, `+layout.js`, or `.svelte` files — SvelteKit will throw.

## Advanced Routing

```
[slug]              → /blog/hello-world  → params.slug = 'hello-world'
[...rest]           → /a/b/c            → params.rest = 'a/b/c'
[[optional]]        → /with or /without
(group)             → layout grouping, no URL segment
[slug=matcher]      → validates param with src/params/matcher.js
```

Layout groups let you apply different layouts without URL changes:
```
src/routes/
├ (auth)/
│  ├ +layout.svelte   ← auth layout
│  ├ login/+page.svelte
│  └ register/+page.svelte
└ (app)/
   ├ +layout.svelte   ← app shell
   └ dashboard/+page.svelte
```

Break out of a layout hierarchy: `+page@.svelte` (reset to root), `+page@(group).svelte` (reset to group).

## Page Options

Export from `+page.js`, `+page.server.js`, `+layout.js`, `+layout.server.js`:

```js
export const prerender = true;   // generate at build time
export const ssr = false;        // SPA mode for this route
export const csr = false;        // no JS hydration (pure HTML)
```

## State Management

**Critical**: never store user state in module-level variables on the server — it's shared across all requests.

Safe patterns:
- `event.locals` — per-request server state
- `$app/state` → `page` — client-side reactive page state
- Svelte context (`setContext`/`getContext`) — scoped to component tree
- URL search params — shareable/bookmarkable state

```svelte
<script>
  import { page } from '$app/state';
  // page.url, page.params, page.data, page.status, page.error
</script>
```

## $app/* Modules Reference

| Module | Key exports | Use |
|--------|------------|-----|
| `$app/state` | `page` | Reactive page state (Svelte 5) |
| `$app/navigation` | `goto`, `invalidate`, `invalidateAll`, `preloadData` | Programmatic navigation |
| `$app/forms` | `enhance` | Progressive form enhancement |
| `$app/environment` | `browser`, `dev`, `building` | Environment detection |
| `$app/paths` | `base`, `assets` | Configured paths |

## Adapters

Configure in `svelte.config.js`:
```js
import adapter from '@sveltejs/adapter-auto';   // auto-detect (Vercel/Netlify/CF)
// import adapter from '@sveltejs/adapter-node'; // Node.js server
// import adapter from '@sveltejs/adapter-static'; // pure static site
// import adapter from '@sveltejs/adapter-cloudflare'; // CF Workers

export default {
  kit: { adapter: adapter() }
};
```

`adapter-static` requires `export const prerender = true` on all pages (or root layout).

## $lib Alias

`$lib` maps to `src/lib/`. Use for shared utilities:
```
src/lib/
├ server/       ← server-only code (auto-protected, can import secrets)
│  ├ db.js
│  └ auth.js
├ components/   ← shared UI
└ utils.js
```

`$lib/server/*` — SvelteKit blocks these from being imported in client-side code.

## Common Patterns

### Auth guard (hook-based, recommended)
```js
// src/hooks.server.js
export async function handle({ event, resolve }) {
  event.locals.user = await validateSession(event.cookies.get('session'));
  return resolve(event);
}
```
Then check `locals.user` in each `+page.server.js` load. Never check auth in `+page.js` — it runs client-side.

### Parallel data loading in load
```js
export async function load({ fetch }) {
  const [users, posts] = await Promise.all([
    fetch('/api/users').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
  ]);
  return { users, posts };
}
```

### Streaming with promises (server load only)
```js
export async function load() {
  return {
    fast: await getFastData(),
    slow: getSlowData(), // NOT awaited — streams to client
  };
}
```

### Programmatic navigation
```svelte
<script>
  import { goto, invalidateAll } from '$app/navigation';
  
  async function submit() {
    await doThing();
    await invalidateAll();   // re-run all load functions
    goto('/success');
  }
</script>
```

## Anti-Patterns to Avoid

1. **Shared module-level state on server** — leaked between requests
2. **Secrets in `+page.js`** — runs in browser, exposes env vars
3. **`fetch` outside load without the enhanced version** — misses cookies/auth on SSR
4. **Checking auth client-side only** — security hole; always verify in server load or hooks
5. **Storing user data in `$app/state` server-side** — `page` is client-only reactive
6. **Nesting `+layout.svelte` without `{@render children()}`** — pages won't render
7. **Using `export let` instead of `$props()` in Svelte 5** — deprecated legacy mode

## Typing Cheatsheet (TypeScript)

```ts
// +page.server.js
import type { PageServerLoad, Actions } from './$types';
export const load: PageServerLoad = async ({ params, locals }) => { ... };
export const actions: Actions = { default: async ({ request }) => { ... } };

// +page.js
import type { PageLoad } from './$types';
export const load: PageLoad = async ({ params, fetch }) => { ... };

// +page.svelte
import type { PageProps } from './$types';
let { data, form }: PageProps = $props();

// +server.js
import type { RequestHandler } from './$types';
export const GET: RequestHandler = ({ url }) => { ... };

// hooks.server.js
import type { Handle, HandleFetch } from '@sveltejs/kit';
```

## Quick Reference: `@sveltejs/kit` Helpers

```js
import { error, redirect, fail, json, text } from '@sveltejs/kit';

error(404, 'Not found');           // throw HTTP error
error(403, { message: 'Forbidden', code: 'AUTH_ERR' }); // typed error
redirect(302, '/login');           // throw redirect
fail(422, { field: 'required' }); // form action validation failure
json({ ok: true }, { status: 201 }); // JSON response
text('OK');                        // plain text response
```

## Further Reading

- Full docs: https://svelte.dev/docs/kit/introduction
- Routing: https://svelte.dev/docs/kit/routing
- Load functions: https://svelte.dev/docs/kit/load
- Form actions: https://svelte.dev/docs/kit/form-actions
- Hooks: https://svelte.dev/docs/kit/hooks
- Advanced routing: https://svelte.dev/docs/kit/advanced-routing
- Adapters: https://svelte.dev/docs/kit/adapters
- Configuration reference: https://svelte.dev/docs/kit/configuration
