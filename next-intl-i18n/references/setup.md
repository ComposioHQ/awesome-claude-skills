# next-intl Setup Boilerplate

Full copy-paste starting point for a Next.js App Router project with next-intl. Assumes TypeScript, Spanish as default locale.

---

## 1. Install

```bash
npm install next-intl
```

---

## 2. messages/es.json

```json
{
  "HomePage": {
    "title": "Bienvenida",
    "description": "Descripción de la página"
  },
  "Nav": {
    "home": "Inicio"
  },
  "Metadata": {
    "title": "Mi App"
  }
}
```

## 3. messages/en.json

```json
{
  "HomePage": {
    "title": "Welcome",
    "description": "Page description"
  },
  "Nav": {
    "home": "Home"
  },
  "Metadata": {
    "title": "My App"
  }
}
```

---

## 4. i18n/routing.ts

```ts
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['es', 'en'],
  defaultLocale: 'es',
  localePrefix: 'as-needed'
});
```

---

## 5. i18n/request.ts

```ts
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

## 6. i18n/navigation.ts

```ts
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, useRouter, usePathname, getPathname } =
  createNavigation(routing);
```

---

## 7. middleware.ts (project root)

```ts
import createMiddleware from 'next-intl/middleware';
import { routing } from './i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};
```

---

## 8. next.config.ts

```ts
import createNextIntlPlugin from 'next-intl/plugin';
import type { NextConfig } from 'next';

const withNextIntl = createNextIntlPlugin('./i18n/request.ts');

const nextConfig: NextConfig = {};

export default withNextIntl(nextConfig);
```

---

## 9. types/global.d.ts

```ts
import es from '../messages/es.json';

type Messages = typeof es;

declare global {
  interface IntlMessages extends Messages {}
}
```

---

## 10. app/[locale]/layout.tsx

```tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

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

## 11. app/[locale]/page.tsx (Server Component example)

```tsx
import { getTranslations } from 'next-intl/server';

export async function generateMetadata({
  params
}: {
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: 'Metadata' });
  return { title: t('title') };
}

export default async function HomePage() {
  const t = await getTranslations('HomePage');
  return (
    <main>
      <h1>{t('title')}</h1>
      <p>{t('description')}</p>
    </main>
  );
}
```