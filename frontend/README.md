# QuranRef Frontend

Vue 3 and TypeScript single-page app built with Vite. UI components come from PrimeVue 4 (Aura theme with a green preset), state lives in Pinia, routing uses Vue Router, reactive helpers come from VueUse, and HTTP calls use mande and fetch.

## Commands

```bash
bun install
bun run dev          # http://localhost:41149, /api is proxied to http://localhost:41148
bun run test         # Vitest unit and component tests (src/**/*.spec.ts)
bun run vue-tsc -b   # type check
bun run build        # type check, then production build into ../static
bun run preview      # serve the production build locally
```

Always use bun for this project, not npm, npx or node.

## Structure

- `src/main.ts`: creates the app, installs PrimeVue, the tooltip directive, the router and Pinia
- `src/QuranRefMainApp.vue`: application shell
- `src/router.ts`: routes
- `src/store.ts`: Pinia store (surah info, text types, selected translations, dark mode, auth, bookmarks)
- `src/type_defs.ts`: shared TypeScript interfaces
- `src/plugins/primevue.ts`: PrimeVue theme preset
- `src/components/`, `src/views/`: components and routed views

## Environment

`vite.config.ts` reads `.env` and `.env.production` through Vite's `loadEnv`. Variables already present in the process environment take priority, which is how the container setup overrides them.

- `VITE_API_BASE_URL`: API prefix used by the app (default `/api/v1`)
- `VITE_WEBSITE_BASE_URL`: public site URL
- `STATIC_URL`: base path of the production build (default `/static/`)
- `VITE_BACKEND_URL`: dev server proxy target for `/api` (default `http://localhost:41148`)

## Licensing note

PrimeVue and PrimeIcons are pinned to their MIT-licensed majors (PrimeVue 4.x, @primevue/themes 4.x, PrimeIcons 7.x). PrimeVue 5 and PrimeIcons 8 are distributed under the PrimeUI license, which is not open source. Do not bump them without a licensing decision.
