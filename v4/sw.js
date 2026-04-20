'use strict';

// Pocket URO v4 Service Worker — scope: /pocket-uro/v4/
// Shares parent (/pocket-uro/) data + images via cross-path fetch interception.

const CACHE_VERSION = 'pocket-uro-v4.0.2-alpha-fix3';

// Core assets — v4 shell + parent shared JSON that the v4 page depends on.
// Paths here use v4/ prefix because SW fetch URLs are absolute.
const CORE_ASSETS = [
  'v4/',
  'v4/index.html',
  'v4/manifest.json?v=4',
  'v4/icon-192.png?v=4',
  'v4/icon-512.png?v=4',
  'v4/apple-touch-icon.png?v=4',
  'lib/marked.min.js?v=4',    // shared with v3.4 via parent /lib/
  'data.json',
  'teaching-notes.json',
  'tips-guide.json',
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

  // Cache-first for textbook WebP renders (immutable per deployment) — lives in
  // /pocket-uro/images/textbook/... shared with v3.4
  if (url.origin === location.origin &&
      url.pathname.includes('/images/textbook/') &&
      url.pathname.endsWith('.webp')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Cache-first for lazy-loaded chapter JSONs (shared with v3.4)
  if (url.origin === location.origin &&
      url.pathname.includes('/textbook-data/') &&
      url.pathname.endsWith('.json')) {
    event.respondWith(staleWhileRevalidate(request));
    return;
  }

  // Stale-while-revalidate for same-origin (v4 pages + core shared files)
  if (url.origin === location.origin) {
    event.respondWith(staleWhileRevalidate(request));
  }
});

function cacheFirst(request) {
  return caches.match(request).then(cached => {
    if (cached) return cached;
    return fetch(request).then(resp => {
      if (resp.ok) {
        const clone = resp.clone();
        caches.open(CACHE_VERSION).then(cache => cache.put(request, clone));
      }
      return resp;
    });
  });
}

function staleWhileRevalidate(request) {
  return caches.match(request).then(cached => {
    const fresh = fetch(request).then(resp => {
      if (resp.ok) {
        const clone = resp.clone();
        caches.open(CACHE_VERSION).then(cache => cache.put(request, clone));
      }
      return resp;
    }).catch(() => cached);
    return cached || fresh;
  });
}
