/**
 * Cloudflare Worker — LE BUZZER
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

    // MP3 épisode : /audio/YYYY-MM-DD.mp3
    const m = url.pathname.match(/^\/audio\/(\d{4}-\d{2}-\d{2})\.mp3$/);
    if (m) {
      return proxyTo(request, `https://github.com/${REPO}/releases/download/${m[1]}/${m[1]}.mp3`);
    }

    // Clips courts : /clips/YYYY-MM-DD_N.mp4
    const c = url.pathname.match(/^\/clips\/(\d{4}-\d{2}-\d{2})_(\d+)\.mp4$/);
    if (c) {
      return proxyTo(request, `https://github.com/${REPO}/releases/download/${c[1]}/${c[1]}_clip_${c[2]}.mp4`);
    }

    // Cover artwork — pointe vers cover-v1.png dans le repo
    if (url.pathname === "/artwork.jpg" || url.pathname === "/artwork.png") {
      return proxyTo(request, `${RAW}/artwork/cover-v1.png`, "image/png", 86400);
    }

    // Landing page
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
};

// ─── helpers ─────────────────────────────────────────────────────────────────

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

// ─── landing page ─────────────────────────────────────────────────────────────

const LANDING_HTML = `<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>LE BUZZER — Sport QC en 5 minutes</title>
<meta name="description" content="Le podcast sport quotidien francophone quebecois. LNH, NBA, foot, F1, MMA — cinq minutes, tout le drame. Chaque matin a 7h." />
<meta property="og:title" content="LE BUZZER" />
<meta property="og:description" content="Le podcast sport quotidien. Cinq minutes, tout le drame." />
<meta property="og:image" content="https://www.lebuzzer.com/artwork.jpg" />
<meta property="og:url" content="https://www.lebuzzer.com" />
<meta property="og:type" content="website" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600&display=swap" rel="stylesheet" />
<style>
  :root {
    --bg:           #0D0D0D;
    --bg-elev:      #141414;
    --red:          #E63946;
    --yellow:       #FFD60A;
    --cream:        #F1FAEE;
    --cream-dim:    rgba(241,250,238,0.55);
    --hairline:     rgba(230,57,70,0.22);
    --hairline-soft:rgba(241,250,238,0.08);
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html,body{background:var(--bg);color:var(--cream);}
  body{
    font-family:'Inter',system-ui,-apple-system,sans-serif;
    line-height:1.5;
    -webkit-font-smoothing:antialiased;
    overflow-x:hidden;
  }
  ::selection{background:var(--red);color:var(--bg);}
  .wrap{width:100%;max-width:1240px;margin:0 auto;padding:0 24px;}

  /* TOPBAR */
  .topbar{
    display:flex;justify-content:space-between;align-items:center;
    padding:18px 24px;
    border-bottom:1px solid var(--hairline-soft);
    position:sticky;top:0;
    background:rgba(13,13,13,.9);
    backdrop-filter:blur(8px);
    z-index:10;
  }
  .tb-brand{
    font-family:'Anton',sans-serif;font-size:20px;
    letter-spacing:.04em;color:var(--cream);
  }
  .tb-meta{
    display:flex;align-items:center;gap:8px;
    font-size:11px;font-weight:600;letter-spacing:.2em;
    text-transform:uppercase;color:var(--red);
  }
  .pulse{
    width:7px;height:7px;border-radius:50%;
    background:var(--red);
    animation:blink 2s ease-in-out infinite;
  }
  @keyframes blink{0%,100%{opacity:1;}50%{opacity:.25;}}

  /* HERO */
  .hero{padding:72px 24px 64px;border-bottom:1px solid var(--hairline-soft);}
  .hero-label{
    font-size:11px;font-weight:600;letter-spacing:.28em;
    text-transform:uppercase;color:var(--yellow);margin-bottom:18px;
  }
  .hero-wordmark{
    font-family:'Anton',sans-serif;
    font-size:clamp(80px,18vw,196px);
    line-height:.88;color:var(--red);
    letter-spacing:-.01em;margin-bottom:4px;
  }
  .hero-dot{
    display:inline-block;
    width:clamp(24px,4vw,44px);height:clamp(24px,4vw,44px);
    background:var(--yellow);border-radius:50%;
    vertical-align:middle;margin-left:6px;
  }
  .hero-tagline{
    font-family:'Anton',sans-serif;
    font-size:clamp(20px,3.5vw,38px);
    color:var(--cream-dim);letter-spacing:.01em;
    margin-top:18px;margin-bottom:40px;
  }
  .cta-row{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:28px;}
  .btn-primary{
    display:inline-flex;align-items:center;gap:8px;
    background:var(--red);color:var(--cream);
    padding:13px 28px;
    font-size:13px;font-weight:600;letter-spacing:.1em;
    text-transform:uppercase;text-decoration:none;
    transition:background .15s;
  }
  .btn-primary:hover{background:#c8313e;}
  .btn-ghost{
    display:inline-flex;align-items:center;gap:8px;
    background:transparent;color:var(--cream-dim);
    border:1px solid rgba(241,250,238,.18);
    padding:13px 28px;
    font-size:13px;font-weight:500;letter-spacing:.08em;
    text-transform:uppercase;text-decoration:none;
    transition:border-color .15s,color .15s;
  }
  .btn-ghost:hover{border-color:var(--red);color:var(--cream);}
  .social-row{display:flex;gap:20px;flex-wrap:wrap;}
  .social-link{
    font-size:12px;font-weight:500;letter-spacing:.1em;
    text-transform:uppercase;color:var(--cream-dim);
    text-decoration:none;transition:color .15s;
  }
  .social-link:hover{color:var(--yellow);}

  /* SECTIONS */
  .section{padding:72px 24px;border-bottom:1px solid var(--hairline-soft);}
  .sec-num{
    font-size:11px;font-weight:600;letter-spacing:.28em;
    text-transform:uppercase;color:var(--red);margin-bottom:18px;
  }
  .sec-title{
    font-family:'Anton',sans-serif;
    font-size:clamp(34px,6.5vw,70px);
    line-height:.92;color:var(--cream);margin-bottom:28px;
  }
  .sec-body{font-size:16px;line-height:1.72;color:var(--cream-dim);max-width:620px;}

  /* CHAPITRES GRID */
  .chapitres{
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
    gap:1px;
    background:var(--hairline-soft);
    margin-top:44px;
  }
  .chap{
    background:var(--bg);padding:26px;
    transition:background .15s;
  }
  .chap:hover{background:var(--bg-elev);}
  .chap-icon{font-size:26px;display:block;margin-bottom:12px;}
  .chap-name{
    font-family:'Anton',sans-serif;font-size:21px;
    letter-spacing:.02em;color:var(--cream);margin-bottom:6px;
  }
  .chap-desc{font-size:13px;color:var(--cream-dim);line-height:1.55;}

  /* PLATEFORMES */
  .platforms{
    display:grid;
    grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
    gap:14px;
    margin-top:44px;
  }
  .plat{
    display:flex;flex-direction:column;align-items:flex-start;
    padding:22px;border:1px solid var(--hairline-soft);
    text-decoration:none;transition:border-color .15s;
  }
  .plat:hover{border-color:var(--red);}
  .plat-name{
    font-size:13px;font-weight:600;letter-spacing:.1em;
    text-transform:uppercase;color:var(--cream);margin-bottom:5px;
  }
  .plat-hint{font-size:12px;color:var(--cream-dim);}
  .plat-rss .plat-hint{color:var(--yellow);}

  /* FOOTER */
  footer{
    padding:36px 24px;
    display:flex;justify-content:space-between;align-items:center;
    flex-wrap:wrap;gap:14px;
    border-top:1px solid var(--hairline-soft);
  }
  .ft-brand{
    font-family:'Anton',sans-serif;font-size:17px;
    color:var(--cream-dim);letter-spacing:.04em;
  }
  .ft-copy{font-size:12px;color:rgba(241,250,238,.28);}

  @media(max-width:580px){
    .hero{padding:48px 24px;}
    .section{padding:48px 24px;}
    .tb-label{display:none;}
  }
</style>
</head>
<body>

<div class="topbar">
  <span class="tb-brand">LE BUZZER</span>
  <div class="tb-meta">
    <span class="pulse"></span>
    <span class="tb-label">SPORT QC &middot; 7h00 chaque matin</span>
  </div>
</div>

<div class="hero">
  <div class="wrap">
    <p class="hero-label">Podcast sport &middot; francophone &middot; qu&eacute;b&eacute;cois</p>
    <div class="hero-wordmark">LE<br>BUZZER<span class="hero-dot"></span></div>
    <p class="hero-tagline">Cinq minutes. Tout le drame.</p>
    <div class="cta-row">
      <a class="btn-primary" href="https://open.spotify.com/show/lebuzzer" target="_blank" rel="noopener">
        &rarr; Spotify
      </a>
      <a class="btn-ghost" href="https://podcasts.apple.com/podcast/lebuzzer" target="_blank" rel="noopener">
        Apple Podcasts
      </a>
      <a class="btn-ghost" href="/feed.xml">
        Flux RSS
      </a>
    </div>
    <div class="social-row">
      <a class="social-link" href="https://www.tiktok.com/@le_buzzerqc" target="_blank" rel="noopener">TikTok @le_buzzerqc</a>
      <a class="social-link" href="https://www.instagram.com/le_buzzer_qc/" target="_blank" rel="noopener">Instagram @le_buzzer_qc</a>
    </div>
  </div>
</div>

<div class="section">
  <div class="wrap">
    <p class="sec-num">01 / Concept</p>
    <h2 class="sec-title">La revue sport.<br>Sans filtre.</h2>
    <p class="sec-body">
      Chaque matin &agrave; 7h, LE BUZZER g&eacute;n&egrave;re automatiquement un briefing de cinq minutes sur l&rsquo;actualit&eacute; sportive qu&eacute;b&eacute;coise et internationale. LNH, NBA, soccer, F1, MMA &mdash; tout ce qui s&rsquo;est pass&eacute; depuis 24&nbsp;heures, condens&eacute;, honn&ecirc;te, sans rembourrage. Pas d&rsquo;invit&eacute;, pas de hot take tiede : juste les faits et l&rsquo;angle qui compte.
    </p>
  </div>
</div>

<div class="section">
  <div class="wrap">
    <p class="sec-num">02 / Chapitres</p>
    <h2 class="sec-title">Tout le sport.<br>Chaque matin.</h2>
    <div class="chapitres">
      <div class="chap">
        <span class="chap-icon">&#x1F3D2;</span>
        <p class="chap-name">LNH &amp; Canadiens</p>
        <p class="chap-desc">R&eacute;sultats, classements, transactions et rumeurs. Le CH au c&oelig;ur, les 31 autres en contexte.</p>
      </div>
      <div class="chap">
        <span class="chap-icon">&#x1F3C0;</span>
        <p class="chap-name">NBA</p>
        <p class="chap-desc">Matchs de la veille, standings, moves de franchise. Tout ce qui bouge dans la ligue.</p>
      </div>
      <div class="chap">
        <span class="chap-icon">&#x26BD;</span>
        <p class="chap-name">Soccer &amp; Foot</p>
        <p class="chap-desc">CF Montr&eacute;al, MLS, Champions League, Liga, Premier League. Le ballon rond sans fronti&egrave;res.</p>
      </div>
      <div class="chap">
        <span class="chap-icon">&#x1F3CE;&#xFE0F;</span>
        <p class="chap-name">Formule 1</p>
        <p class="chap-desc">R&eacute;sultats de course, qualifications, drama de paddock et guerre des constructeurs.</p>
      </div>
      <div class="chap">
        <span class="chap-icon">&#x1F94A;</span>
        <p class="chap-name">MMA &amp; UFC</p>
        <p class="chap-desc">R&eacute;sultats des cartes, contrats sign&eacute;s, drama et prochaines affiches.</p>
      </div>
      <div class="chap">
        <span class="chap-icon">&#x1F4CB;</span>
        <p class="chap-name">Transactions &amp; Potins</p>
        <p class="chap-desc">Rumeurs confirm&eacute;es, &eacute;changes, agents libres et ce que les insiders disent.</p>
      </div>
    </div>
  </div>
</div>

<div class="section">
  <div class="wrap">
    <p class="sec-num">03 / &Eacute;couter</p>
    <h2 class="sec-title">Cinq minutes.<br>Chaque matin.</h2>
    <p class="sec-body">Abonne-toi sur ta plateforme pr&eacute;f&eacute;r&eacute;e &mdash; le nouvel &eacute;pisode t&rsquo;attend &agrave; 7h00.</p>
    <div class="platforms">
      <a class="plat" href="https://open.spotify.com/show/lebuzzer" target="_blank" rel="noopener">
        <span class="plat-name">Spotify</span>
        <span class="plat-hint">Bient&ocirc;t disponible</span>
      </a>
      <a class="plat" href="https://podcasts.apple.com/podcast/lebuzzer" target="_blank" rel="noopener">
        <span class="plat-name">Apple Podcasts</span>
        <span class="plat-hint">Bient&ocirc;t disponible</span>
      </a>
      <a class="plat plat-rss" href="/feed.xml">
        <span class="plat-name">Flux RSS</span>
        <span class="plat-hint">lebuzzer.com/feed.xml</span>
      </a>
    </div>
  </div>
</div>

<footer class="wrap">
  <span class="ft-brand">LE BUZZER</span>
  <span class="ft-copy">&copy; 2026 LE BUZZER &middot; lebuzzer.com</span>
</footer>

</body>
</html>`;
