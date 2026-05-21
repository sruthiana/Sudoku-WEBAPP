self.addEventListener("install", event => {
    event.waitUntil(
        caches.open("sudoku-cache").then(cache =>
            cache.addAll([
                "/",
                "/login",
                "/register",
                "/game",
                "/static/style.css"
            ])
        )
    );
});

self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(res => res || fetch(event.request))
    );
});
