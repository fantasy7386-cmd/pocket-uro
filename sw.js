'use strict';

const CACHE_VERSION = 'pocket-uro-v3.7.15';
// v3.7.1: evict oldest entries when cache.put fails with QuotaExceededError.
// iOS Safari quota is ~50MB per origin. Without this, once full, new writes
// silently fail and fresh content never reaches the cache.
const MAX_EVICT_PER_FAILURE = 20;

const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json?v=3',
  './icon-192.png?v=3',
  './icon-512.png?v=3',
  './apple-touch-icon.png?v=3',
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
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_VERSION).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
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

async function putWithQuotaFallback(request, response) {
  try {
    const cache = await caches.open(CACHE_VERSION);
    await cache.put(request, response);
  } catch (e) {
    // Quota exceeded: evict oldest entries (FIFO by match order) then retry once.
    try {
      const cache = await caches.open(CACHE_VERSION);
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
        putWithQuotaFallback(request, resp.clone());
      }
      return resp;
    });
  });
}

function staleWhileRevalidate(request) {
  return caches.match(request).then(cached => {
    const fresh = fetch(request).then(resp => {
      if (resp.ok) {
        putWithQuotaFallback(request, resp.clone());
      }
      return resp;
    }).catch(() => cached);
    return cached || fresh;
  });
}
