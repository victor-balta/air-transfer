const CACHE_NAME = 'airtransfer-v3';
const urlsToCache = [
    '/',
    '/static/manifest.json',
    '/static/app_icon.png',
    '/static/menubar_icon.png'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(urlsToCache))
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => response || fetch(event.request))
    );
});
