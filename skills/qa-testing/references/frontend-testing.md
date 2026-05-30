# Frontend Testing — SvelteKit / React

## Tool selection

| Test type | Tool | Why |
|---|---|---|
| Pure logic / utility functions | **vitest** | Fast, no DOM needed |
| Components in isolation | **vitest + browser mode** (SvelteKit) / **vitest + Testing Library** (React) | Real browser rendering, less flaky than jsdom |
| API mocking for component tests | **MSW** (Mock Service Worker) | Works in both unit and E2E |
| E2E user flows | **playwright** | Cross-browser, real network, real cookies |
| Visual regression | **playwright** (screenshots) or **percy/chromatic** | Catches design drift |

Why vitest browser mode over jsdom: jsdom is incomplete; real bugs hide in jsdom passes that fail in actual browsers. Browser mode runs in real Chromium/Firefox/Webkit with the same vitest API.

## vitest setup (SvelteKit)

```ts
// vite.config.ts
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  plugins: [sveltekit()],
  test: {
    workspace: [
      {
        extends: './vite.config.ts',
        test: {
          name: 'unit',
          include: ['src/**/*.test.ts'],
          environment: 'node',
        },
      },
      {
        extends: './vite.config.ts',
        test: {
          name: 'browser',
          include: ['src/**/*.svelte.test.ts'],
          browser: {
            enabled: true,
            provider: 'playwright',
            instances: [{ browser: 'chromium' }],
          },
        },
      },
    ],
  },
});
```

## Component test (Svelte 5 + browser)

```ts
// src/lib/components/Button.svelte.test.ts
import { render, screen } from '@testing-library/svelte';
import { userEvent } from '@vitest/browser/context';
import { expect, test, vi } from 'vitest';
import Button from './Button.svelte';

test('Button calls onclick when clicked', async () => {
  const handler = vi.fn();
  render(Button, { props: { onclick: handler, children: 'Click me' } });
  await userEvent.click(screen.getByText('Click me'));
  expect(handler).toHaveBeenCalledOnce();
});
```

## Mocking SvelteKit modules

```ts
import { vi } from 'vitest';

vi.mock('$app/navigation', () => ({
  goto: vi.fn(),
  invalidateAll: vi.fn(),
}));

vi.mock('$app/stores', () => ({
  page: readable({ url: new URL('http://localhost/test'), params: {} }),
}));
```

## API mocking with MSW

```ts
// src/lib/test-utils/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users/:id', ({ params }) => {
    return HttpResponse.json({ id: params.id, name: 'Alice' });
  }),
];

// src/lib/test-utils/setup.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';
import { beforeAll, afterEach, afterAll } from 'vitest';

const server = setupServer(...handlers);
beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

`onUnhandledRequest: 'error'` catches "the test forgot to mock an endpoint" — flaky tests turn into hard failures.

## Playwright E2E

```ts
// tests/e2e/login.spec.ts
import { test, expect } from '@playwright/test';

test('user can log in', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('alice@test.com');
  await page.getByLabel('Password').fill('correcthorsebattery');
  await page.getByRole('button', { name: 'Log in' }).click();
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByText('Welcome, Alice')).toBeVisible();
});
```

## Test-id discipline

Avoid `data-testid` for anything you can select semantically:

| Bad | Good |
|---|---|
| `getByTestId('submit-btn')` | `getByRole('button', { name: 'Submit' })` |
| `getByTestId('email-input')` | `getByLabelText('Email')` |
| `getByTestId('error-msg')` | `getByRole('alert')` |

`data-testid` is acceptable for things that have no semantic role (a chart, a custom widget). When you use it, mark it clearly: `data-testid="user-list"` not `data-testid="ul-1"`.

## Playwright fixtures

```ts
// tests/fixtures.ts
import { test as base } from '@playwright/test';

type Fixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<Fixtures>({
  authenticatedPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.getByLabel('Email').fill('test@test.com');
    await page.getByLabel('Password').fill('test');
    await page.click('button[type=submit]');
    await page.waitForURL('/dashboard');
    await use(page);
  },
});
```

Now tests use `test('thing', async ({ authenticatedPage }) => { ... })` and skip the login boilerplate.

## Visual regression

```ts
test('homepage visual', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    maxDiffPixels: 100,  // allow tiny anti-aliasing differences
    fullPage: true,
  });
});
```

- Screenshots commit to git; review changes in PR
- Update with `playwright test --update-snapshots`
- Mask dynamic content (timestamps, avatars) with `mask: [page.getByTestId('time')]`

## Common failures

- **Test passes locally, fails in CI** → almost always timing; add explicit `await expect(locator).toBeVisible()` instead of arbitrary `waitForTimeout`
- **Hydration mismatch in component test** → component reads `window` at module scope; guard with `browser` check
- **MSW handler not called** → check the URL pattern (relative vs absolute, trailing slash)
- **Playwright element not found** → try `await page.pause()` to inspect interactively; check for iframes
