// Service Worker for AirTransfer PWA
const CACHE_NAME = 'airtransfer-v1';
const urlsToCache = [
    '/',
    '/static/manifest.json',
    '/static/icon-192.png'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', (event) => {
    // For share target, always go to network
    if (event.request.url.includes('/share') || event.request.url.includes('/upload')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => response || fetch(event.request))
    );
});
