/**
 * Cloudflare Worker â€” LE BUZZER
 *
 * fetch handler  : proxy audio MP3 + feed RSS depuis GitHub Releases
 *                  + landing page inline + artwork
 */

const REPO = "meerkly-00/lebuzzer-podcast";
const RAW = `https://raw.githubusercontent.com/${REPO}/main`;

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Feed RSS
    if (url.pathname === "/feed.xml") {
      return proxyTo(request, `${RAW}/feed.xml`, "application/rss+xml; charset=utf-8", 300);
    }

    // MP3 Ã©pisode : /audio/YYYY-MM-DD.mp3
    const m = url.pathname.match(/^\/audio\/(\d{4}-\d{2}-\d{2})\.mp3$/);
    if (m) {
      return proxyTo(request, `https://github.com/${REPO}/releases/download/${m[1]}/${m[1]}.mp3`);
    }

    // Clips courts : /clips/YYYY-MM-DD_N.mp4
    const c = url.pathname.match(/^\/clips\/(\d{4}-\d{2}-\d{2})_(\d+)\.mp4$/);
    if (c) {
      return proxyTo(request, `https://github.com/${REPO}/releases/download/${c[1]}/${c[1]}_clip_${c[2]}.mp4`);
    }

    // Cover artwork â€” pointe vers cover-v1.png dans le repo
    if (url.pathname === "/artwork.jpg" || url.pathname === "/artwork.png") {
      return proxyTo(request, `${RAW}/artwork/cover-v1.png`, "image/png", 86400);
    }

    // Assets du site (polices, images) : /assets/<fichier>
    const a = url.pathname.match(/^\/assets\/([A-Za-z0-9._-]+)$/);
    if (a) {
      const ct = a[1].endsWith(".woff2") ? "font/woff2"
        : a[1].endsWith(".woff") ? "font/woff"
        : a[1].endsWith(".png") ? "image/png"
        : a[1].endsWith(".jpg") || a[1].endsWith(".jpeg") ? "image/jpeg"
        : a[1].endsWith(".svg") ? "image/svg+xml"
        : a[1].endsWith(".webp") ? "image/webp"
        : null;
      return proxyTo(request, `${RAW}/site/assets/${a[1]}`, ct, 86400);
    }

    // Fichiers SEO racine
    if (url.pathname === "/sitemap.xml") {
      return proxyTo(request, `${RAW}/site/sitemap.xml`, "application/xml; charset=utf-8", 3600);
    }
    if (url.pathname === "/robots.txt") {
      return proxyTo(request, `${RAW}/site/robots.txt`, "text/plain; charset=utf-8", 3600);
    }
    if (url.pathname === "/site.webmanifest") {
      return proxyTo(request, `${RAW}/site/site.webmanifest`, "application/manifest+json", 86400);
    }
    if (url.pathname === "/favicon.ico") {
      return proxyTo(request, `${RAW}/site/assets/favicon.ico`, "image/x-icon", 86400);
    }

    // Landing page â€” servie depuis site/index.html dans le repo
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return proxyTo(request, `${RAW}/site/index.html`, "text/html; charset=utf-8", 300);
    }

    return new Response("Not found", { status: 404 });
  },
};

// â”€â”€â”€ helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async function proxyTo(request, target, contentType = null, maxAge = 86400) {
  const upstream = await fetch(target, {
    method: request.method,
    headers: { "User-Agent": "LeBuzzer-Proxy/1.0" },
    redirect: "follow",
  });
  const headers = new Headers(upstream.headers);
  headers.set("Cache-Control", `public, max-age=${maxAge}`);
  headers.set("Access-Control-Allow-Origin", "*");
  if (contentType) headers.set("Content-Type", contentType);
  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers,
  });
}
