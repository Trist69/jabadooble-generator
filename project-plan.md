# Dobble Generator — Project Plan

## Overview

A web application that generates printable Dobble card games with custom image themes. Built with Svelte + Material Design 3 (frontend) and Python FastAPI (backend).

---

## Dobble Math Primer

For a prime power `n`, the game produces:
- **n² + n + 1** unique cards
- **n + 1** symbols per card
- Any two cards share **exactly 1 symbol**

Standard Dobble uses `n = 7` → **57 cards**, **8 symbols each**, requiring **57 unique symbols**.

---

## Architecture

```
dobble-generator/
├── frontend/               # Svelte + TypeScript + MUI Web Components
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/   # UI components
│   │   │   ├── stores/       # Svelte stores (state)
│   │   │   └── utils/        # Dobble math, helpers
│   │   └── routes/           # SvelteKit pages
│   └── tests/
├── backend/                # Python FastAPI
│   ├── app/
│   │   ├── api/              # Route handlers
│   │   ├── core/             # Dobble engine, PDF generation
│   │   ├── models/           # Pydantic models
│   │   └── services/         # Library, image, cartoonize services
│   └── tests/
└── docker-compose.yml
```

---

## Phases

### Phase 1 — Project Setup & Scaffolding
**Goal:** Working skeleton with CI-ready structure.

- [ ] Scaffold SvelteKit project with TypeScript + MUI Web Components
- [ ] Scaffold FastAPI project with folder structure and Pydantic models
- [ ] Set up docker-compose (frontend + backend + optional local storage)
- [ ] Configure linting, formatting (ESLint/Prettier for TS, Ruff/Black for Python)
- [ ] Set up test frameworks (Vitest for frontend, Pytest for backend)
- [ ] Basic health-check route on backend + frontend loads without errors

**Deliverable:** `docker-compose up` serves a blank Svelte app talking to a FastAPI health endpoint.

---

### Phase 2 — Dobble Engine (Core Logic)
**Goal:** Pure algorithmic module, fully tested, no UI.

- [ ] Implement projective plane algorithm (finite field construction for prime-power n)
- [ ] Support configurable order `n` (default 7 → 57 cards / 8 symbols)
- [ ] Unit tests: verify any 2 cards share exactly 1 symbol, correct card/symbol counts
- [ ] Expose as importable Python module and as `/api/engine/generate` endpoint

**Deliverable:** Backend endpoint returns a card matrix (list of symbol-index lists) that passes all Dobble invariants.

---

### Phase 3 — Image Library Management
**Goal:** Users can create themed libraries of symbols.

- [ ] Data model: `Library { id, name, theme, symbols[] }`, `Symbol { id, url, label }`
- [ ] CRUD API endpoints: create/list/delete libraries, add/remove symbols
- [ ] Image source adapters:
  - JSON file import (URL list + metadata)
  - Direct image upload (multipart)
  - External API fetch (Harry Potter API as first example)
- [ ] Local file storage for uploaded/fetched assets (configurable path)
- [ ] Frontend: Library management page — create library, browse symbols, import sources

**Deliverable:** User can create a "Harry Potter" library, fetch characters from the HP API, see them in the UI.

---

### Phase 4 — Cartoonize Feature
**Goal:** Auto-stylize imported images for a consistent card look.

- [ ] Research and integrate a lightweight cartoonization approach (e.g. OpenCV edge-detection + colour quantization, or a small ML model)
- [ ] Expose `/api/images/cartoonize` endpoint (accepts image URL or upload, returns processed image)
- [ ] Batch cartoonization for an entire library
- [ ] Frontend: Toggle "cartoonize" per symbol or per library; preview before/after

**Deliverable:** Raw character photos can be converted to cartoon-style icons in one click.

---

### Phase 5 — Card Generation & Display
**Goal:** Generate a visual Dobble deck from a library.

- [ ] Backend: `/api/games/generate` — takes library ID + order n → assigns symbols to card matrix → returns card definitions (list of symbol URLs per card)
- [ ] Frontend: Game preview page — renders card grid, each card as an SVG/canvas circle with symbols placed without overlap
- [ ] Symbol layout algorithm: distribute n+1 symbols evenly on a circular card face
- [ ] Support card customisation: card size, background colour, symbol scale

**Deliverable:** User selects a library, clicks "Generate", sees a full deck preview in the browser.

---

### Phase 6 — PDF Export
**Goal:** Print-ready PDF output, 2 cards per A4 page.

- [ ] Backend: `/api/games/export/pdf` — uses ReportLab or WeasyPrint
- [ ] Layout: 2 cards per A4 page (landscape or portrait), centred with bleed marks
- [ ] Embed images at print resolution (300 dpi target)
- [ ] Frontend: "Export PDF" button → downloads file

**Deliverable:** User downloads a PDF, prints it, and gets a playable Dobble deck.

---

### Phase 7 — Polish & UX
**Goal:** Clean, friendly UI for non-technical users (kids' parents).

- [ ] Responsive layout (desktop + tablet)
- [ ] Loading states, error messages, empty states
- [ ] Onboarding flow: "Create your first library" wizard
- [ ] Saved games list (past generated decks)
- [ ] Share / send feature (link or email a PDF)

---

## Tech Decisions

| Concern | Choice | Reason |
|---|---|---|
| Frontend framework | SvelteKit | Lightweight, fast, great DX |
| UI components | MUI Web Components (M3) | Design consistency, web standards |
| Backend | FastAPI + Pydantic | Fast, typed, async-ready |
| PDF generation | ReportLab | Fine-grained layout control |
| Cartoonize | OpenCV (cv2) | No GPU required, runs anywhere |
| Image storage | Local FS (Docker volume) | Simple to start; swap for S3 later |
| Testing | Pytest + Vitest | Idiomatic for each stack |

---

## Milestones

| # | Milestone | Phase(s) |
|---|---|---|
| M1 | Skeleton running in Docker | 1 |
| M2 | Dobble engine tested & exposed | 2 |
| M3 | HP library importable & browsable | 3 |
| M4 | Cartoon symbols in library | 4 |
| M5 | Deck preview in browser | 5 |
| M6 | PDF download works end-to-end | 6 |
| M7 | Production-ready UX | 7 |
