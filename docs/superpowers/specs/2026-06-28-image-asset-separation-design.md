# Design: Image Asset Separation (content-addressed files)

**Date:** 2026-06-28
**Status:** Approved in brainstorming; pending spec review
**Target version:** v3.8.0
**Affects:** `index.html`, `sw.js`, content JSON (`data.json`, `teaching-notes.json`, `tips-guide.json`, `textbook-data/*.json`), new `images/content/` directory

## Background / Problem

Two recent cold-start white-screens (v3.7.24 SW reload race, v3.7.25 boot race) were both *amplified* by a slow boot: `loadCore()` runs `Promise.all([data.json, teaching-notes.json, tips-guide.json])` and **data.json is 5.6 MB**. Investigation (2026-06-28) found **98% of data.json (5.5 MB) is 3 base64-embedded images** sitting inline in 3 article `text` fields (夜尿 / BCG / TURP comparison, all PDF-imported). Actual text is ~0.1 MB.

Root architectural flaw: **images (heavy, binary) are stored base64 in the same JSON the boot critical path must fully download on every cold start.** Images should be separate, on-demand assets — exactly like textbook slides (`images/textbook/**.webp` + SW `cacheFirst`), a mechanism the app already ships.

"Add an image anytime" is a core admin feature and MUST be preserved with unchanged UX.

## Goals

- Cold start downloads only text (~0.1 MB), not images → fast, stable, boot-race window minimized.
- "Add image" admin UX unchanged: 📷 → instant preview → sync.
- Adding images never re-bloats the boot path, regardless of count.
- Backward compatible: existing base64 images keep rendering during/after transition.
- One mechanism across all 4 image-bearing datasets (articles / notes / tips / textbook topics — they share `images[]`, `renderAttachments`, and the sync path).

## Non-Goals

- No change to text content, categories, or any non-image data.
- No orphaned-image garbage collection this round (deferred; files are small + cacheFirst).
- No native / TestFlight work (separately evaluated and declined).

## Data Model

Per-image object inside `entity.images[]`:

```
legacy / pending:  { data: "data:image/jpeg;base64,…", alt, caption, _pending?: true }
synced:            { ref:  "images/content/<sha256-16>.jpg", alt, caption }
```

- `ref`: repo-relative path. Filename = first 16 hex chars of SHA-256(raw image bytes) + extension (`.jpg` / `.png`, from the resize MIME at index.html:2043). Content-addressed → immutable → safe for `cacheFirst`.
- Render: `const src = img.ref || img.data;` — both forms render transparently.

## Add-image Flow (dual-state)

1. 📷 → `resizeImageToDataUrl(file, 1600, 0.8)` (unchanged) → push `{ data: base64, alt, caption, _pending: true }` to `_editorImages`.
2. Renders immediately from base64 — instant, identical to today.
3. On save: stored in `entity.images[]` (still base64 + `_pending`) → `markDirty` → localStorage override.

The admin never waits on a network round-trip to *see* the image; upload happens at sync.

## Sync (atomic ordering)

`syncAll()` gains a pre-pass before pushing each dirty dataset's JSON:

1. Collect all `_pending` images across dirty datasets.
2. For each: SHA-256 (SubtleCrypto) of raw bytes → path `images/content/<hash>.<ext>` → `ghPutFile` (content = raw image base64, `data:…;base64,` prefix stripped). Idempotent: same bytes → same path → re-push is harmless.
3. On success, mutate the image object in place: delete `data` + `_pending`, set `ref`.
4. **Only after ALL pending images for a dataset succeed** → push that dataset's slimmed JSON.

Failure handling:
- Image push fails → keep `data` + `_pending`, skip the JSON push for that dataset, retry next sync.
- Image push OK but JSON push fails → image file already in repo (harmless); JSON retried next sync.
- **Invariant: a pushed JSON never references a `ref` that is not already in the repo.**

`ghPutFile` already performs a base64 PUT via the GitHub Contents API (index.html:1871-1883) and is reused unchanged; for image files the content is the raw image base64.

## Migration (one-time, run on the computer — not the app)

Python script:
- Scan `data.json`, `teaching-notes.json`, `tips-guide.json`, `textbook-data/*.json`.
- Find base64 images in (a) `images[].data` and (b) inline `![](data:…)` inside text/markdown/notes fields.
- For each: decode → write `images/content/<hash>.<ext>` → replace with a `ref` (`images[].ref`; inline-markdown images are moved into `images[]` as a `ref`).
- Verify: re-read each file, assert no `data:image` remains, assert every `ref` file exists on disk, assert JSON still parses, report before/after sizes.
- Expected: data.json 5.6 MB → ~0.1 MB. Commit slimmed JSON + new image files in one commit.

**Behavior note (display position):** moving an inline `![](data:…)` image into `images[]` shifts its render position from *within the markdown body* to the *attachments gallery below the body* (where it also gains lightbox zoom). The 3 affected articles are PDF-imported single-sheet handouts where the image *is* the content, so this is acceptable (arguably better). True mid-text inline figures are out of scope this round.

## Service Worker / Offline

- `sw.js`: add a `cacheFirst` branch for `url.pathname.includes('/images/content/')`, mirroring the textbook-webp branch (immutable assets).
- `__downloadAll`: extend prefetch URL collection to also scan every dataset's `images[].ref`, so offline download covers article/notes/tips images, not just textbook webp.

## Compatibility & Versioning

- `img.ref || img.data` keeps any not-yet-migrated or not-yet-synced base64 working — zero content breakage.
- Bump `CACHE_VERSION` + brand-tag → **v3.8.0** (architecture change touching index.html + sw.js; per the SW CACHE_VERSION bump policy both must move together).

## Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Partial sync inconsistency | Atomic ordering: images first, JSON only after all succeed. |
| Stale device serving old data.json (with base64) | `staleWhileRevalidate` refreshes in background; old base64 still renders meanwhile. |
| SHA-256 collision | Negligible; content-addressed by cryptographic hash. |
| Orphaned image files after delete/replace | Accepted this round (no GC); files small + cacheFirst. |

## Verification Plan

- **Migration:** data.json < 200 KB; zero `data:image` remaining; every `ref` resolves to a file; all JSON valid.
- **Cold start (Playwright, existing harness):** boot loads ~0.1 MB; render fast; the v3.7.25 race test still reports 0 errors.
- **Functional:** add image → sync → reload in a clean context → image renders from `ref`; a legacy base64 image still renders.
- **Offline:** `__downloadAll` includes the new image paths.
- **Live:** Pages built; brand-tag + sw both v3.8.0.
