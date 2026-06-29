'use strict';

const CACHE_VERSION = 'pocket-uro-v3.8.2';
// Immutable, content-addressed assets (textbook webp + images/content/*). Kept in a
// SEPARATE, unversioned cache that SURVIVES version bumps — so updating the app no
// longer wipes the user's downloaded-for-offline images. Before v3.8.2 everything
// shared CACHE_VERSION, so every bump (v3.7.24→v3.8.1 was 4 of them) deleted the
// ~155 MB of downloaded slides and forced a full re-download.
const ASSET_CACHE = 'pocket-uro-assets';
// v3.7.1: evict oldest entries when cache.put fails with QuotaExceededError.
// iOS Safari quota is ~50MB per origin. Without this, once full, new writes
// silently fail and fresh content never reaches the cache.
const MAX_EVICT_PER_FAILURE = 20;

const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json?v=5',
  './icon-192.png?v=5',
  './icon-512.png?v=5',
  './apple-touch-icon.png?v=5',
  './brand-icon.png?v=4',
  './lib/marked.min.js?v=3',
  './data.json',
  './teaching-notes.json',
  './tips-guide.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then(cache => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  // NOTE: intentionally NO self.clients.claim(). Claiming the open page mid-session
  // fires `controllerchange` in index.html, whose handler reloaded the page and aborted
  // the in-flight 5.7 MB data.json boot fetch -> state.data = null -> blank / "Load failed".
  // Without claim(), a newly installed SW takes control on the NEXT navigation instead,
  // so the current load finishes from the network uninterrupted.
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        // Delete old versioned caches, but KEEP the immutable asset cache so
        // downloaded offline images persist across app updates.
        keys.filter(k => k !== CACHE_VERSION && k !== ASSET_CACHE).map(k => caches.delete(k))
      ))
  );
});

self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Passthrough for GitHub API
  if (/\.githubusercontent\.com$|^api\.github\.com$|^github\.com$/.test(url.hostname)) {
    return;
  }

  // Cache-first for textbook WebP renders (immutable per deployment)
  if (url.origin === location.origin &&
      url.pathname.includes('/images/textbook/') &&
      url.pathname.endsWith('.webp')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Cache-first for content-addressed article/notes/tips images.
  // Filename = content hash, so the asset is immutable -> safe to cache forever.
  if (url.origin === location.origin &&
      url.pathname.includes('/images/content/')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Cache-first for lazy-loaded chapter JSONs
  if (url.origin === location.origin &&
      url.pathname.includes('/textbook-data/') &&
      url.pathname.endsWith('.json')) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Stale-while-revalidate for same-origin
  if (url.origin === location.origin) {
    event.respondWith(staleWhileRevalidate(request));
  }
});

async function putWithQuotaFallback(request, response, cacheName) {
  const name = cacheName || CACHE_VERSION;
  try {
    const cache = await caches.open(name);
    await cache.put(request, response);
  } catch (e) {
    // Quota exceeded: evict oldest entries (FIFO by match order) then retry once.
    try {
      const cache = await caches.open(name);
      const keys = await cache.keys();
      const evictTargets = keys.slice(0, MAX_EVICT_PER_FAILURE);
      await Promise.all(evictTargets.map(k => cache.delete(k)));
      // Retry once; if still fails, drop silently — the fetch response is
      // already returned to the page so functionality is preserved.
      await cache.put(request, response);
    } catch (_) {
      // Give up; serving is unaffected.
    }
  }
}

function cacheFirst(request) {
  return caches.match(request).then(cached => {
    if (cached) return cached;
    return fetch(request).then(resp => {
      if (resp.ok) {
        // Immutable assets go to the persistent ASSET_CACHE (survives version bumps).
        putWithQuotaFallback(request, resp.clone(), ASSET_CACHE);
      }
      return resp;
    });
  });
}

function staleWhileRevalidate(request) {
  return caches.match(request).then(cached => {
    const fresh = fetch(request).then(resp => {
      if (resp.ok) {
        putWithQuotaFallback(request, resp.clone(), CACHE_VERSION);
      }
      return resp;
    });
    // With a cached copy: serve it now, refresh in the background, swallow bg errors.
    // Without a cache: await the network and let a genuine failure reject naturally —
    // returning `cached` (undefined) here made respondWith() throw
    // "FetchEvent.respondWith received an error: TypeError: Load failed".
    if (cached) {
      fresh.catch(() => {});
      return cached;
    }
    return fresh;
  });
}
