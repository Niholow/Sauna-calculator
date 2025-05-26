import os

# Пути
STATIC_DIR = "static"

# manifest.json
MANIFEST_JSON = '''{
  "name": "Калькулятор сауны",
  "short_name": "Сауна",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#007AFF",
  "description": "Рассчитывай стоимость сауны как в античности"
}
'''

# service-worker.js
SERVICE_WORKER_JS = '''const CACHE_NAME = "sauna-calculator-cache-v1";
const urlsToCache = ["/", "/static/style.css"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
  );
});

self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => response || fetch(event.request))
  );
});
'''

def write_file(path, content):
    with open(path, "w") as f:
        f.write(content)
    print(f"Файл создан: {path}")

if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

write_file(os.path.join(STATIC_DIR, "manifest.json"), MANIFEST_JSON)
write_file(os.path.join(STATIC_DIR, "service-worker.js"), SERVICE_WORKER_JS)

print("\n✅ Файлы успешно созданы!")
print("Теперь добавь в app.py поддержку PWA")
print("Или используй готовый шаблон HTML из предыдущего ответа")
print("Затем открой сайт на телефоне и добавь его на главный экран")
