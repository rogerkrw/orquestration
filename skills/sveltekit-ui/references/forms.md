# Forms — Formsnap + Superforms + Zod

The canonical stack for SvelteKit forms. Gives you: typed schemas, server validation, client validation, progressive enhancement, error states, accessibility wiring — for free.

## Setup

```bash
npm install sveltekit-superforms zod formsnap
```

## Schema (shared client + server)

```ts
// src/lib/schemas/login.ts
import { z } from "zod";

export const loginSchema = z.object({
  email: z.string().email("Invalid email"),
  password: z.string().min(8, "At least 8 characters"),
});

export type LoginSchema = typeof loginSchema;
```

## Server load + action

```ts
// src/routes/login/+page.server.ts
import { superValidate, message } from "sveltekit-superforms/server";
import { zod } from "sveltekit-superforms/adapters";
import { loginSchema } from "$lib/schemas/login";
import { fail } from "@sveltejs/kit";

export const load = async () => {
  const form = await superValidate(zod(loginSchema));
  return { form };
};

export const actions = {
  default: async ({ request }) => {
    const form = await superValidate(request, zod(loginSchema));
    if (!form.valid) return fail(400, { form });

    // ... auth logic ...

    return message(form, "Logged in");
  },
};
```

## Page form

```svelte
<!-- src/routes/login/+page.svelte -->
<script lang="ts">
  import { superForm } from "sveltekit-superforms";
  import { zodClient } from "sveltekit-superforms/adapters";
  import * as Form from "$lib/components/ui/form";
  import { Input } from "$lib/components/ui/input";
  import { loginSchema } from "$lib/schemas/login";

  let { data } = $props();

  const form = superForm(data.form, {
    validators: zodClient(loginSchema),
  });
  const { form: formData, enhance } = form;
</script>

<form method="POST" use:enhance>
  <Form.Field {form} name="email">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Email</Form.Label>
        <Input {...props} bind:value={$formData.email} type="email" />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>

  <Form.Field {form} name="password">
    <Form.Control>
      {#snippet children({ props })}
        <Form.Label>Password</Form.Label>
        <Input {...props} bind:value={$formData.password} type="password" />
      {/snippet}
    </Form.Control>
    <Form.FieldErrors />
  </Form.Field>

  <Form.Button>Login</Form.Button>
</form>
```

## Critical patterns

- **Always wrap inputs in `<Form.Control>`**. It generates the `id`/`for` linkage, ARIA attributes, and error binding. Skipping it = broken a11y.
- For non-`<input>` controls (Select, Combobox), the `{#snippet children({ props })}` pattern is mandatory — props carry the ARIA wiring.
- `<Form.FieldErrors />` reads from the field state — no manual error rendering.
- Server-side, always check `form.valid` before processing. The schema is the contract; bypassing it is the source of most form bugs.
- For multi-step forms, use one schema with `.partial()` per step, or one schema per step composed by `.merge()`.

## File uploads

Superforms handles multipart natively when the schema uses `z.instanceof(File)`. Use `dataType: "form"` in `superForm` options when uploading files.

## Submit states

```svelte
<script>
  const { submitting, delayed, timeout } = form;
</script>

<Form.Button disabled={$submitting}>
  {#if $delayed}Submitting…{:else}Login{/if}
</Form.Button>
```

`$delayed` triggers after 500ms (configurable), preventing flash on fast networks. `$timeout` triggers at 8s for "still working" UI.
