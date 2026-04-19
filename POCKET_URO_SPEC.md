# Pocket URO — Specification

> **Version**: 1.1.0  
> **Date**: 2026-04-19  
> **Predecessor**: Pocket PPu (`pocket-ppu` repo, 1887-line SPA)

> **Changelog 1.1.0 (2026-04-19)**: All four modules now admin-editable. Patient Education gains article CRUD. Textbook Knowledge gains per-topic notes (Markdown), inline OCR text editing, and text-only topic insertion (levels ①②③). Levels ④ (topic/slide reordering) and ⑤ (slide image replacement) remain out of scope.

---

## 1. Overview

Pocket URO is a mobile-first PWA for urology residents and attending physicians.
It consolidates four knowledge modules into a single offline-capable app:

| Module | Color | Data Source | Content |
|--------|-------|-------------|---------|
| **Patient Education** | Blue `#2980b9` | `data.json` | 61 TMUA patient education articles across 11 categories |
| **PPu Notes** | Green `#27ae60` | `teaching-notes.json` | 13 sections, 49 subsections of teaching notes |
| **Tips & Guide** | Orange `#e67e22` | `tips-guide.json` | 13 chapters, 59 subsections of clinical tips (Markdown) |
| **Textbook Knowledge** | Purple `#8e44ad` | `textbook-data/tb_01–12.json` | 12 chapters, 171 topics, 1,626 slides (PPT renders) |

**Target users**: Urology residents at the user's hospital (read-only), with Admin editing capability.

---

## 2. Architecture

### 2.1 Constraints (carried from Pocket PPu)

- **Single-page SPA**: one `index.html`, zero build tools, no framework
- **Pure static hosting**: GitHub Pages (`pocket-uro` repo)
- **Offline-first**: Service Worker with stale-while-revalidate
- **No backend**: all data in JSON files; editing persists via localStorage + GitHub API sync

### 2.2 File Structure

```
pocket-uro/
├── index.html              # The entire SPA
├── sw.js                   # Service Worker
├── manifest.json           # PWA manifest
├── icon-192.png
├── icon-512.png
├── apple-touch-icon.png    # 180×180 iOS Home Screen icon
├── data.json               # Patient Education articles
├── teaching-notes.json     # PPu Notes
├── tips-guide.json         # Tips & Guide
├── textbook-data/
│   └── tb_01.json … tb_12.json    # 12 chapter metadata files (~2.7 MB total)
├── images/
│   └── textbook/
│       ├── ch01_stone/render/sY_sNN.webp
│       ├── ch02_prostate/render/sY_sNN.webp
│       ├── ...
│       └── ch12_trauma/render/sY_sNN.webp    # 1,679 WebP slide renders, ~155 MB total across 12 chapters
└── lib/
    └── marked.min.js       # Markdown parser (~7 KB gzipped)
```

**Chapter folder naming**: `ch01_stone`, `ch02_prostate`, `ch03_kidney`, `ch04_uc`, `ch05_genital_ca`, `ch06_adrenal`, `ch07_voiding`, `ch08_male_repro`, `ch09_pediatric`, `ch10_infection`, `ch11_emergency`, `ch12_trauma`.

### 2.3 External Dependencies

| Library | Purpose | Size | Load Strategy |
|---------|---------|------|---------------|
| `marked.js` | Markdown → HTML rendering for Tips & Guide | ~40 KB (~7 KB gzip) | Bundled in `lib/`, cached by SW |

No other external libraries. All UI is hand-written CSS + vanilla JS.

---

## 3. Navigation & UI

### 3.1 Home Screen

A **2×2 grid** of module cards, each showing:
- Module icon/emoji
- Module name
- Content count (e.g., "61 articles", "171 topics")
- Module accent color as left border or gradient

Above the grid:
- **Global search bar** (cross-module full-text search)
- **Favorites button** (top-right corner)

Below the grid (small text):
- **Submission link** (Google Form for non-admin users to suggest content)

### 3.2 Navigation Pattern

```
Home ──┬── Patient Education ── Category List ── Article View
       ├── PPu Notes ── Section List ── Subsection View
       ├── Tips & Guide ── Chapter List ── Subsection View (Markdown rendered)
       └── Textbook Knowledge ── Chapter List ── Section List ── Topic/Slide View
```

- **Back navigation**: Top-left back button + swipe-right gesture (mobile)
- **Breadcrumb**: Shown as `Module > Section > Item` in the header area
- **No tab bar**: Home is the hub; each module is a full-screen drill-down

### 3.3 Responsive Layout

- **Mobile** (< 768px): Single-column, full-width cards, touch-optimized (44px tap targets)
- **Desktop** (≥ 768px): Max-width 800px centered container, same layout

---

## 4. Data Layer

### 4.1 Patient Education — `data.json`

Existing format (unchanged from Pocket PPu):

```jsonc
{
  "categories": [
    { "id": "cat_01", "name": "泌尿道結石", "count": 8 }
  ],
  "articles": [
    {
      "id": "art_001",
      "category": "cat_01",
      "title": "...",
      "content": "plain text body...",
      "source_url": "https://..."
    }
  ]
}
```

### 4.2 PPu Notes — `teaching-notes.json`

Existing format (unchanged):

```jsonc
{
  "version": "1.0.0",
  "updated": "2026-03-27",
  "author": "...",
  "total_sections": 13,
  "sections": [
    {
      "id": "tn_00",
      "number": "I",
      "title": "...",
      "full_title": "I. ...",
      "subsections": [
        {
          "title": "1. ...",
          "items": ["plain text", "plain text", "..."]
        }
      ]
    }
  ]
}
```

### 4.3 Tips & Guide — `tips-guide.json` (NEW)

```jsonc
{
  "version": "1.0.0",
  "updated": "2026-04-06",
  "total_sections": 13,
  "total_subsections": 59,
  "sections": [
    {
      "id": "tg_01",
      "number": "I",
      "title": "急診評估與處置",
      "full_title": "I. 急診評估與處置",
      "subsections": [
        {
          "id": "tg_01_01",
          "title": "Stone 處置流程",
          "markdown": "1. Fever? CRE?\n2. Image...\n- **Urosepsis...**"
        }
      ]
    }
  ]
}
```

Key difference from PPu Notes: `markdown` field (single string) instead of `items[]` array.

### 4.4 Textbook Knowledge — `textbook-data/tb_XX.json`

Existing format (unchanged):

```jsonc
{
  "id": "tb_01",
  "number": "I",
  "title": "結石",
  "icon": "🪨",
  "sections": [
    {
      "id": "tb_01_01",
      "title": "結石疾病",
      "source_file": "1-1 結石疾病 (2022).pptx",
      "total_slides": 76,
      "topics": [
        {
          "id": "t01",
          "type": "slides",                // NEW (1.1.0): "slides" | "text_only"; default "slides" for backward compat
          "title": "臨床表現與鑑別診斷",
          "slide_count": 2,
          "has_exam_questions": true,      // topic-level flag (plural)
          "has_hjh_content": false,        // reserved flag from data pipeline (doctor-attributed content); UI surface TBD
          "notes": "Admin-added Markdown. Rendered above primary content. Optional.",  // NEW (1.1.0, level ①)
          "slides": [
            {
              "slide_num": 2,
              "text": ["Acute flank pain D/D", "D/D:"],     // user-visible caption lines; admin-editable (1.1.0, level ②)
              "ocr_text": "Acute flank pain D/D and survey\n...",  // raw OCR archive; not admin-edited, used for search indexing
              "has_exam_question": true,   // slide-level flag (singular — note difference from topic's plural form)
              "slide_image": "images/textbook/ch01_stone/render/s1_s02.webp",  // full repo-relative path to WebP render
              "hidden": false              // slide visibility flag from pipeline; UI treats `true` as skipped
            }
          ]
        },
        {
          "id": "t_extra_01",
          "type": "text_only",             // NEW (1.1.0, level ③): Markdown-only topic, no slides
          "title": "2026 guideline update",
          "has_exam_questions": false,
          "notes": "optional notes",
          "markdown_content": "# Header\n\nBody text..."
        }
      ]
    }
  ]
}
```

---

## 5. Module Specifications

### 5.1 Patient Education (Blue `#2980b9`)

**View Mode** (all users):

- **Category List**: 11 category cards with article count badge
- **Article List**: Articles within selected category, sorted by ID
- **Article View**: Full-text display with back button
- **Search**: Title + body full-text search, results show category badge

**Admin Edit Mode** (NEW in 1.1.0):

- Edit article: title + content (plain-text `<textarea>`) + category dropdown
- Add new article (select category, fill title + content)
- Delete article (with confirmation)
- `source_url` is preserved as "original reference" metadata — not re-fetched from TMUA
- Save flow: Edit → localStorage → Sync to GitHub (writes `data.json`)

Editing intentionally diverges from TMUA — Pocket URO becomes the authoritative local version, with `source_url` retained for citation.

### 5.2 PPu Notes (Green `#27ae60`)

**Behavior**: Identical to current Pocket PPu v2.

- **Section List**: 13 sections (Roman numeral I–XIV)
- **Subsection View**: Items displayed as bullet list
- **Admin Editing**: Section/subsection CRUD, plain-text textarea
  - Add/insert section
  - Add/insert subsection
  - Move section up/down
  - Delete section (with confirmation)
  - Sync to GitHub

### 5.3 Tips & Guide (Orange `#e67e22`)

**View Mode** (all users):
- **Chapter List**: 13 chapter cards, each showing subsection count
- **Subsection View**: Markdown rendered to HTML via `marked.js`
  - Tables render as styled `<table>` elements
  - Doctor attribution tags `[小黃]` rendered with a distinct inline badge style
  - `####` sub-headings render as styled sub-headers within the subsection
  - Code/backtick content renders as inline code badges

**Admin Edit Mode**:
- Same structural operations as PPu Notes (add/move/delete section & subsection)
- Content editing: **split-pane layout**
  - Left: `<textarea>` with raw Markdown
  - Right: Live HTML preview (re-rendered on each keystroke via `marked.js`)
  - On mobile (< 768px): Toggle between Edit and Preview tabs (not side-by-side)
- Save flow: Edit → localStorage → Sync to GitHub
- Subsection title is editable as a separate text input above the Markdown editor

### 5.4 Textbook Knowledge (Purple `#8e44ad`)

**View Mode** (all users):
- **Chapter List**: 12 chapter cards with icon, title, topic count
- **Section List**: Sections within a chapter (e.g., "1-1 結石疾病")
- **Topic List**: Topics within a section, with badges:
  - 📝 Exam question indicator (yellow badge)
  - 📄 Text-only topic indicator (for `type: "text_only"`)
  - Topic title + slide count (or word count for text-only)
- **Topic Notes** (all topics): collapsible Markdown-rendered `notes` field shown at top of Topic View, visually distinct from primary content (NEW 1.1.0, level ①)
- **Topic View** dispatches by `type`:
  - `slides` (default):
    - PPT slide rendered as image (full-width)
    - OCR text overlay below image for accessibility/search
    - Swipe left/right or arrow buttons to navigate slides
    - Slide counter: "3 / 76"
  - `text_only` (NEW 1.1.0, level ③): Markdown rendered via `marked.js` — no slide viewer

**Admin Edit Mode** (NEW in 1.1.0, scoped to levels ①②③):

1. **① Topic Notes** — edit `notes` Markdown field per topic
   - Reuses Tips & Guide split-pane editor (desktop) / tab toggle (mobile)
   - Rendered above primary content (slides or text_only body)
2. **② OCR Text** — edit `slides[].text` array per slide (the user-visible caption lines)
   - `<textarea>` with one line per newline; split on save
   - Used for correcting OCR errors or adding annotations
   - Note: `slides[].ocr_text` (raw OCR archive) is **not** directly editable; it remains as search-index source
3. **③ Add Text-Only Topic** — insert a new topic with `type: "text_only"`
   - Fields: title, `markdown_content`, optional `has_exam_questions`
   - Insertable at any position within a section's topic list
   - Displayed inline with slide-based topics in the Topic List

**Out of scope (deferred)**: topic/slide reordering (④), slide image replacement (⑤).

Save flow: Edit → localStorage → Sync to GitHub (writes only the affected `textbook-data/tb_XX.json`).

---

## 6. Cross-Module Features

### 6.1 Global Search

- Located on home screen (always visible) and accessible from within any module via header search icon
- Searches across ALL four modules simultaneously
- Results grouped by module with color-coded badges:
  - 🔵 Patient Education — matches in article title + body
  - 🟢 PPu Notes — matches in subsection items
  - 🟠 Tips & Guide — matches in subsection markdown (raw text, not rendered HTML)
  - 🟣 Textbook — matches in topic title + slide OCR text
- Results are clickable and navigate directly to the matched item
- Debounced input (300ms) to avoid excessive re-rendering
- Minimum query length: 2 characters

### 6.2 Favorites

- Unified favorites list across all modules
- Toggle favorite via heart/star icon on any content item
- Stored in `localStorage` as array of `{ module, id, title, timestamp }`
- Favorites screen accessible from home (top-right)
- Favorites grouped by module with accent color indicators

### 6.3 Submission (Non-Admin)

- "Suggest Content" button visible to non-admin users
- Links to a Google Form (URL configured in code, same as Pocket PPu design)
- Admin reviews submissions externally and adds content manually

---

## 7. Editing & Sync (Admin Only)

### 7.1 Admin Detection

Admin status is determined by the presence of a GitHub personal access token in localStorage (key: `ppu_gh_token`). This is the same mechanism as Pocket PPu.

- Non-admin users: Read-only across all modules
- Admin users: Edit buttons appear in all four modules (Patient Ed, PPu Notes, Tips & Guide, Textbook — scoped per 5.4)

### 7.2 Editable Modules

| Module | Editable | Edit Format |
|--------|----------|-------------|
| Patient Education | Yes (Admin) | Plain-text (title + content + category) |
| PPu Notes | Yes (Admin) | Plain-text items |
| Tips & Guide | Yes (Admin) | Markdown with live preview |
| Textbook Knowledge | Yes (Admin, scoped) | Topic notes (MD), OCR text, add text-only topic |

### 7.3 Sync to GitHub

Same mechanism as Pocket PPu:

1. Admin edits content in-app
2. Changes saved to localStorage immediately
3. "Sync" button uses GitHub API to:
   - Fetch current file SHA from repo
   - PUT updated JSON content via Contents API
   - Commit directly to `main` branch
4. Service Worker detects new version on next fetch and updates cache
5. Other users receive update on next app load (stale-while-revalidate)

**Sync targets**: `data.json` (Patient Education), `teaching-notes.json` (PPu Notes), `tips-guide.json` (Tips & Guide), `textbook-data/tb_XX.json` (Textbook — only the affected chapter file)

### 7.4 Conflict Resolution

Simple last-write-wins. Since only one admin exists, conflicts are not expected.
If the SHA check fails (file was modified externally), show an error and offer to force-overwrite or reload.

---

## 8. Access Control

### 8.1 Gate Screen

- Full-screen overlay on first visit
- Single text input for employee ID (員編)
- Validated against `VALID_CODES` array in index.html
- On success: code saved to localStorage, gate hidden, `init()` called
- On failure: error message shown

### 8.2 Code Management

- Codes stored in `VALID_CODES` array within index.html (same as Pocket PPu)
- Current codes: `ADMIN`, `123944` (總院吳), `Y08594` (雲林吳)
- Admin manages codes by editing the array and deploying

### 8.3 Access Logging

- Optional Google Sheet logging via Apps Script endpoint
- Logs: code, timestamp, device type, user agent
- Endpoint URL configured via `LOG_ENDPOINT` constant (empty = disabled)

---

## 9. Service Worker & Caching

### 9.1 Strategy

- **Install**: Pre-cache core assets (index.html, all JSON files, lib/marked.min.js, icons)
- **Activate**: Delete old caches, claim all clients
- **Fetch**: 
  - Same-origin: Stale-while-revalidate (serve cache, update in background)
  - External (GitHub API): Passthrough (never cache)
  - Textbook renders (`images/textbook/**/*.webp`): Cache-first (WebP files are immutable per deployment)

### 9.2 Cache Assets

```
./
./index.html
./data.json
./teaching-notes.json
./tips-guide.json
./manifest.json
./icon-192.png
./icon-512.png
./apple-touch-icon.png
./lib/marked.min.js
```

Textbook JSON files (`textbook-data/tb_XX.json`) and render images (`images/textbook/**/*.webp`) are cached on first access (not pre-cached, to avoid large initial download on PWA install).

### 9.3 Version Bumping

- `CACHE_VERSION` in sw.js must be updated on every deployment
- Triggers old cache invalidation and re-download on users' devices
- The `?reset` URL parameter force-clears all caches and SW registration (emergency escape hatch)

---

## 10. Migration from Pocket PPu

### 10.1 New Repository

- Create new repo `pocket-uro` (separate from `pocket-ppu`)
- Copy data + assets: `data.json`, `teaching-notes.json`, `tips-guide.json`, `textbook-data/` (2.7 MB), and `images/textbook/` (155 MB WebP renders across 12 chapter folders)
- New index.html built from scratch incorporating all four modules
- Note: 155 MB images is within GitHub Pages 1 GB repo limit and 100 GB/month bandwidth soft limit

### 10.2 Pocket PPu Coexistence

- Pocket PPu remains live at its current URL (no breaking changes)
- Pocket URO is deployed at a new GitHub Pages URL
- PPu Notes data is shared: both apps read/write `teaching-notes.json` via GitHub API
  - Potential future: Pocket PPu reads teaching-notes.json from pocket-uro repo (single source of truth)

### 10.3 What Changes

| Aspect | Pocket PPu | Pocket URO |
|--------|-----------|------------|
| Modules | 2 (Education + Notes) | 4 (+ Tips & Guide + Textbook) |
| Entry point | Tab bar (Articles / Notes) | Home grid (4 modules) |
| Tips & Guide | N/A | Markdown rendering + editing |
| Textbook | Separate preview page | Integrated module |
| Search | Per-module | Cross-module global search |
| Favorites | Per-module | Unified across modules |

---

## 11. Non-Goals (Out of Scope)

- Multi-user editing / collaboration (Admin-only is sufficient)
- User accounts / authentication server (employee ID gate is sufficient)
- Full-text indexing / Elasticsearch (in-memory JS search is sufficient for this data size)
- Build tooling (Webpack, Vite, etc.) — zero-build constraint preserved
- Native app (iOS/Android) — PWA with offline support is sufficient
- Real-time sync between devices (GitHub API sync is the single mechanism)
- Analytics beyond basic access logging
- Textbook topic/slide reordering (level ④) and slide image replacement (level ⑤) — deferred until ①②③ are validated in production
