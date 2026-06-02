/**
 * Cloudflare Worker - LE BUZZER
 *
 * fetch handler  : proxy audio MP3 + feed RSS depuis GitHub Releases
 * scheduled      : (optionnel) cron pour distribution sociale future
 *
 * Adapte du worker Presto. Configuration des secrets dans Cloudflare Dashboard
 * (Settings -> Variables) ou via `wrangler secret put NAME`.
 */

const REPO = "meerkly-00/lebuzzer-podcast";
const RAW = `https://raw.githubusercontent.com/${REPO}/main`;
const TWITTER_API = "https://api.twitter.com/2/tweets";

// ─── fetch handler : audio + feed proxy ──────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Feed RSS depuis le repo
    if (url.pathname === "/feed.xml") {
      const ghUrl = `${RAW}/feed.xml`;
      return proxyTo(request, ghUrl, "application/rss+xml; charset=utf-8", 300);
    }

    // MP3 d'episode : /audio/YYYY-MM-DD.mp3 -> GitHub Release du meme nom
    const m = url.pathname.match(/^\/audio\/(\d{4}-\d{2}-\d{2})\.mp3$/);
    if (m) {
      const date = m[1];
      return proxyTo(request, `https://github.com/${REPO}/releases/download/${date}/${date}.mp3`);
    }

    // Clips courts : /clips/YYYY-MM-DD_N.mp4 -> GitHub Release
    const c = url.pathname.match(/^\/clips\/(\d{4}-\d{2}-\d{2})_(\d+)\.mp4$/);
    if (c) {
      const date = c[1];
      const idx = c[2];
      return proxyTo(request, `https://github.com/${REPO}/releases/download/${date}/${date}_clip_${idx}.mp4`);
    }

    // Cover artwork
    if (url.pathname === "/artwork.jpg" || url.pathname === "/artwork.png") {
      const ext = url.pathname.endsWith(".png") ? "png" : "jpg";
      return proxyTo(request, `${RAW}/artwork/cover.${ext}`, `image/${ext === "jpg" ? "jpeg" : "png"}`, 86400);
    }

    // Landing page minimaliste
    if (url.pathname === "/" || url.pathname === "/index.html") {
      return new Response(LANDING_HTML, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "public, max-age=300",
        },
      });
    }

    return new Response("Not found", { status: 404 });
  },

  // ─── scheduled handler (optionnel, desactive par defaut) ────────────────────

  async scheduled(event, env, ctx) {
    // Twitter cron - actif uniquement si les secrets sont configures
    if (!env.TWITTER_API_KEY) {
      console.log("[cron] Twitter secrets non configures, skip.");
      return;
    }

    const date = new Date().toISOString().slice(0, 10);
    console.log(`[tweet-cron] starting for ${date}`);

    const tweetsUrl = `${RAW}/data/tweets/${date}.json`;
    const tweetsResp = await fetch(tweetsUrl, { cf: { cacheEverything: false } });
    if (!tweetsResp.ok) {
      console.log(`[tweet-cron] no tweets file for ${date} (${tweetsResp.status}), skip`);
      return;
    }

    const { tweets } = await tweetsResp.json();
    if (!tweets || tweets.length === 0) {
      console.log(`[tweet-cron] empty tweet list for ${date}, skip`);
      return;
    }

    console.log(`[tweet-cron] posting ${tweets.length} tweets`);

    let replyToId = null;
    for (let i = 0; i < tweets.length; i++) {
      const id = await postTweet(tweets[i], replyToId, env);
      console.log(`[tweet-cron] tweet ${i + 1}/${tweets.length} -> ${id}`);
      replyToId = id;
      if (i < tweets.length - 1) await sleep(2500);
    }

    console.log(`[tweet-cron] thread done`);
  },
};

// ─── Twitter OAuth 1.0a ──────────────────────────────────────────────────────

async function buildOAuthHeader(method, url, env) {
  const oauthParams = {
    oauth_consumer_key: env.TWITTER_API_KEY,
    oauth_nonce: crypto.randomUUID().replace(/-/g, ""),
    oauth_signature_method: "HMAC-SHA1",
    oauth_timestamp: Math.floor(Date.now() / 1000).toString(),
    oauth_token: env.TWITTER_ACCESS_TOKEN,
    oauth_version: "1.0",
  };

  const sortedPairs = Object.entries(oauthParams)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${pct(k)}=${pct(v)}`)
    .join("&");

  const sigBase = `${method.toUpperCase()}&${pct(url)}&${pct(sortedPairs)}`;
  const sigKey = `${pct(env.TWITTER_API_SECRET)}&${pct(env.TWITTER_ACCESS_TOKEN_SECRET)}`;

  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(sigKey),
    { name: "HMAC", hash: "SHA-1" },
    false,
    ["sign"]
  );
  const sigBytes = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(sigBase));
  const signature = btoa(String.fromCharCode(...new Uint8Array(sigBytes)));

  const headerParts = Object.entries({ ...oauthParams, oauth_signature: signature })
    .map(([k, v]) => `${pct(k)}="${pct(v)}"`)
    .join(", ");

  return `OAuth ${headerParts}`;
}

async function postTweet(text, replyToId, env) {
  const authHeader = await buildOAuthHeader("POST", TWITTER_API, env);

  const body = { text };
  if (replyToId) body.reply = { in_reply_to_tweet_id: replyToId };

  const resp = await fetch(TWITTER_API, {
    method: "POST",
    headers: {
      Authorization: authHeader,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const err = await resp.text();
    throw new Error(`Twitter API ${resp.status}: ${err.slice(0, 300)}`);
  }

  const data = await resp.json();
  return data.data.id;
}

// ─── helpers ─────────────────────────────────────────────────────────────────

const pct = (s) => encodeURIComponent(String(s));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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

// ─── landing page minimaliste ────────────────────────────────────────────────

const LANDING_HTML = `<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>LE BUZZER - podcast sport quotidien</title>
  <meta name="description" content="Le podcast sport quotidien francophone quebecois. Resultats, histoires et angles de la LNH, NBA, foot, F1 et MMA en 5 minutes.">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: #0D0D0D;
      color: #F1FAEE;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
      text-align: center;
    }
    .container { max-width: 600px; }
    h1 {
      font-size: clamp(64px, 14vw, 140px);
      font-weight: 900;
      letter-spacing: -2px;
      line-height: 0.85;
      color: #E63946;
      margin-bottom: 8px;
    }
    .accent {
      width: 120px;
      height: 4px;
      background: #FFD60A;
      margin: 16px auto 24px;
    }
    .tagline {
      font-size: 18px;
      color: #888;
      margin-bottom: 40px;
      font-style: italic;
    }
    .description {
      font-size: 16px;
      line-height: 1.6;
      color: #ccc;
      margin-bottom: 40px;
    }
    .platforms {
      display: flex;
      gap: 16px;
      justify-content: center;
      flex-wrap: wrap;
    }
    .platforms a {
      color: #F1FAEE;
      text-decoration: none;
      padding: 12px 24px;
      border: 1px solid #333;
      border-radius: 4px;
      transition: all 0.2s;
      font-size: 14px;
      font-weight: 500;
    }
    .platforms a:hover {
      border-color: #E63946;
      color: #E63946;
    }
    footer {
      position: fixed;
      bottom: 16px;
      font-size: 12px;
      color: #555;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>LE<br>BUZZER</h1>
    <div class="accent"></div>
    <p class="tagline">Le podcast sport quotidien.</p>
    <p class="description">
      LNH, NBA, foot, F1, MMA. Cinq minutes le matin pour tout savoir, avec attitude.
      Bientot sur Spotify, Apple Podcasts et YouTube.
    </p>
    <div class="platforms">
      <a href="/feed.xml">Flux RSS</a>
    </div>
  </div>
  <footer>(c) 2026 LE BUZZER</footer>
</body>
</html>`;
