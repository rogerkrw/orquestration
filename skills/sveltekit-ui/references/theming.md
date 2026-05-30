# Theming — Tailwind v4 + OKLCH + Dark Mode

## Tailwind v4 setup

No `tailwind.config.js`. Everything in CSS:

```css
/* src/app.css */
@import "tailwindcss";
@plugin "tailwindcss-animate";
@source "../**/*.{html,js,svelte,ts}";

@custom-variant dark (&:is(.dark *));

@theme {
  --color-background: oklch(1 0 0);
  --color-foreground: oklch(0.145 0 0);
  --color-primary: oklch(0.205 0 0);
  --color-primary-foreground: oklch(0.985 0 0);
  --color-muted: oklch(0.97 0 0);
  --color-muted-foreground: oklch(0.556 0 0);
  --color-destructive: oklch(0.577 0.245 27.325);
  --color-border: oklch(0.922 0 0);
  --color-ring: oklch(0.708 0 0);
  --radius: 0.625rem;
}

.dark {
  --color-background: oklch(0.145 0 0);
  --color-foreground: oklch(0.985 0 0);
  --color-primary: oklch(0.985 0 0);
  --color-primary-foreground: oklch(0.205 0 0);
  --color-muted: oklch(0.269 0 0);
  --color-muted-foreground: oklch(0.708 0 0);
  --color-border: oklch(0.269 0 0);
}
```

## OKLCH — why and how to pick colors

OKLCH is perceptually uniform: equal lightness numbers feel equally bright. Use it for:
- Reliable contrast ratios (calculate L difference, get predictable WCAG passes)
- Smooth color scales (lerp L while keeping C and H)
- Dark mode that doesn't wash out

**Tooling:** `oklch.com/` or VSCode extensions. Don't convert hex by hand.

**Picking values:**
- Backgrounds: L 0.95–1.0 (light) / 0.10–0.20 (dark)
- Surfaces: L 0.97 / 0.18
- Text on background: L 0.10–0.20 (light) / 0.90–1.0 (dark)
- Muted text: L 0.50–0.60 (consistent in both modes)
- Borders: L 0.90 / 0.27

## Dark mode

```svelte
<!-- src/routes/+layout.svelte -->
<script>
  import { ModeWatcher } from "mode-watcher";
</script>

<ModeWatcher />
<slot />
```

```svelte
<!-- toggle component -->
<script>
  import { toggleMode } from "mode-watcher";
  import { Sun, Moon } from "@lucide/svelte";
  import { Button } from "$lib/components/ui/button";
</script>

<Button variant="ghost" size="icon" onclick={toggleMode}>
  <Sun class="size-4 dark:hidden" />
  <Moon class="hidden size-4 dark:block" />
</Button>
```

`<ModeWatcher />` handles SSR (no FOUC), system-preference detection, persistence to `localStorage`, and the `.dark` class on `<html>`.

## Component tokens

shadcn-svelte components reference semantic tokens, not raw colors:

| Token | When |
|---|---|
| `bg-background` / `text-foreground` | Default page surface |
| `bg-card` / `text-card-foreground` | Card surfaces |
| `bg-primary` / `text-primary-foreground` | Primary actions |
| `bg-secondary` / `text-secondary-foreground` | Secondary actions |
| `bg-muted` / `text-muted-foreground` | De-emphasized content |
| `bg-accent` / `text-accent-foreground` | Hover/focus surfaces |
| `bg-destructive` / `text-white` | Destructive actions, errors |
| `border-border` | Default borders |
| `ring-ring` | Focus rings |

Override these in `@theme` — never override Tailwind's `blue-500` etc. to "rebrand."
