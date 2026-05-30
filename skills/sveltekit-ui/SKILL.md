---
name: sveltekit-ui
description: shadcn-svelte component system on SvelteKit + Svelte 5 runes + Tailwind v4. Use when building or refining UI in a SvelteKit project — components, forms, theming, dark mode, design tokens. Complements the `sveltekit` skill (which covers routing/SSR/load functions); this one covers the visual layer.
---

# SvelteKit UI — shadcn-svelte + Tailwind v4

The frontend visual layer for SvelteKit projects. Pairs with the `sveltekit` skill (routing/SSR) and is consumed by `swe-frontend` and `ux-ui-designer`.

## Stack assumptions
- **Svelte 5** with runes (`$state`, `$derived`, `$effect`, `$props`)
- **Tailwind v4** with OKLCH color tokens (no `tailwind.config.js` — config lives in CSS via `@theme`)
- **shadcn-svelte** components copied into `$lib/components/ui/`, owned by the project
- **bits-ui** as the headless primitive layer
- **Formsnap + Superforms + Zod** for forms
- **mode-watcher** for dark/light mode

## Core rules
1. Components are **owned, not imported from a package**. If you need to modify behavior, edit the file in `$lib/components/ui/`.
2. Use **design tokens** (`bg-primary`, `text-muted-foreground`) — never arbitrary classes (`bg-[#3b82f6]`, `text-[14px]`).
3. **Composable mode** is the current standard: import primitives explicitly (`import { Root, Trigger, Content } from "$lib/components/ui/dialog"`), not from a barrel object.
4. **Read `$lib/components/ui/` before creating any new component** — duplicating an existing primitive is the most common failure here.
5. For forms, **always** wrap inputs in `<Form.Field>` + `<Form.Control>`. Skipping `<Form.Control>` breaks accessibility for non-`<input>` elements (Select, Combobox).

## Top 5 gotchas
1. **`class:dark` toggle by hand → broken.** Use `<ModeWatcher />` + `toggleMode()` from `mode-watcher`. Manual toggle skips system-pref sync and persists nothing.
2. **Svelte 4 `let:item` syntax in new code.** Svelte 5 uses snippets: `{#snippet item(value)}...{/snippet}`. Mixing styles in the same component breaks reactivity.
3. **Tailwind v3 `tailwind.config.js` patterns.** v4 reads everything from CSS (`@theme`, `@import "tailwindcss"`). A `tailwind.config.js` file at the root is a v3 migration smell.
4. **Importing from `bits-ui` directly** when shadcn-svelte has wrapped it. Always prefer `$lib/components/ui/*`; only drop to bits-ui for custom primitives.
5. **`use:enhance` without `superForm`** for forms with validation. Pure `use:enhance` gives you progressive enhancement but no client-side validation; Superforms wires both.

## When to load references
- Building a component or wiring a primitive → `references/components.md`
- Designing tokens, theming, dark mode, color system → `references/theming.md`
- Building any form → `references/forms.md`
- Hit a wall or unexpected behavior → `references/gotchas.md`
