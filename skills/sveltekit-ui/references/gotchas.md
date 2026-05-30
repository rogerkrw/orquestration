# shadcn-svelte / Svelte 5 / Tailwind v4 — Gotchas

## Svelte 5 migration smells

### Reactive declarations
- **Svelte 4:** `$: doubled = count * 2`
- **Svelte 5:** `let doubled = $derived(count * 2)`
- Mixing `$:` and runes in the same component is a code smell; pick one per file (rune-mode is the default in new projects).

### Props
- **Svelte 4:** `export let name = "default"`
- **Svelte 5:** `let { name = "default" } = $props()`
- TypeScript: `let { name = "default" }: { name?: string } = $props()` or use a `Props` type.

### Snippets replace slots
- **Svelte 4 slot:** `<slot name="header" />` + `<div slot="header">…</div>`
- **Svelte 5 snippet:** `{@render header()}` + `{#snippet header()}…{/snippet}`
- Named slots are deprecated. Default slot still works but use `{@render children?.()}` in new code.

### Stores → runes
- Stores still work for cross-component state, but for component-local state use `$state`.
- `$state` is shallow-reactive by default. Use `$state.raw` for non-reactive references (e.g., a large dataset you mutate elsewhere).

## Tailwind v3 → v4

- **No `tailwind.config.js` in v4.** Config lives in CSS via `@theme`. If you see one, it's a v3 leftover.
- **`@apply` still works** but is discouraged; prefer composing with classes directly.
- **Custom variants** use `@custom-variant` instead of the JS `addVariant`.
- **Content scanning** uses `@source` directives instead of `content: [...]` config.
- **Plugin loading**: `@plugin "tailwindcss-animate";` instead of `plugins: [...]`.

## shadcn-svelte specifics

- **Composable mode is current.** Old `<Dialog.Root>` + `<Dialog.Trigger asChild let:builder>` is legacy. Use snippets: `{#snippet child({ props })}<Button {...props}>…</Button>{/snippet}`.
- **DataTable updates require runes.** If a column update doesn't render, check that you're using `$state` for the data and `get data() { return rows; }` in `createSvelteTable`.
- **Forms break silently without `<Form.Control>`.** Visual is fine, accessibility and error binding are not.

## React → Svelte translation traps

| React pattern | Svelte 5 equivalent | Trap |
|---|---|---|
| `useState` | `$state` | $state is not a function call; it's a rune |
| `useEffect` | `$effect` | `$effect` runs after DOM update; for derived data use `$derived` |
| `useMemo` | `$derived` | `$derived` is automatic; don't wrap everything |
| `useRef` | `let el: HTMLElement; bind:this={el}` | Svelte refs are real DOM refs, not boxes |
| `cn(…)` (clsx) | `cn(…)` from `$lib/utils` | shadcn-svelte ships its own `cn` helper |
| `forwardRef` | Not needed | All Svelte components forward DOM via `bind:this` |
| `children` prop | `{@render children?.()}` | Children are snippets, not nodes |

## Performance

- **Don't put expensive computations in `$derived`** that runs every render. Memoize at the data layer or move to a load function.
- **Large lists need virtualization** (e.g., `@tanstack/svelte-virtual`) past ~200 visible rows; native Svelte rendering doesn't paginate for you.
- **Image optimization is manual.** `enhanced:img` (from `@sveltejs/enhanced-img`) replaces what Next.js's `<Image>` does — use it for hero/above-fold images.

## SSR / hydration mismatches

- **Don't read `window` / `document` at top level.** Use `onMount` or `browser` guard from `$app/environment`.
- **Date formatting differs SSR vs. client.** Use `Intl.DateTimeFormat` with explicit locale (`"en-US"`), never `toLocaleString()` without args.
- **Random IDs** must come from the server (`crypto.randomUUID()` in a `load` function), not generated client-side at render.

## Build-time

- **Vite + Tailwind v4 needs `@tailwindcss/vite` plugin.** PostCSS pipeline is deprecated for v4.
- **Bundle size:** shadcn-svelte components are tree-shaken because you own them — unused components don't ship. The biggest cost is usually icon libraries; import individually, never barrel-import.
