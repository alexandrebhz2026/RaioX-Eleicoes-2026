const C='apuracao-2026-v4-1';
self.addEventListener('install',e=>{self.skipWaiting()});
self.addEventListener('activate',e=>{e.waitUntil(Promise.all([
  caches.keys().then(ks=>Promise.all(ks.map(k=>caches.delete(k)))),
  self.registration.unregister(),
  self.clients.claim()
]))});
self.addEventListener('fetch',()=>{});
