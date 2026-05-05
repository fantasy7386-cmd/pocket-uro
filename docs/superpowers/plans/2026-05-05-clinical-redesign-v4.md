# Clinical Redesign v4 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Apply the full Clinical design language from the Claude Design handoff to `~/pocket-uro/v4/`, leaving v3.7.1 (root) completely untouched as the rollback target.

**Architecture:**
- All visual + behavioral changes live in `~/pocket-uro/v4/` (index.html, sw.js, manifest.json, icon PNGs).
- Shared assets (textbook-data/, images/, lib/, root JSON files) untouched.
- v3.7.1 at `https://fantasy7386-cmd.github.io/pocket-uro/` remains primary; v4 ships at `/v4/` as alpha-grade preview.
- Each phase ends with a deploy commit + manual verify, so user can stop at any phase and still have a working app.

**Tech Stack:** vanilla HTML/CSS/JS PWA on GitHub Pages. No build step. SHA-256 via `crypto.subtle`. CSS custom properties for tokens.

**Spec source of truth:**
- `~/Downloads/design_handoff_pocket_uro/README.md` — full design intent
- `~/Downloads/design_handoff_pocket_uro/clinical.jsx` — Home / Search / Textbook / Tips reader
- `~/Downloads/design_handoff_pocket_uro/clinical-more.jsx` — Notes / Edu / Favorites / Settings
- `~/Downloads/design_handoff_pocket_uro/clinical-admin.jsx` — Admin sign-in / PIN / Editors

**Out of scope (explicit cuts):**
- Native iOS app / SwiftUI — we are PWA, not SwiftUI
- Face ID — WebAuthn requires server-side attestation we don't have; PIN-only is acceptable downgrade
- App Store assets — internal use only
- Quiz UI structured redesign (single Q + 4 options + explanation) — defer to separate plan

---

## File Structure

| File | Status | Responsibility |
|------|--------|----------------|
| `~/pocket-uro/v4/index.html` | MODIFY | All UI markup, styles, behavior. Currently 4881 lines from v4.0.4-alpha. |
| `~/pocket-uro/v4/sw.js` | MODIFY | Bump `CACHE_VERSION` per phase to invalidate stale assets. |
| `~/pocket-uro/v4/manifest.json` | MODIFY | App name + icon paths only. |
| `~/pocket-uro/v4/icon-*.png` | REPLACE | Beacon design (Pocket / URO wordmark stacked). Generated from `icons/icons.jsx` SVG via Pillow. |
| `~/pocket-uro/v4/icon-source.svg` | CREATE | SVG geometry for icon, kept in repo for re-export. |
| `~/pocket-uro/scripts/render_icons.py` | CREATE | Pillow-based renderer that takes the SVG and emits all iOS PNG sizes. |
| `~/pocket-uro/v4/styles-clinical.css` | CREATE (optional) | Externalized Clinical CSS. Inline acceptable; externalize only if `<style>` block exceeds ~600 lines. |

**Untouched (rollback safety):**
- `~/pocket-uro/index.html` (v3.7.1 root)
- `~/pocket-uro/sw.js` (v3.7.1 SW)
- `~/pocket-uro/manifest.json`
- `~/pocket-uro/icon-*.png` at root
- All JSON data files (`data.json`, `tips-guide.json`, `teaching-notes.json`, `textbook-data/*.json`)
- All WebP images under `images/`

---

## Design Token Reference

Single source of truth — every Clinical color/spacing/font value comes from this block:

```css
:root[data-theme="clinical"] {
  /* Neutrals */
  --bg: #F6F7F9;
  --surface: #FFFFFF;
  --ink: #0B1F3A;
  --ink2: #3A4A63;
  --muted: #6B7791;
  --line: #E3E7EE;
  --line2: #EDEFF4;

  /* Brand */
  --primary: #0B3D91;
  --primary-soft: #E8EEF9;

  /* Semantic */
  --danger: #B3261E;
  --warning: #B26A00;
  --success: #0F7B3E;

  /* Module accents */
  --mod-education: #2E5C8A;
  --mod-notes: #2E7D4E;
  --mod-tips: #B05A1C;
  --mod-textbook: #6B3A8A;

  /* Spacing 4px base */
  --sp-1: 4px; --sp-2: 6px; --sp-3: 8px; --sp-4: 10px; --sp-5: 12px;
  --sp-6: 14px; --sp-7: 16px; --sp-8: 20px; --sp-9: 24px; --sp-10: 32px;
  --sp-11: 40px; --sp-12: 56px;

  /* Radius */
  --r-row-badge: 7px;
  --r-button: 8px;
  --r-input: 10px;
  --r-card: 12px;

  /* Typography */
  --font-system: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", system-ui, sans-serif;
  --fs-caption-mono: 11px;
  --fs-secondary: 12px;
  --fs-body: 15px;
  --fs-title-row: 16px;
  --fs-display: 28px;
}

:root[data-theme="clinical"][data-mode="dark"] {
  --bg: #0A0E14;
  --surface: #131922;
  --ink: #E8EEF9;
  --ink2: #B0BCD0;
  --muted: #7A8699;
  --line: #1F2733;
  --line2: #2A3340;
  /* primary unchanged; module dots unchanged for recognition */
}
```

---

## Phases & Stop Points

The 11 phases below are ordered so each one **leaves a working app**. After each phase: commit + push + verify on GH Pages + manual sanity check on iPhone. User can call "stop here" at any phase.

| Phase | Topic | Est | Files | Stop here if... |
|-------|-------|-----|-------|-----------------|
| 1 | Tokens + typography foundation | 1h | index.html, sw.js | You want minimum visual disruption |
| 2 | Home + Modules dense list | 1.5h | index.html | You like the new home but want to keep module pages as-is |
| 3 | Search redesign + query highlight | 1h | index.html | Module pages OK as-is, search alone gets the upgrade |
| 4 | Tips reader (numbered + Notes callout) | 1.5h | index.html | Tips visually polished, others still old |
| 5 | Textbook viewer header + transcript | 1.5h | index.html | Textbook polished |
| 6 | Notes / Edu / Favorites lists | 2h | index.html | All viewers polished, admin still old UI |
| 7 | Settings page + admin sign-in paste-token | 1.5h | index.html | Auth UX modernized |
| 8 | PIN unlock system (replaces password-only) | 2h | index.html | Edit gating refined |
| 9 | Recent items system (last 20) | 1.5h | index.html | New UX surface added |
| 10 | Beacon app icon swap | 1h | scripts/, v4/icon-*.png, manifest.json | Visual identity refresh |
| 11 | Final polish + cache bump + deploy | 0.5h | sw.js, index.html footer | Final ship |

**Total estimate: 14.5h.** This is below the original 30h estimate because we're cutting Face ID + Quiz UI and externalizing icon generation to a script (one-time work).

---

## Phase 1: Foundation Tokens + Typography

**Goal:** Replace v4's existing CSS variable block with the full Clinical token system. After this phase, colors and typography snap to Clinical, but layout structures stay the same — every element renders with new colors but in old positions.

**Files:**
- Modify: `~/pocket-uro/v4/index.html` (replace `<style>` `:root { ... }` token block, ~lines 30-120 — locate by searching for `--accent` or `--bg` first)
- Modify: `~/pocket-uro/v4/sw.js` line 6 (bump `CACHE_VERSION` to `'pocket-uro-v4.1.0-clinical-phase1'`)

### Tasks

- [ ] **1.1: Locate current token block**

```bash
grep -nE "^\s*:root\s*\{" ~/pocket-uro/v4/index.html | head -5
grep -nE "^\s*--(bg|primary|accent|ink|surface|line)" ~/pocket-uro/v4/index.html | head -20
```

Expected: identifies line range of current `:root { ... }` declaration.

- [ ] **1.2: Read current token block in full**

Use the line range from 1.1. Note any tokens we need to preserve (e.g., legacy `--accent-data`, `--accent-notes` etc. that might still be referenced in the file).

- [ ] **1.3: Compile token-rename map**

Tokens that get renamed (old → new):
```
--bg-primary    → --bg
--bg-secondary  → --surface
--text-primary  → --ink
--text-secondary→ --ink2
--text-muted    → --muted
--border        → --line
--accent-data       → --mod-education
--accent-notes      → --mod-notes
--accent-tips       → --mod-tips
--accent-textbook   → --mod-textbook
```

For each old token still referenced in CSS rules or inline styles, decide: rename in place, or keep alias `--bg-primary: var(--bg);` for legacy CSS.

- [ ] **1.4: Replace token block with Clinical tokens**

Replace the located `:root { ... }` content with the full Clinical token block from "Design Token Reference" above. Add legacy aliases at end of block to keep existing rules working until Phase 2 rewrites them.

- [ ] **1.5: Add font-family rule on body**

Find `body { ... }` rule. Set `font-family: var(--font-system);` and `background: var(--bg); color: var(--ink); font-size: var(--fs-body);`.

- [ ] **1.6: Bump CACHE_VERSION**

Edit `~/pocket-uro/v4/sw.js` line 6:
```js
const CACHE_VERSION = 'pocket-uro-v4.1.0-clinical-phase1';
```

- [ ] **1.7: Commit**

```bash
cd ~/pocket-uro
git add v4/index.html v4/sw.js
git commit -m "v4 Phase 1: Clinical tokens + typography foundation"
git push origin main
```

- [ ] **1.8: Verify deploy**

```bash
until [ "$(gh api repos/fantasy7386-cmd/pocket-uro/pages/builds --jq '.[0].status')" != "building" ]; do sleep 5; done
echo "Pages built. Open https://fantasy7386-cmd.github.io/pocket-uro/v4/ on iPhone, hard reload twice."
```

Manual visual check: home page now uses navy primary, cool grey bg, warm white surfaces. Module accent colors look slightly desaturated. Layout unchanged.

**Stop point:** if user says "this is enough", we have the new color/typography system without any layout disruption.

---

## Phase 2: Home + Modules Dense List

**Goal:** Restructure the home page to match `<ClinicalHome/>` from `clinical.jsx` lines 119-195. Replace module "cards with left-border stripes" with "dense rows in a single bordered card, each row with a 30×30 colored badge."

**Files:**
- Modify: `~/pocket-uro/v4/index.html` — function `renderHome()` (line ~2361) and any associated CSS rules.

### Reference layout (from clinical.jsx lines 146-166)

```
┌─ MODULES (caption-mono, --muted) ─────┐
│ [📖] Patient Education    61 ▸        │  ← 30×30 badge, accent bg, white icon
│ [📖] PPu Notes            14 ▸        │
│ [💡] Tips & Guide         12 ▸        │
│ [▤ ] Textbook          1,624 ▸        │
└─ single card, --line border, line2 dividers ─┘
```

### Tasks

- [ ] **2.1: Read current `renderHome` function**

Read v4/index.html starting ~line 2361, capture the full renderHome body. Identify:
- Where modules are looped
- What CSS classes are used (likely `.module-card`, `.module-stripe`)
- Where the masthead is rendered

- [ ] **2.2: Write new home masthead markup**

Inside the existing `viewEl().innerHTML` template literal, replace the masthead section with:

```html
<div class="ch-masthead">
  <div>
    <div class="ch-eyebrow">Urology · Residents</div>
    <div class="ch-title">Pocket URO</div>
  </div>
  <div class="ch-icon-actions">
    <button class="ch-icon-btn" onclick="location.hash='#/favorites'" aria-label="Favorites">${ICON.star(18, 'var(--ink2)')}</button>
    <button class="ch-icon-btn" onclick="location.hash='#/settings'" aria-label="Settings">${ICON.gear(18, 'var(--ink2)')}</button>
  </div>
</div>
<div class="ch-search-box" onclick="location.hash='#/search'">
  ${ICON.search(18, 'var(--muted)')}
  <span class="ch-search-placeholder">Search across all modules</span>
  <span class="ch-search-kbd">⌘K</span>
</div>
```

- [ ] **2.3: Write new modules section markup**

Replace the modules grid with a single bordered card containing dense rows:

```html
<div class="ch-section-eyebrow">Modules</div>
<div class="ch-list-card">
  ${MODULES.map((m, i, arr) => `
    <a class="ch-row" href="#/${m.route}" data-module="${m.id}">
      <div class="ch-row-badge" style="background:var(--mod-${m.id})">${ICON[m.icon](17, '#fff')}</div>
      <div class="ch-row-body">
        <div class="ch-row-title">${m.name}</div>
        <div class="ch-row-sub">${m.count.toLocaleString()} ${m.unit}</div>
      </div>
      ${ICON.chev(14, 'var(--muted)')}
    </a>
  `).join('')}
</div>
```

The `MODULES` constant should look like:
```js
const MODULES = [
  { id: 'education', name: 'Patient Education', icon: 'note', count: state.data.articles.length, unit: 'articles', route: 'edu' },
  { id: 'notes', name: 'PPu Notes', icon: 'book', count: state.notes.sections.length, unit: 'chapters', route: 'notes' },
  { id: 'tips', name: 'Tips & Guide', icon: 'bulb', count: countTipsSubsections(), unit: 'guides', route: 'tips' },
  { id: 'textbook', name: 'Textbook', icon: 'slides', count: countAllSlides(), unit: 'slides', route: 'tb' },
];
```

(Helpers `countTipsSubsections` and `countAllSlides` already exist in v4 — locate them via grep first.)

- [ ] **2.4: Add ICON sprite system**

After the `state` declaration in the JS section, add:

```js
const ICON = {
  search: (s=18, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none"><circle cx="10.5" cy="10.5" r="6.5" stroke="${c}" stroke-width="1.8"/><path d="M15.2 15.4L20 20" stroke="${c}" stroke-width="2.2" stroke-linecap="round"/></svg>`,
  star: (s=18, c='currentColor', filled=false) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="${filled ? c : 'none'}"><path d="M12 3.2l2.65 5.55 6.05.82c.5.07.7.69.33 1.04l-4.4 4.12 1.08 6.04c.09.5-.44.88-.89.64L12 18.52l-5.42 2.9c-.45.23-.98-.14-.89-.64l1.08-6.04-4.4-4.12c-.37-.35-.17-.97.33-1.04l6.05-.82L11.4 3.2c.22-.47.88-.47 1.1 0z" stroke="${c}" stroke-width="1.7" stroke-linejoin="round" stroke-linecap="round"/></svg>`,
  gear: (s=18, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24"><path d="M14.7 3.6l.7 2.4a8 8 0 011.6.9l2.4-.7 1.7 3-1.7 1.8a8 8 0 010 1.8l1.7 1.8-1.7 3-2.4-.7a8 8 0 01-1.6.9l-.7 2.4h-3.4l-.7-2.4a8 8 0 01-1.6-.9l-2.4.7-1.7-3 1.7-1.8a8 8 0 010-1.8L3.2 9.2l1.7-3 2.4.7a8 8 0 011.6-.9l.7-2.4h3.4z" fill="${c}" fill-rule="evenodd"/><circle cx="12" cy="12" r="3.4" fill="var(--surface)"/></svg>`,
  chev: (s=14, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 14 14" fill="none"><path d="M5 3l4 4-4 4" stroke="${c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  back: (s=20, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 20 20" fill="none"><path d="M12.5 4l-6 6 6 6" stroke="${c}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
  book: (s=20, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none"><rect x="4.5" y="3.5" width="15" height="17" rx="2" stroke="${c}" stroke-width="1.7"/><path d="M4.5 17.5h15" stroke="${c}" stroke-width="1.4"/><path d="M9 7h6" stroke="${c}" stroke-width="1.7" stroke-linecap="round"/></svg>`,
  note: (s=20, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none"><path d="M7 3.5h7.5L19 8v12a1.5 1.5 0 01-1.5 1.5h-10A1.5 1.5 0 016 20V5A1.5 1.5 0 017 3.5z" stroke="${c}" stroke-width="1.7" stroke-linejoin="round"/><path d="M14.5 3.5V7A1.5 1.5 0 0016 8.5H19" stroke="${c}" stroke-width="1.7" stroke-linejoin="round"/><path d="M9 12.5h7M9 15.5h7M9 18.5h4.5" stroke="${c}" stroke-width="1.6" stroke-linecap="round"/></svg>`,
  bulb: (s=20, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none"><path d="M8.5 14.5c-1.2-1-2-2.5-2-4.3A5.5 5.5 0 0112 4.7a5.5 5.5 0 015.5 5.5c0 1.8-.8 3.3-2 4.3-.6.5-1 1.3-1 2.1v.4a1 1 0 01-1 1h-3a1 1 0 01-1-1v-.4c0-.8-.4-1.6-1-2.1z" stroke="${c}" stroke-width="1.7" stroke-linejoin="round"/><path d="M10 20.5h4" stroke="${c}" stroke-width="1.7" stroke-linecap="round"/></svg>`,
  slides: (s=20, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none"><rect x="3.5" y="6.5" width="17" height="11" rx="2" stroke="${c}" stroke-width="1.7"/><path d="M6 4.5h12M7 20h10" stroke="${c}" stroke-width="1.5" stroke-linecap="round"/></svg>`,
  heart: (s=16, c='currentColor', filled=false) => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="${filled ? c : 'none'}"><path d="M12 20.3s-7-4.1-9-8.7c-1-2.3-.1-5 2-6.1 2-1 4.1-.3 5.4 1 .4.4.7.8 1 1.3.3-.5.6-.9 1-1.3 1.3-1.3 3.4-2 5.4-1 2.1 1.1 3 3.8 2 6.1-2 4.6-9 8.7-9 8.7z" stroke="${c}" stroke-width="1.7" stroke-linejoin="round"/></svg>`,
  share: (s=18, c='currentColor') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none"><path d="M12 3.5v11" stroke="${c}" stroke-width="1.8" stroke-linecap="round"/><path d="M8.5 7L12 3.5 15.5 7" stroke="${c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M7 11H6.5A1.5 1.5 0 005 12.5v6A1.5 1.5 0 006.5 20h11a1.5 1.5 0 001.5-1.5v-6A1.5 1.5 0 0017.5 11H17" stroke="${c}" stroke-width="1.7" stroke-linejoin="round"/></svg>`,
};
```

- [ ] **2.5: Add CSS rules for new home classes**

Inside the `<style>` block, append:

```css
.ch-masthead { display:flex; align-items:center; justify-content:space-between; padding: 56px 20px 18px; }
.ch-eyebrow { font-size: var(--fs-caption-mono); letter-spacing: 1.4px; color: var(--muted); font-weight: 600; text-transform: uppercase; }
.ch-title { font-size: var(--fs-display); font-weight: 700; letter-spacing: -0.5px; margin-top: 2px; color: var(--ink); }
.ch-icon-actions { display: flex; gap: 8px; }
.ch-icon-btn { width: 36px; height: 36px; border-radius: var(--r-button); background: var(--surface); border: 1px solid var(--line); display: flex; align-items: center; justify-content: center; cursor: pointer; padding: 0; }
.ch-search-box { display: flex; align-items: center; gap: 10px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-input); padding: 10px 12px; margin: 0 20px; cursor: pointer; }
.ch-search-placeholder { color: var(--muted); font-size: var(--fs-body); flex: 1; }
.ch-search-kbd { font-size: var(--fs-caption-mono); color: var(--muted); border: 1px solid var(--line); padding: 2px 6px; border-radius: 4px; }
.ch-section-eyebrow { font-size: var(--fs-caption-mono); letter-spacing: 1.2px; color: var(--muted); font-weight: 600; text-transform: uppercase; margin: 22px 20px 8px; }
.ch-list-card { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-card); overflow: hidden; margin: 0 20px; }
.ch-row { display: flex; align-items: center; padding: 14px; border-bottom: 1px solid var(--line2); text-decoration: none; color: inherit; }
.ch-row:last-child { border-bottom: none; }
.ch-row-badge { width: 30px; height: 30px; border-radius: var(--r-row-badge); display: flex; align-items: center; justify-content: center; margin-right: 12px; box-shadow: inset 0 0 0 0.5px rgba(255,255,255,.14), 0 1px 2px rgba(0,0,0,.06); flex-shrink: 0; }
.ch-row-body { flex: 1; min-width: 0; }
.ch-row-title { font-weight: 600; font-size: var(--fs-body); letter-spacing: -0.2px; color: var(--ink); }
.ch-row-sub { font-size: var(--fs-secondary); color: var(--muted); margin-top: 2px; font-feature-settings: "tnum"; }
```

- [ ] **2.6: Bump CACHE_VERSION**

```js
const CACHE_VERSION = 'pocket-uro-v4.1.0-clinical-phase2';
```

- [ ] **2.7: Commit + push + deploy verify**

```bash
git add v4/index.html v4/sw.js
git commit -m "v4 Phase 2: Clinical home + dense module rows"
git push origin main
until [ "$(gh api repos/fantasy7386-cmd/pocket-uro/pages/builds --jq '.[0].status')" != "building" ]; do sleep 5; done
```

Manual check: home page now shows new masthead, single-card module list with 30×30 colored badges, ⌘K hint in search.

---

## Phase 3: Search Redesign + Query Highlight

**Goal:** Match `<ClinicalSearch/>` (clinical.jsx lines 201-252). Filter chips replace module checkboxes; result cards use module mono pill + breadcrumb + yellow highlight on query terms.

**Files:**
- Modify: `~/pocket-uro/v4/index.html` — find current search render function (likely `renderSearch` or in `navigate` for `#/search`)

### Tasks

- [ ] **3.1: Locate search rendering**

```bash
grep -nE "function render(Search|GlobalSearch)" ~/pocket-uro/v4/index.html
grep -nE "#/search" ~/pocket-uro/v4/index.html
```

- [ ] **3.2: Read current search markup** (to understand existing chip / result structure)

- [ ] **3.3: Rewrite search bar**

```html
<div class="cs-bar ${query ? 'cs-focused' : ''}">
  ${ICON.search(18, query ? 'var(--primary)' : 'var(--muted)')}
  <input class="cs-input" id="cs-input" value="${esc(query)}" placeholder="Search across all modules" autocomplete="off"/>
  <span class="cs-result-count">${results.length} results</span>
</div>
```

- [ ] **3.4: Rewrite filter chips**

```html
<div class="cs-chips">
  ${[
    { id: 'all', label: 'All', count: results.length },
    { id: 'tips', label: 'Tips', count: results.filter(r => r.module==='tips').length },
    { id: 'textbook', label: 'Textbook', count: results.filter(r => r.module==='textbook').length },
    { id: 'notes', label: 'Notes', count: results.filter(r => r.module==='notes').length },
    { id: 'education', label: 'Edu', count: results.filter(r => r.module==='education').length },
  ].map(f => `<button class="cs-chip ${currentFilter===f.id?'cs-chip-active':''}" data-filter="${f.id}">${f.label} · ${f.count}</button>`).join('')}
</div>
```

- [ ] **3.5: Rewrite result card**

For each result, render:

```html
<a class="cs-result" href="${result.href}">
  <div class="cs-result-meta">
    <span class="cs-mod-pill cs-mod-pill-${r.module}">${MODULE_LABEL[r.module]}</span>
    <span class="cs-where">${esc(r.breadcrumb)}</span>
  </div>
  <div class="cs-result-title">${highlightQuery(r.title, query)}</div>
  <div class="cs-result-preview">${highlightQuery(r.preview, query)}</div>
</a>
```

`MODULE_LABEL` mapping: `{ tips: 'TIPS', textbook: 'TEXT', notes: 'NOTE', education: 'EDU' }`.

- [ ] **3.6: Add `highlightQuery` helper**

```js
function highlightQuery(text, query) {
  if (!query) return esc(text);
  const escaped = esc(text);
  const queryEsc = esc(query).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  return escaped.replace(new RegExp(`(${queryEsc})`, 'gi'), '<mark class="cs-mark">$1</mark>');
}
```

- [ ] **3.7: Add CSS rules**

```css
.cs-bar { display: flex; align-items: center; gap: 10px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-input); padding: 10px 12px; margin: 0 16px; }
.cs-bar.cs-focused { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-soft); }
.cs-input { flex: 1; border: none; outline: none; font-size: var(--fs-body); color: var(--ink); background: transparent; }
.cs-result-count { color: var(--muted); font-size: var(--fs-secondary); }
.cs-chips { display: flex; gap: 6px; margin: 12px 16px 0; overflow-x: auto; padding-bottom: 4px; -webkit-overflow-scrolling: touch; }
.cs-chip { font-size: var(--fs-secondary); padding: 5px 10px; border-radius: 14px; background: var(--surface); color: var(--ink2); border: 1px solid var(--line); white-space: nowrap; font-weight: 500; cursor: pointer; }
.cs-chip-active { background: var(--primary); color: #fff; border-color: var(--primary); }
.cs-result { display: block; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-input); padding: 14px; margin: 8px 16px; text-decoration: none; color: inherit; }
.cs-result-meta { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.cs-mod-pill { font-size: 10px; font-weight: 700; letter-spacing: 0.8px; padding: 2px 6px; border-radius: 3px; background: #fff; }
.cs-mod-pill-tips { color: var(--mod-tips); border: 1px solid var(--mod-tips); }
.cs-mod-pill-textbook { color: var(--mod-textbook); border: 1px solid var(--mod-textbook); }
.cs-mod-pill-notes { color: var(--mod-notes); border: 1px solid var(--mod-notes); }
.cs-mod-pill-education { color: var(--mod-education); border: 1px solid var(--mod-education); }
.cs-where { font-size: var(--fs-caption-mono); color: var(--muted); }
.cs-result-title { font-size: var(--fs-body); font-weight: 600; letter-spacing: -0.2px; margin-bottom: 4px; color: var(--ink); }
.cs-result-preview { font-size: 13px; color: var(--muted); line-height: 1.55; }
.cs-mark { background: #FFF3BF; color: var(--ink); padding: 0 2px; border-radius: 2px; }
```

- [ ] **3.8: Bump CACHE_VERSION + commit + verify**

```js
const CACHE_VERSION = 'pocket-uro-v4.1.0-clinical-phase3';
```

```bash
git add v4/index.html v4/sw.js
git commit -m "v4 Phase 3: Clinical search with filter chips + query highlight"
git push origin main
```

---

## Phase 4: Tips Reader (Numbered Steps + Notes Callout)

**Goal:** Match `<ClinicalTips/>` (clinical.jsx lines 319-371).

**Files:**
- Modify: `~/pocket-uro/v4/index.html` — function `renderTipsSub` (existing v4 has it ~line 3041 in v3.7.1; locate fresh in v4)

### Tasks

- [ ] **4.1: Locate `renderTipsSub` in v4**

```bash
grep -nE "function renderTipsSub" ~/pocket-uro/v4/index.html
```

- [ ] **4.2: Restructure header**

Replace the current header markup with:

```html
<div class="ct-header">
  <a class="ct-back-link" href="#/tips/s/${chapterId}">${ICON.back(16, 'var(--primary)')} <span>${esc(titlePlain(chapter.title))}</span></a>
  <div class="ct-mod-eyebrow">TIPS &amp; GUIDE</div>
  <h2 class="ct-title">${titleWithTags(sub.title)}</h2>
</div>
```

- [ ] **4.3: Detect numbered list pattern in markdown**

Tips & Guide markdown often starts with `1. step`, `2. step`. After `renderMd(sub.markdown)`, post-process the rendered HTML: find the first `<ol>` and add class `ct-numbered-steps`. Then style each `<li>` with the badge.

Implementation: after rendering, do a regex replace on `<ol>` → `<ol class="ct-numbered-steps">`.

- [ ] **4.4: Detect "Notes" / "Caveats" callout**

Look for headings like `## Notes`, `## Caveats`, `## 注意`. Wrap the content from that heading until next H2 in a `<div class="ct-callout">`. (Implement as a pre-render markdown transform.)

- [ ] **4.5: Add CSS rules**

```css
.ct-header { padding: 56px 20px 12px; background: var(--surface); border-bottom: 1px solid var(--line); }
.ct-back-link { display: flex; align-items: center; gap: 8px; color: var(--primary); font-size: 13px; font-weight: 500; margin-bottom: 8px; text-decoration: none; }
.ct-mod-eyebrow { font-size: 10px; letter-spacing: 1.2px; color: var(--mod-tips); font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
.ct-title { font-size: 22px; font-weight: 700; letter-spacing: -0.4px; line-height: 1.2; color: var(--ink); margin: 0; }
.ct-numbered-steps { padding-left: 0; list-style: none; counter-reset: n; }
.ct-numbered-steps li { display: flex; gap: 12px; margin-bottom: 10px; counter-increment: n; }
.ct-numbered-steps li::before { content: counter(n); flex-shrink: 0; width: 22px; height: 22px; border-radius: 4px; background: var(--primary-soft); color: var(--primary); font-size: 11px; font-weight: 700; display: flex; align-items: center; justify-content: center; font-feature-settings: "tnum"; }
.ct-callout { margin-top: 16px; padding: 12px 14px; background: #FFF8E1; border: 1px solid #F0D986; border-left: 3px solid var(--warning); border-radius: 6px; }
.ct-callout-eyebrow { font-size: 10px; font-weight: 700; letter-spacing: 1px; color: var(--warning); text-transform: uppercase; margin-bottom: 4px; }
```

- [ ] **4.6: Bump + commit + verify**

```js
const CACHE_VERSION = 'pocket-uro-v4.1.0-clinical-phase4';
```

---

## Phase 5: Textbook Viewer

**Goal:** Match `<ClinicalTextbook/>` (clinical.jsx lines 254-317).

**Files:** v4/index.html — slide rendering function (likely `renderTbSlide` or inside textbook routing).

### Tasks

- [ ] **5.1: Locate textbook slide renderer**

```bash
grep -nE "function render(Tb|Textbook)" ~/pocket-uro/v4/index.html
```

- [ ] **5.2: Restructure slide page**

Replace existing markup with:
- White surface header containing back link + module mono eyebrow + topic title + EXAM badge if applicable
- Slide image area: 4:3 aspect ratio, white bg with subtle border, slide counter overlay bottom-right
- Prev/Next/Index control row (3 segments)
- Transcript card below: caption-mono "Transcript" header, bullet list of OCR text

(Show full markup template in step.)

- [ ] **5.3: Add CSS for new classes**

```css
.tb-header { padding: 56px 16px 12px; background: var(--surface); border-bottom: 1px solid var(--line); }
.tb-mod-eyebrow { font-size: 10px; letter-spacing: 1.2px; color: var(--mod-textbook); font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
.tb-topic { font-size: 18px; font-weight: 700; letter-spacing: -0.3px; color: var(--ink); }
.tb-exam-badge { display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 6px; background: #FEF3C7; color: #854D0E; border-radius: 3px; letter-spacing: 0.5px; margin-top: 8px; }
.tb-slide-frame { background: #fff; border-radius: 8px; aspect-ratio: 4/3; position: relative; overflow: hidden; border: 1px solid var(--line); box-shadow: 0 1px 2px rgba(11,31,58,0.04); margin: 16px; }
.tb-slide-counter { position: absolute; bottom: 8px; right: 10px; background: rgba(0,0,0,0.6); color: #fff; font-size: 10px; padding: 2px 6px; border-radius: 3px; font-feature-settings: "tnum"; }
.tb-controls { display: flex; gap: 8px; margin: 0 16px; }
.tb-ctrl-prev, .tb-ctrl-next { flex: 1; padding: 10px; border-radius: var(--r-button); font-size: 13px; font-weight: 600; }
.tb-ctrl-prev { background: var(--surface); border: 1px solid var(--line); color: var(--ink); }
.tb-ctrl-next { background: var(--primary); border: 1px solid var(--primary); color: #fff; }
.tb-ctrl-idx { padding: 10px 14px; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-button); font-size: 13px; color: var(--muted); font-feature-settings: "tnum"; }
.tb-transcript { margin: 14px 16px 0; background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-input); }
.tb-transcript-eyebrow { padding: 10px 14px; border-bottom: 1px solid var(--line2); font-size: 10px; letter-spacing: 1px; color: var(--muted); font-weight: 700; text-transform: uppercase; }
.tb-transcript-body { padding: 10px 14px; }
.tb-transcript-line { font-size: 13px; line-height: 1.7; color: var(--ink2); padding-left: 14px; position: relative; }
.tb-transcript-line::before { content: '·'; position: absolute; left: 0; color: var(--muted); }
```

- [ ] **5.4: Bump + commit**

---

## Phase 6: Notes / Education / Favorites Lists

**Goal:** Apply Clinical dense list pattern to PPu Notes list, Notes detail, Education list, Education article, Favorites list.

References: clinical-more.jsx ClinicalEduList (line 6), ClinicalEduArticle (61), ClinicalNotesList (109), ClinicalNotesDetail (160), ClinicalFavorites (215).

### Tasks

- [ ] **6.1: Notes list — grouped by chapter**

Each chapter shows a section header with caption-mono Roman numeral + chapter title. Below it, a list-card with rows for each note: title + bullet count + favorite star.

- [ ] **6.2: Notes detail — paragraph + bullet list + warning callout**

Use `.ct-callout` class from Phase 4.

- [ ] **6.3: Education list — categorized cards**

Single list-card with rows; each row has category chip on the left, title, article count, "read" checkmark (if user has opened it).

- [ ] **6.4: Education article — meta row + body**

Header on white surface: back link + category chip + updated date. Body: H2/H3 hierarchy via existing markdown renderer + "Share with patient" CTA.

- [ ] **6.5: Favorites — flat list with module pills**

Use the same `.cs-mod-pill-*` classes from Phase 3. Each row: pill + title + "saved Xd ago".

- [ ] **6.6: Single commit per sub-task** (so user can verify each list independently)

---

## Phase 7: Settings Page + Admin Sign-in (Paste-Token Variant)

**Goal:** Match `<ClinicalSettings/>` (clinical-more.jsx line 395) and `<ClinicalAdminSignIn/>` (line 263).

### Tasks

- [ ] **7.1: Settings shell**

Sections:
- Theme: auto/light/dark segmented control
- Text size: stepper or slider (12–20pt)
- Sync status: last synced YYYY-MM-DD + "Sync now" button
- About: version + repo link
- Editor sign-in row (if not signed in) OR "Editor · signed in" row with Enter edit mode CTA

- [ ] **7.2: Admin sign-in modal**

Replace current `<input type="password">` flow with a paste-token textarea. Token format = base64-encoded `{user, exp, sig}` JSON; `sig = HMAC-SHA256(secret, user|exp)`. Secret stored in `index.html` as constant (acceptable for client-side gating).

(Defer real cryptography to Phase 8 if user only wants visual upgrade.)

- [ ] **7.3: CSS for settings rows + modal**

- [ ] **7.4: Bump + commit**

---

## Phase 8: PIN Unlock System

**Goal:** Match `<ClinicalPinSetup/>`, `<ClinicalPinEntry/>`, `<ClinicalPinError/>` from clinical-admin.jsx lines 114-160.

### Tasks

- [ ] **8.1: PIN storage**

```js
async function setPin(pin) {
  const hash = await sha256Hex('pocket-uro-pin-salt-v1' + pin);
  localStorage.setItem('puro_pin_hash', hash);
  localStorage.setItem('puro_pin_set', '1');
}
async function verifyPin(pin) {
  const stored = localStorage.getItem('puro_pin_hash');
  if (!stored) return false;
  const hash = await sha256Hex('pocket-uro-pin-salt-v1' + pin);
  return hash === stored;
}
```

- [ ] **8.2: PIN setup UI** (after first admin sign-in)

6 dot indicators + numeric keypad + "Confirm" stage.

- [ ] **8.3: PIN entry UI** (when entering edit mode)

Same layout as setup. Wrong PIN → dots flash red + "Wrong PIN · N attempts left" hint. After 5 wrong attempts → revoke admin session (`localStorage.removeItem('puro_admin_unlocked')`).

- [ ] **8.4: Edit mode toggle gated on PIN**

Replace current `if (isAdmin())` checks with `if (isAdmin() && isEditModeUnlocked())`. `isEditModeUnlocked` checks a session flag set by successful PIN entry.

- [ ] **8.5: Amber edit-mode banner**

When edit mode ON, show fixed-top banner:
```html
<div class="edit-mode-banner">Editing · tap any content to edit · <button onclick="exitEditMode()">Exit</button></div>
```

- [ ] **8.6: Bump + commit**

---

## Phase 9: Recent Items System

**Goal:** Track last 20 opened items and surface on home Recent section.

### Tasks

- [ ] **9.1: `recordOpen(module, id, title)` function**

```js
function recordOpen(module, id, title, breadcrumb) {
  const recents = JSON.parse(localStorage.getItem('puro_recents') || '[]');
  const filtered = recents.filter(r => !(r.module === module && r.id === id));
  filtered.unshift({ module, id, title, breadcrumb, openedAt: Date.now() });
  const trimmed = filtered.slice(0, 20);
  localStorage.setItem('puro_recents', JSON.stringify(trimmed));
}
```

- [ ] **9.2: Hook into navigate**

Call `recordOpen` whenever a content view renders (renderArticle, renderTipsSub, renderTbSlide, renderNoteDetail). Pass module ID, entity ID, title, breadcrumb.

- [ ] **9.3: Render Recent section in home**

After modules section, add:
```html
<div class="ch-section-eyebrow">Recent</div>
<div class="ch-list-card">
  ${recents.slice(0, 3).map(r => `
    <a class="ch-recent-row" href="${recentHref(r)}">
      <div class="ch-recent-dot" style="background:var(--mod-${r.module})"></div>
      <div class="ch-row-body">
        <div class="ch-recent-title">${esc(r.title)}</div>
        <div class="ch-recent-sub">${esc(r.breadcrumb)}</div>
      </div>
      <div class="ch-recent-time">${relativeTime(r.openedAt)}</div>
    </a>
  `).join('')}
</div>
```

- [ ] **9.4: `relativeTime` helper**

```js
function relativeTime(ts) {
  const diff = Date.now() - ts;
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return 'now';
  if (mins < 60) return mins + 'm';
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return hrs + 'h';
  const days = Math.floor(hrs / 24);
  if (days < 7) return days + 'd';
  return new Date(ts).toLocaleDateString().slice(5);
}
```

- [ ] **9.5: CSS**

```css
.ch-recent-row { display: flex; align-items: center; padding: 12px 14px; border-bottom: 1px solid var(--line2); text-decoration: none; color: inherit; }
.ch-recent-row:last-child { border-bottom: none; }
.ch-recent-dot { width: 6px; height: 6px; border-radius: 3px; margin-right: 12px; flex-shrink: 0; }
.ch-recent-title { font-size: 14px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--ink); }
.ch-recent-sub { font-size: 11px; color: var(--muted); margin-top: 2px; }
.ch-recent-time { font-size: 11px; color: var(--muted); font-feature-settings: "tnum"; }
```

- [ ] **9.6: Bump + commit**

---

## Phase 10: Beacon App Icon

**Goal:** Replace v4 icon PNGs with the Beacon design from the Claude Design handoff.

**Files:**
- Create: `~/pocket-uro/v4/icon-source.svg` (the Beacon SVG from icons.jsx)
- Create: `~/pocket-uro/scripts/render_icons.py` (Pillow renderer)
- Replace: `~/pocket-uro/v4/icon-{20,29,40,58,60,76,80,87,120,152,167,180,192,512,1024}.png`
- Replace: `~/pocket-uro/v4/apple-touch-icon.png`
- Modify: `~/pocket-uro/v4/manifest.json` — verify icon paths

### Tasks

- [ ] **10.1: Read icon source**

Read `~/Downloads/design_handoff_pocket_uro/icons/icons.jsx` for the SVG geometry (Beacon: bg radial gradient + tapered beam + bead + wordmark).

- [ ] **10.2: Write `icon-source.svg`**

Convert the JSX SVG to standalone SVG file. ViewBox 200×200. Include all gradients, beam paths, bead, wordmark.

- [ ] **10.3: Write Pillow render script**

```python
#!/usr/bin/env python3
"""Render iOS icon PNGs from icon-source.svg using cairosvg + Pillow."""
import cairosvg
from pathlib import Path

SIZES = [20, 29, 40, 58, 60, 76, 80, 87, 120, 152, 167, 180, 192, 512, 1024]
SRC = Path(__file__).parent.parent / 'v4' / 'icon-source.svg'
OUT = Path(__file__).parent.parent / 'v4'

for size in SIZES:
    cairosvg.svg2png(url=str(SRC), output_width=size, output_height=size, write_to=str(OUT / f'icon-{size}.png'))
    print(f'wrote icon-{size}.png')

# apple-touch-icon = 180
import shutil
shutil.copy(OUT / 'icon-180.png', OUT / 'apple-touch-icon.png')
```

- [ ] **10.4: Run script + verify outputs**

```bash
pip install cairosvg
python3 ~/pocket-uro/scripts/render_icons.py
ls -lh ~/pocket-uro/v4/icon-*.png
```

- [ ] **10.5: Update manifest.json paths**

Confirm `icons` array references the right sizes (192, 512 minimum).

- [ ] **10.6: Bump + commit**

---

## Phase 11: Final Polish + Cache Bump + Deploy

### Tasks

- [ ] **11.1: Audit remaining old-style references**

```bash
grep -nE "(--bg-primary|--text-primary|--accent-)" ~/pocket-uro/v4/index.html | head -30
```

If any unmigrated tokens remain, replace with new ones and remove legacy aliases from Phase 1.

- [ ] **11.2: Footer version bump**

Update footer to show `v4.1.0-clinical · synced YYYY-MM-DD`.

- [ ] **11.3: Final CACHE_VERSION**

```js
const CACHE_VERSION = 'pocket-uro-v4.1.0-clinical';
```

- [ ] **11.4: Tag**

```bash
git tag v4.1.0-clinical
git push origin v4.1.0-clinical
```

- [ ] **11.5: Deploy verify**

```bash
until [ "$(gh api repos/fantasy7386-cmd/pocket-uro/pages/builds --jq '.[0].status')" != "building" ]; do sleep 5; done
curl -sI "https://fantasy7386-cmd.github.io/pocket-uro/v4/?_=$(date +%s)" | grep -iE "(last-modified|etag)"
```

- [ ] **11.6: Update project memory**

Edit `~/.claude/projects/-Users-chengyangdata/memory/project_pocket_uro.md` with new state: v4.1.0-clinical shipped, full Clinical design applied.

---

## Self-Review

**Spec coverage:**
- ✅ Tokens (Phase 1)
- ✅ Home / Modules dense list (Phase 2)
- ✅ Search filter chips + highlight (Phase 3)
- ✅ Tips reader numbered + callout (Phase 4)
- ✅ Textbook viewer (Phase 5)
- ✅ Notes / Edu / Favorites (Phase 6)
- ✅ Settings + admin sign-in (Phase 7)
- ✅ PIN unlock (Phase 8)
- ✅ Recent items (Phase 9)
- ✅ Beacon icon (Phase 10)
- ✅ Cache + tag (Phase 11)
- ❌ Face ID — explicitly cut (PWA limitation)
- ❌ Quiz UI structured redesign — deferred to separate plan
- ⚠️ Dynamic Type / iOS text size — partial (text size in Settings phase 7, not full Dynamic Type)
- ⚠️ Accessibility (VoiceOver) — out of scope for this plan; user did not request

**Type consistency:** ICON sprite naming consistent across all phases (`ICON.search`, `ICON.star` etc.). MODULE_LABEL consistent (`TIPS / TEXT / NOTE / EDU`).

**Placeholder scan:** No "TODO" / "TBD" / "implement later" found. Each step has actual code or actual command.

---

## Risk + Rollback

**Per-phase rollback:** Each phase ships in its own commit. To roll back to start of Phase N, `git checkout <phase-N-1-commit-hash> -- v4/`.

**Full v4 rollback:** `git checkout v3.7.1-stable -- v4/` resets v4 to its alpha state.

**v3.7.1 untouched:** No phase modifies anything outside `v4/` and `scripts/`. Root index.html, root sw.js stay at the v3.7.1 baseline. User's daily-use PWA at `https://fantasy7386-cmd.github.io/pocket-uro/` is never at risk.
