# shadcn-svelte — Component Catalog

## Installation pattern

```bash
pnpm dlx sv create my-app --add tailwindcss
cd my-app
pnpm dlx shadcn-svelte@latest init
pnpm dlx shadcn-svelte@latest add button card dialog input
```

Components land in `src/lib/components/ui/<name>/` — each as its own folder with an `index.ts` barrel and individual `.svelte` files. **You own them.** Edit freely.

## Import (composable mode, Svelte 5)

```svelte
<script lang="ts">
  import * as Dialog from "$lib/components/ui/dialog/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
</script>

<Dialog.Root>
  <Dialog.Trigger>
    {#snippet child({ props })}
      <Button {...props}>Open</Button>
    {/snippet}
  </Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Title>Title</Dialog.Title>
    <Dialog.Description>Description</Dialog.Description>
  </Dialog.Content>
</Dialog.Root>
```

The `{#snippet child({ props })}` pattern replaces Svelte 4's `<Trigger asChild let:builder>`.

## Common primitives + when to use

| Primitive | Use case |
|---|---|
| `Button` | Any clickable action; variants: `default`, `secondary`, `outline`, `ghost`, `destructive`, `link` |
| `Card` | Grouped content with header/title/description/content/footer slots |
| `Dialog` | Modal that needs user attention; use `Sheet` for side panels |
| `Sheet` | Side drawer (mobile menus, filter panels) |
| `Popover` | Floating UI anchored to a trigger; not modal |
| `Tooltip` | Hover-only hint; never use for primary information |
| `DropdownMenu` | Action menu (kebab, settings); keyboard-navigable |
| `Select` | Single-value picker from a list |
| `Combobox` | Search + select; built from `Command` primitives |
| `Tabs` | Mutually exclusive views; use sparingly on mobile |
| `Toast` (sonner) | Async feedback; never for synchronous errors |
| `Alert` | Inline static notice; never for transient feedback |
| `Skeleton` | Loading placeholder; match the shape of what's loading |

## Tables — TanStack Table for Svelte

shadcn-svelte's `DataTable` is built on TanStack Table. Use when you need sorting, filtering, pagination, or column visibility. For simple read-only tables, use plain `<Table>` primitives — TanStack is overhead.

```svelte
<script lang="ts">
  import { createSvelteTable, getCoreRowModel } from "@tanstack/svelte-table";
  import { Table } from "$lib/components/ui/table";

  const table = createSvelteTable({
    get data() { return rows; },
    columns,
    getCoreRowModel: getCoreRowModel(),
  });
</script>
```

## Icon library

`@lucide/svelte` is the default. Import as components, not strings:

```svelte
<script>
  import { Search, X, ChevronDown } from "@lucide/svelte";
</script>
<Search class="size-4" />
```

Size with Tailwind (`size-4`, `size-5`), not the `size` prop, to keep visual rhythm with the spacing scale.
