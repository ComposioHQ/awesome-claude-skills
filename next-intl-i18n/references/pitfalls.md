# next-intl Edge Cases & Pitfalls

---

## Static Rendering with i18n

By default, Next.js tries to statically render pages. With i18n, this requires `generateStaticParams` in the locale layout — otherwise dynamic locale pages won't build.

```tsx
// app/[locale]/layout.tsx — required for static export or output: 'export'
export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}
```

If you're using `output: 'export'` in next.config, you also need `localeDetection: false` in your routing config (cookie/header detection doesn't work without a server).

---

## Suspense Boundaries and useTranslations

`useTranslations` reads from context. If a Client Component using it renders outside the `NextIntlClientProvider` tree (e.g., inside a Portal, or in an error boundary that mounts before the provider), it will throw.

Fix: ensure `NextIntlClientProvider` is high enough in the tree — ideally in `[locale]/layout.tsx` wrapping all children.

---

## Nested Layouts Losing Locale

If you add a nested layout that doesn't pass through the locale param, child pages lose locale context. Every layout in the `[locale]/` directory that does its own data fetching needs to either:

1. Accept and forward `params: Promise<{ locale: string }>`, or
2. Use `getLocale()` from `next-intl/server` to read it from the request

```tsx
// Safe pattern for nested layouts
import { getLocale } from 'next-intl/server';

export default async function NestedLayout({ children }: { children: React.ReactNode }) {
  const locale = await getLocale(); // reads from request, no params needed
  // ...
}
```

---

## Testing with next-intl

In Jest/Vitest unit tests, `useTranslations` needs a provider or a mock. The simplest approach is to mock the hook:

```ts
jest.mock('next-intl', () => ({
  useTranslations: () => (key: string) => key,
  useLocale: () => 'es',
}));
```

For integration tests with Playwright or Cypress, set the `NEXT_LOCALE` cookie or navigate to the localized path directly (`/en/about`).

---

## Per-Page Namespaces vs Shared Namespaces

Pattern that scales well in large apps:

```
messages/es.json
{
  "common": { "loading": "Cargando...", "error": "Error" },
  "nav": { ... },
  "pages": {
    "home": { ... },
    "dashboard": { ... }
  }
}
```

Load only the namespace you need per component:
```ts
const t = await getTranslations('pages.home');
// or
const t = useTranslations('common');
```

Avoid one giant flat namespace — TypeScript inference slows down and message keys become ambiguous.

---

## Date & Number Formatting

next-intl wraps the Intl API. Use `useFormatter` (client) or `getFormatter` (server):

```ts
// Server
const format = await getFormatter();
format.dateTime(new Date(), { dateStyle: 'long' }); // "12 de marzo de 2025" in es

// Client
'use client';
const format = useFormatter();
format.number(1234567, { style: 'currency', currency: 'COP' }); // $ 1.234.567 in es-CO
```

For Colombian peso specifically, you'll want `locale: 'es-CO'` not just `'es'` — the number separators differ from Spain.

---

## Adding a Third Locale Later

1. Add locale to `routing.ts` locales array
2. Create `messages/[locale].json` (copy from default and translate)
3. That's it — middleware and routing update automatically

The one gotcha: if you have `generateStaticParams`, add the new locale there too.

---

## Environment Variable for Default Locale

Useful for staging environments where you want to test the non-default locale:

```ts
// i18n/routing.ts
export const routing = defineRouting({
  locales: ['es', 'en'],
  defaultLocale: (process.env.DEFAULT_LOCALE as 'es' | 'en') ?? 'es',
  localePrefix: 'as-needed'
});
```

---

## Translating Zod Error Messages

If you use Zod for form validation and want locale-aware errors:

```ts
import { useTranslations } from 'next-intl';
import { z } from 'zod';

function useSchema() {
  const t = useTranslations('Validation');
  return z.object({
    email: z.string().email(t('invalidEmail')),
    name: z.string().min(2, t('nameTooShort')),
  });
}
```

Put `useSchema` in a Client Component or custom hook — Zod schemas with translated messages need to be created at render time, not module level.