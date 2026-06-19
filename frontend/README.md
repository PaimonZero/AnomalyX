# AnomalyX Frontend

React + TypeScript + Vite frontend for the AnomalyX AML prototype.

## Run locally

```bash
npm install
npm run dev
```

Copy `.env.example` to `.env.local`, then set `VITE_API_TOKEN` to the same local token as backend `AUTH_TOKEN`.

During `npm run dev`, requests to `/api/*` are proxied to `http://127.0.0.1:8000`, so the local frontend does not require backend CORS configuration. Set `VITE_API_BASE_URL` only when the API is hosted elsewhere.

## Structure

- `src/app` — app bootstrap, providers and routing.
- `src/layouts` — page-level application shells.
- `src/features` — business features; each feature owns its pages, components, hooks and API calls.
- `src/shared` — reusable API infrastructure, types, utilities and UI primitives.
- `src/styles` — global tokens and base styles.
