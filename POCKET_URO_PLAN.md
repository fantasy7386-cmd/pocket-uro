# Pocket URO — Implementation Plan

> **Spec**: `POCKET_URO_SPEC.md` (v1.1.0)  
> **Date**: 2026-04-19

---

## Phase Overview

| Phase | Description | Deliverable | Depends On |
|-------|-------------|-------------|------------|
| **P0** | Repo setup + scaffold | Empty SPA shell with routing + access gate | — |
| **P1** | Patient Education module | Browsable articles (port from Pocket PPu) | P0 |
| **P2** | PPu Notes module | Browsable + admin-editable notes (port from PPu) | P0 |
| **P3** | Tips & Guide module | Markdown-rendered tips + admin editing | P0 |
| **P4** | Textbook Knowledge module | Slide viewer with image loading | P0 |
| **P5** | Cross-module features | Global search + favorites + home grid counts | P1–P4 |
| **P6** | Service Worker + PWA | Offline support, caching, manifest | P5 |
| **P7** | Polish + deploy | Final QA, access codes, GitHub Pages | P6 |

**P1–P4 are independent** and can be built in parallel or any order after P0.

---

## P0: Repo Setup + Scaffold

### Tasks

1. Create `pocket-uro` directory (local, init git repo)
2. Create `index.html` with:
   - HTML skeleton: `<div id="app">` root
   - CSS: Design tokens (4 module colors, typography, spacing)
   - CSS: Access gate overlay
   - CSS: Home screen 2×2 grid layout
   - CSS: Module view layout (header + back button + content area)
   - JS: Simple hash-based router (`#/`, `#/education`, `#/notes`, `#/tips`, `#/textbook`)
   - JS: Access gate logic (VALID_CODES, localStorage check)
   - JS: Navigation helpers (pushView, popView, breadcrumb update)
3. Create placeholder `manifest.json` + icons
4. Copy data + assets from pocket-ppu to pocket-uro:
   - `data.json` (278 KB, Patient Education)
   - `teaching-notes.json` (19 KB, PPu Notes)
   - `tips-guide.json` (22 KB, Tips & Guide)
   - `textbook-data/` (2.7 MB, 12 chapter JSONs)
   - `images/textbook/` (155 MB, 1,679 WebP renders across 12 chapter folders — required for P4 slide viewer)
5. Add `lib/marked.min.js` (download from CDN, bundle locally)
6. Add iOS PWA meta tags in `<head>`:
   - `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` (cover handles iPhone notch)
   - `<meta name="apple-mobile-web-app-capable" content="yes">`
   - `<meta name="apple-mobile-web-app-status-bar-style" content="default">`
   - `<meta name="apple-mobile-web-app-title" content="Pocket URO">`
   - `<link rel="apple-touch-icon" href="apple-touch-icon.png">`
   - `<meta name="theme-color" content="#1a1a2e">`

### Acceptance

- App loads, shows access gate
- After entering valid code, shows home screen with 4 colored cards
- Tapping a card navigates to an empty module page with correct header color
- Back button returns to home
- Hash-based URLs work (direct linking)

---

## P1: Patient Education Module

### Tasks

1. Port article data loading from Pocket PPu
2. Build Category List view: 11 cards with article count
3. Build Article List view: articles within selected category
4. Build Article View: full-text display, scrollable
5. Wire navigation: Home → Category → Article List → Article
6. Admin editing (NEW in 1.1.0):
   - Edit article: title + content (textarea) + category dropdown
   - Add new article
   - Delete article (with confirmation)
   - Sync to GitHub (writes `data.json`)

### Acceptance

- All 61 articles browsable via category drill-down
- Article text renders correctly (plain text with line breaks)
- Back navigation works at every level
- Admin can edit, add, delete articles; non-admin sees read-only
- Sync to GitHub writes `data.json` correctly

---

## P2: PPu Notes Module

### Tasks

1. Port notes data loading from Pocket PPu
2. Build Section List view: 13 sections with subsection count
3. Build Subsection View: items as bullet list
4. Port admin editing UI:
   - Edit subsection items (textarea)
   - Add/insert/move/delete section
   - Add/insert subsection
   - Auto-renumber sections (Roman) and subsections (1. 2. 3.)
5. Port GitHub Sync button (token-based, same API flow)

### Acceptance

- All 13 sections, 49 subsections browsable
- Admin (with GH token) can edit, add, move, delete sections
- Sync to GitHub works (writes teaching-notes.json to pocket-uro repo)
- Non-admin sees read-only view, no edit buttons

---

## P3: Tips & Guide Module

### Tasks

1. Load `tips-guide.json`
2. Build Chapter List view: 13 chapter cards with subsection count
3. Build Subsection View:
   - Render `markdown` field via `marked.js` to HTML
   - Style rendered output: tables, code, lists, headings
   - Style doctor tags: detect `[xxx]` patterns → render as colored inline badges
4. Build admin editing UI:
   - Structural ops: add/insert/move/delete section & subsection (reuse P2 patterns)
   - Content editing:
     - Desktop: split-pane (textarea left, live preview right)
     - Mobile: toggle tabs (Edit / Preview)
   - Title editing: text input above markdown editor
   - Save to localStorage, sync to GitHub (tips-guide.json)
5. Markdown rendering configuration:
   - Enable tables, strikethrough
   - Sanitize output (no raw HTML injection)
   - Add custom renderer for `####` headings (styled sub-headers)

### Acceptance

- All 13 chapters, 59 subsections browsable
- Markdown renders correctly: tables, bold, lists, code, sub-headings
- Doctor tags `[小黃]` etc. render as inline badges
- Admin can edit markdown with live preview
- Sync to GitHub works

---

## P4: Textbook Knowledge Module

### Tasks

1. Load textbook JSON files (lazy: load chapter JSON on first access)
2. Build Chapter List view: 12 cards with icon, title, section/topic count
3. Build Section List view: sections within chapter
4. Build Topic List view: topics with badges (📝 exam question, 📄 text-only)
5. Build Topic View dispatched by `type`:
   - `slides`: Slide Viewer
     - Image display: `<img src="{slide.slide_image}">` (e.g. `images/textbook/ch01_stone/render/s1_s02.webp`)
     - Lazy image loading (only load visible + adjacent slides)
     - Slide navigation: swipe left/right + arrow buttons + slide counter
     - OCR text below image (collapsible): render `slide.text[]` as bullet lines
     - Skip slides where `slide.hidden === true`
   - `text_only`: Markdown rendered via `marked.js`
6. Topic Notes renderer (all topics): collapsible `notes` Markdown block above primary content
7. Admin editing (NEW in 1.1.0, levels ①②③):
   - ① Edit topic `notes` field (reuse Tips & Guide split-pane editor)
   - ② Edit slide `text[]` OCR array (textarea, newline-split)
   - ③ Add text-only topic: title + `markdown_content` + optional `has_exam_questions`; insertable at any position
   - Sync to GitHub (writes only the affected `textbook-data/tb_XX.json`)
8. Handle large data gracefully:
   - Show loading spinner while chapter JSON loads
   - Image placeholder while slide images load

### Acceptance

- All 12 chapters, 171 topics browsable
- Slide images load and display correctly
- Text-only topics render Markdown correctly
- Swipe/arrow navigation between slides works
- Exam question + text-only badges show on relevant topics
- OCR text visible below slides
- Admin can edit topic notes, OCR text, and add text-only topics
- Sync to GitHub writes correct chapter JSON
- Out of scope: reordering topics/slides (④), replacing slide images (⑤)

---

## P5: Cross-Module Features

### Tasks

1. **Global Search**:
   - Build search index on init (in-memory): title + content from all modules
   - Debounced input (300ms), min 2 chars
   - Results grouped by module with color badge
   - Click result → navigate to item
   - Search accessible from home + header icon within modules
2. **Favorites**:
   - Heart/star toggle on content items (articles, subsections, topics)
   - localStorage storage: `[{ module, id, title, timestamp }]`
   - Favorites screen: grouped by module
   - Home screen: favorites button (top-right)
3. **Home Screen Stats**:
   - Each module card shows live count (articles, sections, topics)
   - Loaded from data files on init
4. **Submission Link**:
   - Google Form URL constant
   - "Suggest Content" button on home (non-admin only)

### Acceptance

- Search finds content across all modules
- Search results are clickable and navigate correctly
- Favorites persist across sessions
- Home cards show correct counts

---

## P6: Service Worker + PWA

### Tasks

1. Create `sw.js`:
   - Pre-cache: index.html, JSON files, lib/marked.min.js, icons, manifest
   - Stale-while-revalidate for same-origin
   - Cache-first for textbook renders (immutable images)
   - Passthrough for external APIs (GitHub)
2. Create `manifest.json`:
   - `name`: "Pocket URO"
   - `short_name`: "Pocket URO"
   - `start_url`: "./"
   - `display`: "standalone" (full-screen PWA mode on iOS/Android)
   - `theme_color`: `#1a1a2e` (dark header; matches iOS status bar)
   - `background_color`: `#ffffff`
   - `icons`: 192×192 + 512×512 PNG with `"purpose": "any maskable"`
3. Register SW in index.html (after DOMContentLoaded)
4. Add `?reset` cache-bust handler
5. Add update detection: show "New version available" toast on SW update
6. iOS PWA verification:
   - Confirm `apple-touch-icon.png` (180×180) present
   - Confirm all `apple-mobile-web-app-*` meta tags in place (see P0 step 6)
   - `display: standalone` renders without Safari chrome after "Add to Home Screen"

### Acceptance

- App works offline after first load
- Textbook images cached after first view
- `?reset` clears all caches
- New version toast appears when SW updates

---

## P7: Polish + Deploy

### Tasks

1. Create `pocket-uro` GitHub repo
2. Final QA checklist:
   - [ ] All 61 articles load
   - [ ] All 49 PPu Notes subsections load
   - [ ] All 59 Tips & Guide subsections render Markdown correctly
   - [ ] All 171 textbook topics / 1,626 slides load
   - [ ] Global search works across all modules (including topic notes + text-only topics)
   - [ ] Favorites add/remove/persist
   - [ ] Admin editing works for Patient Ed, PPu Notes, Tips & Guide, Textbook (notes/OCR/text-only)
   - [ ] GitHub sync works for all four editable modules
   - [ ] Access gate blocks unauthorized users
   - [ ] Offline mode works
   - [ ] Mobile layout (iPhone) looks correct
   - [ ] Desktop layout looks correct
   - [ ] Back navigation / swipe-back works everywhere
   - [ ] ?reset clears cache
3. Enable GitHub Pages on `pocket-uro` repo (source: main branch, root)
4. Update access codes if needed
5. iPhone PWA install + test flow:
   - Open pages URL in mobile Safari
   - Tap Share → "Add to Home Screen"
   - Launch from Home Screen icon → verify full-screen standalone mode (no Safari bar)
   - Verify apple-touch-icon displays correctly
   - Test offline: enable Airplane Mode → reopen PWA → browse cached content
   - Test all four modules load on iPhone viewport
6. Test on Mac (Chrome) for desktop layout

### Acceptance

- App is live on GitHub Pages over HTTPS
- All QA items pass
- PWA installs cleanly on iPhone Home Screen with correct icon and name
- Standalone mode works without Safari chrome
- Offline mode serves cached JSON and previously-viewed slide images
- Admin can edit + sync from iPhone

---

## Implementation Notes

### Code Reuse from Pocket PPu

The following can be directly ported with minimal changes:
- Access gate HTML/CSS/JS
- GitHub Sync logic (token storage, SHA fetch, PUT file)
- PPu Notes editing UI (section CRUD, auto-renumber)
- Service Worker pattern

### New Code

- Hash-based router (Pocket PPu used tab bar, not routing)
- Home screen 2×2 grid
- Markdown rendering + editing (Tips & Guide)
- Textbook slide viewer (swipe + lazy image load)
- Textbook editing UI: topic notes editor, OCR text editor, text-only topic CRUD
- Patient Education article CRUD
- Text-only topic type dispatch in Topic View
- Cross-module search indexing (includes topic notes + text-only markdown)
- Unified favorites system

### Estimated Complexity

| Component | Lines (est.) | Complexity |
|-----------|-------------|------------|
| Router + navigation | ~150 | Low |
| Home screen | ~100 | Low |
| Patient Education + editing | ~350 | Low-Medium (port + new edit) |
| PPu Notes + editing | ~400 | Medium (port) |
| Tips & Guide + editing | ~500 | Medium-High (new) |
| Textbook viewer + editing (①②③) | ~700 | Medium-High (new) |
| Global search | ~220 | Medium |
| Favorites | ~100 | Low |
| SW + PWA | ~60 | Low (port) |
| CSS | ~550 | Medium |
| **Total** | **~3,130** | — |
