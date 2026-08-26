// ============================================
// 🔥 WiFi Hacker Pro v7.0 - Service Worker
// ============================================

const CACHE_NAME = 'wifi-hacker-v7';
const ASSETS = [
    '/',
    '/index.html',
    '/style.css',
    '/wifi_hack.js',
    '/storage.js',
    '/particles.js',
    '/app.js',
    '/manifest.json',
    '/icon-192.png',
    '/icon-512.png'
];

// Install
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Caching assets...');
                return cache.addAll(ASSETS);
            })
            .then(() => self.skipWaiting())
    );
});

// Activate
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys => {
            return Promise.all(
                keys.filter(key => key !== CACHE_NAME)
                    .map(key => caches.delete(key))
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch
self.addEventListener('fetch', event => {
    const request = event.request;
    
    if (request.url.includes('analytics') || request.url.includes('telemetry')) {
        return;
    }
    if (request.url.includes('cdnjs') || request.url.includes('fonts.googleapis')) {
        event.respondWith(fetch(request));
        return;
    }

    event.respondWith(
        fetch(request)
            .then(response => {
                const responseClone = response.clone();
                caches.open(CACHE_NAME).then(cache => {
                    if (request.method === 'GET') {
                        cache.put(request, responseClone);
                    }
                });
                return response;
            })
            .catch(() => {
                return caches.match(request)
                    .then(cachedResponse => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        return caches.match('/index.html');
                    });
            })
    );
});

// Message
self.addEventListener('message', event => {
    if (event.data === 'skipWaiting') {
        self.skipWaiting();
    }
    if (event.data === 'update') {
        self.skipWaiting();
        self.clients.claim();
    }
});

console.log('[SW] WiFi Hacker Pro v7.0 loaded');
