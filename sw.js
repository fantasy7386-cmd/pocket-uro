'use strict';

const CACHE_VERSION = 'pocket-uro-v1.4.0';

const CORE_ASSETS = [
  './',
  './index.html',
  './manifest.json?v=3',
  './icon-192.png?v=3',
  './icon-512.png?v=3',
  './apple-touch-icon.png?v=3',
  './lib/marked.min.js?v=3',
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
