# Design: Scoped (in-context) Search

**Date:** 2026-06-28
**Status:** Approved in brainstorming
**Target version:** v3.8.1
**Affects:** `index.html` only (search logic + list-page search boxes). No data/sync changes.

## Background / Problem

Search is global (or module-filtered via the existing `only=<module>`). A user browsing a specific section (e.g. Textbook › 前列腺 › 良性疾病) wants to search **only within that scope**, not be flooded by results from other chapters. Confirmed scope: all modules; result presentation: jump to the existing search page carrying a removable scope chip.

## Scope encoding

URL: `#/search?q=<q>&scope=<spec>`, where `<spec>` is one of:
- `edu` / `edu:<catId>` — patient education: whole module / one category
- `notes` — PPu notes (module level)
- `tips` / `tips:<chapterId>` — tips: whole module / one chapter
- `tb:<tbId>` — textbook chapter (e.g. all of 前列腺)
- `tb:<tbId>:<secIdx>` — textbook section (e.g. 良性疾病) ← **primary use case**

The existing `only=<module>` filter is subsumed: a module-level scope behaves like `only`. Keep `only=` working for back-compat; when both present, `scope` (finer) wins.

## Search boxes (7 list pages)

Add a search box in the title row of each list page; submitting navigates to `#/search?q=<q>&scope=<spec>` with the scope derived from the current route:

| Render fn | Scope |
|---|---|
| renderEducationCategories | `edu` |
| renderEducationArticles(catId) | `edu:<catId>` |
| renderNotesList | `notes` |
| renderTipsList | `tips` |
| renderTipsChapter(chapterId) | `tips:<chapterId>` |
| renderTextbookChapter(tbId) | `tb:<tbId>` |
| renderTextbookSection(tbId, secIdx) | `tb:<tbId>:<secIdx>` |

## doSearch(q, only, scope)

The existing traversal already loops chapter→section→topic→slide per module. Add a scope gate that, before scanning each dataset/chapter/section, skips anything outside scope:
- `edu[:cat]` → only scan `state.data.articles` (optionally filtered to `a.category === cat`).
- `notes` → only scan notes.
- `tips[:ch]` → only scan tips (optionally the one chapter).
- `tb:<id>[:<sec>]` → only scan that textbook chapter (optionally that section index).
- no scope → current behaviour (all modules, honoring `only`).

## Search page

- `renderSearch(q, only, scope)` shows a chip `範圍: <label> ✕` when scope is set; the ✕ links to the same `q` without `scope` (→ global).
- `scopeLabel(scope)` resolves a human path from loaded data (e.g. `前列腺 › 良性疾病`); falls back to the raw id if a chapter isn't loaded.

## Verification

- Playwright: from a textbook section page, search a term → results only from that section; press ✕ → results appear from other chapters too. Tips-chapter scope likewise. Global search (no scope) unchanged. Existing `only=` module filter still works. 0 errors.

## Risk

Low — frontend search + UI only, no data/sync changes. Bump CACHE_VERSION + brand-tag → v3.8.1.
