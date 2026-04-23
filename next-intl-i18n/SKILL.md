---
name: next-intl-i18n
description: Set up and maintain multilingual Next.js App Router applications using next-intl. Use this skill whenever the user mentions i18n, internationalization, translations, multiple languages, locale routing, next-intl, or multilingual support in a Next.js project — even if they only say "I want to add Spanish" or "make my app work in two languages." Also trigger when debugging locale-related errors like missing messages, broken middleware, or useTranslations crashing in a Server Component.
---

# next-intl i18n for Next.js App Router

Opinionated, production-tested guide for `next-intl` with the App Router. The single biggest source of bugs is the **RSC/client boundary split** — Server Components use `getTranslations()` (async), Client Components use `useTranslations()` (hook). Everything else follows from that.

---

## Quick Setup Checklist

1. Install: `npm install next-intl`
2. Create `messages/` directory with one JSON per locale
3. Create `i18n/request.ts` (next-intl config)
4. Wrap `next.config.ts` with `createNextIntlPlugin`
5. Add `middleware.ts` at project root
6. Move app files into `app/[locale]/` directory
7. Add `NextIntlClientProvider` to `[locale]/layout.tsx`

See → [references/setup.md](./references/setup.md) for full file contents.

---

## Project Structure

```
├── messages/
│   ├── es.json          # default locale
│   └── en.json
├── i18n/
│   └── request.ts       # locale + messages resolver
├── middleware.ts         # locale detection & redirect
├── next.config.ts        # wrapped with createNextIntlPlugin
└── app/
    └── [locale]/
        ├── layout.tsx    # NextIntlClientProvider lives here
        └── page.tsx
```

---

## The RSC / Client Boundary Rule

This is the #1 source of errors. Memorize it:

| Context | Function | Notes |
|---|---|---|
| Server Component | `await getTranslations('Namespace')` | async, call at top of component |
| Client Component | `useTranslations('Namespace')` | hook, component must be `'use client'` |
| Server Action / Route Handler | `await getTranslations('Namespace')` | same as RSC |
| generateMetadata | `await getTranslations('Namespace')` | async context |

**Never call `useTranslations` in a Server Component.** It will throw at runtime, not compile time.

```tsx
// ✅ Server Component
export default async function Page() {
  const t = await getTranslations('HomePage');
  return <h1>{t('title')}</h1>;
}

// ✅ Client Component
'use client';
export default function Nav() {
  const t = useTranslations('Nav');
  return <nav>{t('home')}</nav>;
}
```

---

## Middleware Setup

The middleware is what detects locale from headers/cookies/path and redirects. Without it, locale routing breaks silently.

```ts
// middleware.ts (project root, NOT inside app/)
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};
```

```ts
// i18n/routing.ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['es', 'en'],
  defaultLocale: 'es',
  localePrefix: 'as-needed'  // hides /es/, shows /en/
});
```

**`localePrefix` options:**
- `'as-needed'` — default locale has no prefix (`/` = Spanish, `/en/` = English). Best for Spanish-first apps.
- `'always'` — all locales prefixed (`/es/`, `/en/`). Cleaner but adds redirect for root.
- `'never'` — no prefixes, locale from cookie/header only. Hard to share links.

---

## i18n/request.ts

This file runs on every server request to resolve the locale and load messages.

```ts
// i18n/request.ts
import { getRequestConfig } from 'next-intl/server';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  let locale = await requestLocale;

  if (!locale || !routing.locales.includes(locale as any)) {
    locale = routing.defaultLocale;
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default
  };
});
```

---

## Message Files

Keep namespaces flat and consistent across locales. Missing keys throw at runtime in development but silently fall back in production — don't rely on that.

```json
// messages/es.json
{
  "HomePage": {
    "title": "Bienvenida",
    "cta": "Empezar ahora"
  },
  "Nav": {
    "home": "Inicio",
    "about": "Sobre mí"
  }
}
```

```json
// messages/en.json
{
  "HomePage": {
    "title": "Welcome",
    "cta": "Get started"
  },
  "Nav": {
    "home": "Home",
    "about": "About"
  }
}
```

**Keep both files in sync.** A missing key in one locale will crash in dev.

---

## TypeScript: Full Type Safety

Type your messages so missing keys are caught at compile time.

```ts
// global.d.ts (or types/index.d.ts)
import es from '../messages/es.json';

type Messages = typeof es;

declare global {
  interface IntlMessages extends Messages {}
}
```

Now `t('nonexistent')` is a TypeScript error. This is especially important when keys are added to one locale and forgotten in the other.

---

## Interpolation, Plurals, Rich Text

```json
{
  "greeting": "Hola, {name}",
  "items": "{count, plural, =0 {Sin resultados} one {# resultado} other {# resultados}}",
  "bold": "Lee los <link>términos</link>"
}
```

```tsx
// Interpolation
t('greeting', { name: 'Ana' })

// Plurals
t('items', { count: 3 })

// Rich text (Client Component only for JSX tags)
t.rich('bold', {
  link: (chunks) => <a href="/terms">{chunks}</a>
})
```

---

## Navigation (locale-aware)

Replace `next/link` and `next/navigation` with next-intl versions:

```ts
// navigation.ts (create once, import everywhere)
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, useRouter, usePathname } =
  createNavigation(routing);
```

```tsx
// Use Link instead of next/link — it forwards locale automatically
import { Link } from '@/i18n/navigation';

<Link href="/about">Sobre mí</Link>
// Renders as /about (es) or /en/about (en) automatically
```

---

## Layout Setup

```tsx
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;

  if (!routing.locales.includes(locale as any)) {
    notFound();
  }

  const messages = await getMessages();

  return (
    <html lang={locale}>
      <body>
        <NextIntlClientProvider messages={messages}>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

---

## next.config.ts

```ts
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

const nextConfig = {
  // your existing config
};

export default withNextIntl(nextConfig);
```

---

## generateMetadata with i18n

```ts
export async function generateMetadata({
  params
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'Metadata' });
  return { title: t('title') };
}
```

---

## Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `useTranslations` called in Server Component | Wrong hook in RSC | Switch to `await getTranslations()` |
| Locale is `undefined` in `request.ts` | Static rendering with no locale param | Add fallback to `defaultLocale` |
| Messages missing at runtime | `NextIntlClientProvider` not wrapping tree | Verify layout.tsx has provider |
| Link doesn't switch locale | Using `next/link` instead of next-intl's `Link` | Use `createNavigation` export |
| `/` doesn't redirect to default locale | Middleware matcher too narrow | Check matcher regex covers root |
| Type errors on `t('key')` | `global.d.ts` not set up | Add `IntlMessages` interface |
| Build fails: Can't resolve messages | Dynamic import path not literal | Use template literal `${locale}.json` format |

---

## Locale Switcher Pattern

```tsx
'use client';
import { useRouter, usePathname } from '@/i18n/navigation';
import { useLocale } from 'next-intl';

export function LocaleSwitcher() {
  const router = useRouter();
  const pathname = usePathname();
  const currentLocale = useLocale();

  function switchLocale(locale: string) {
    router.replace(pathname, { locale });
  }

  return (
    <div>
      {['es', 'en'].map((locale) => (
        <button
          key={locale}
          onClick={() => switchLocale(locale)}
          disabled={locale === currentLocale}
        >
          {locale.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
```

---

## Reference Files

- [references/setup.md](./references/setup.md) — Full copy-paste boilerplate for a new project
- [references/pitfalls.md](./references/pitfalls.md) — Deeper dives on edge cases: static rendering, Suspense boundaries, testing