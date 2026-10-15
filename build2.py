#!/usr/bin/env python3
"""Cripto Capitale — pagina briefing generata dai feed Refracto (JSON).
Struttura ripresa da prismanews.com/en (15/10/2026); contenuti SOLO dal feed.
Design system di default: Binance (token letti live il 15/10/2026); il tema "prisma" resta come alternativa.
Interattivo: filtri categoria, ricerca, testo completo, IT/EN, dimensione testo, tema.
Uso: python3 build2.py feed.json feed-en.json index.html
"""
import json, sys, html, re, datetime

feed_it, feed_en, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

SECTORS = [
    ("MERCATI", "MARKETS", r"bitcoin|btc|ether|eth\b|mercato|market|quotazion|prezzo|price|vendite|sell|liquidaz|liquidat|etf|indice|index|s&p|rally|ribass|drops|falls|rallies|outflow|inflow"),
    ("REGOLAMENTAZIONE", "REGULATION", r"regolament|regulat|norm|legge|law|sec\b|commissione|governo|government|stablecoin|genius act|autorità|authorit|licen|supervis|tassa|tax|mica"),
    ("SICUREZZA", "SECURITY", r"cybersicurezza|cybersecur|attacc|attack|hack|vulnerab|sicurezza|securit|furto|theft|exploit|dati personali|personal data|breach"),
    ("INFRASTRUTTURE", "INFRASTRUCTURE", r"exchange|piattaforma|platform|protocollo|protocol|blockchain|rete|network|hyperliquid|deribit|opzioni|options|derivati|derivatives|wallet|oracol|oracle"),
    ("FINANZA TRADIZIONALE", "TRADFI", r"banca|bank|fondo|fund|istituto|institut|azione|stock|ipo|asset manager|treasur|pension"),
]

def sector_of(it):
    txt = (it.get("title", "") + " " + it.get("summary", "")).lower()
    for it_name, en_name, pat in SECTORS:
        if re.search(pat, txt):
            return it_name, en_name
    return "ALTRO", "OTHER"

def fmt(iso):
    return datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))

MONTHS = {
 "it": (["lunedì","martedì","mercoledì","giovedì","venerdì","sabato","domenica"],
        ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]),
 "en": (["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        ["January","February","March","April","May","June","July","August","September","October","November","December"]),
}
def long_date(iso, lang):
    dt = fmt(iso); g, m = MONTHS[lang]
    return f"{g[dt.weekday()]} {dt.day} {m[dt.month-1]} {dt.year}"

def strip_aside(content_html):
    return re.sub(r"<aside[^>]*>.*?</aside>", "", content_html or "", flags=re.S).strip()

LABELS = {
 "it": dict(ultimora="ULTIM'ORA", apertura="Apertura", brief="Briefing di oggi", fonti="fonti",
            lingua="lingua IT", fino="fonti max per sintesi", copertura="Fonti per briefing",
            copertura_note="Quante testate diverse sostengono ogni sintesi. Dato del feed (sourceCount).",
            disclosure="Trasparenza", come="Come leggere questa pagina",
            come_txt="Ogni titolo è una sintesi multi-fonte: il numero dice quante testate la sostengono. Le categorie sono una proposta di navigazione, non un dato del feed (che ha tag quasi vuoti). Clicca un titolo per il testo completo.",
            tutte="TUTTO", cerca="Cerca", chiudi="Chiudi", proto="Prototipo non pubblicato",
            dati="dati: feed Refracto Cripto Capitale (staging)", finestra="item nel feed · finestra 12–15 ottobre 2026",
            brief_oggi="briefing oggi", fonte_sing="sintesi di {n} fonti"),
 "en": dict(ultimora="BREAKING", apertura="Top story", brief="Today's briefings", fonti="sources",
            lingua="language EN", fino="max sources per briefing", copertura="Sources per briefing",
            copertura_note="How many outlets back each synthesis. Feed data (sourceCount).",
            disclosure="Disclosure", come="How to read this page",
            come_txt="Every headline is a multi-source synthesis: the number shows how many outlets back it. The categories are a navigation proposal, not feed data (its tags are nearly empty). Click a headline for the full text.",
            tutte="ALL", cerca="Search", chiudi="Close", proto="Unpublished prototype",
            dati="data: Refracto Cripto Capitale feed (staging)", finestra="items in the feed · window 12–15 October 2026",
            brief_oggi="briefings today", fonte_sing="synthesis of {n} sources"),
}

CSS = """
:root{
  /* DEFAULT = design system Binance (sito crypto n.1 per visite mensili, token letti live 15/10/2026) */
  --bg:#181A20; --paper:#202630; --surface-2:#29313D; --ink:#EAECEF; --ink-2:#EAECEF; --muted:#929AA5;
  --line:#333B47; --line-2:#434C5A; --accent:#FCD535; --accent-2:#F0B90B; --on-accent:#202630; --bar:#FCD535;
  --chip-bg:#29313D; --chip-border:#434C5A; --badge-sec-bg:#29313D; --badge-sec-ink:#EAECEF;
  --display:"IBM Plex Sans",Arial,sans-serif; --body:"IBM Plex Sans",Arial,sans-serif; --mono:"IBM Plex Sans",Arial,sans-serif;
  --body-size:16px; --dek-size:15px; --h2:24px; --h2-big:40px; --h2-grid:18px;
  --chip-radius:4px; --card-radius:10px; --ctrl-radius:4px; --maxw:1280px; --scale:1;
}
html[data-theme="prisma"]{
  /* alternativa: token letti da prismanews.com/en */
  --bg:#f4eddc; --paper:#faf6ec; --surface-2:#f4eddc; --ink:#1b1714; --ink-2:#3d362e; --muted:#7b7263;
  --line:#d8cfbc; --line-2:#c9bfa8; --accent:#b9091b; --accent-2:#b82027; --on-accent:#ffffff; --bar:#0096a7;
  --chip-bg:transparent; --chip-border:#c9bfa8; --badge-sec-bg:rgba(244,237,220,.92); --badge-sec-ink:#1b1714;
  --display:"Fraunces",Georgia,serif; --body:"Newsreader",Georgia,serif; --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
  --body-size:19px; --dek-size:16px; --h2:27px; --h2-big:40px; --h2-grid:19px;
  --chip-radius:999px; --card-radius:0px; --ctrl-radius:0px;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:calc(var(--body-size)*var(--scale));line-height:1.45}
body[data-lang="it"] [data-lang="en"]{display:none}
body[data-lang="en"] [data-lang="it"]{display:none}
.mono{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
.topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 0;border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:700;letter-spacing:-.02em;font-size:22px}
.brand .mark{width:26px;height:26px;background:var(--accent);display:inline-block;clip-path:polygon(50% 0,100% 100%,0 100%)}
.brand small{font-family:var(--mono);font-size:11.5px;font-weight:400;color:var(--muted);letter-spacing:.14em}
.actions{display:flex;align-items:center;gap:10px}
.icon{height:34px;min-width:34px;padding:0 10px;border:1px solid var(--line);display:inline-grid;place-items:center;font-family:var(--mono);font-size:12px;background:transparent;color:var(--ink);cursor:pointer;border-radius:var(--ctrl-radius);text-decoration:none}
.icon:hover{border-color:var(--accent);color:var(--accent)}
.icon.on{background:var(--accent);color:var(--on-accent);border-color:var(--accent);font-weight:600}
#searchbox{display:none;border:1px solid var(--line);background:var(--surface-2);color:var(--ink);font-family:var(--mono);font-size:12px;padding:9px 12px;border-radius:var(--ctrl-radius);min-width:240px}
#searchbox.show{display:block}
.edition{display:flex;justify-content:space-between;gap:16px;padding:10px 0;border-bottom:1px solid var(--line)}
.edition .l{color:var(--accent);font-family:var(--mono);font-size:11.5px;letter-spacing:.1em;text-transform:uppercase}
.ticker{display:flex;align-items:center;gap:14px;border-bottom:1px solid var(--line);padding:12px 0;overflow:hidden}
.tick-label{background:var(--accent);color:var(--on-accent);font-weight:600;font-family:var(--mono);font-size:11px;letter-spacing:.12em;padding:5px 9px;white-space:nowrap;position:relative;z-index:2;border-radius:var(--ctrl-radius)}
.tick-wrap{flex:1;overflow:hidden;min-width:0}
.tick-track{display:flex;gap:22px;white-space:nowrap;font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;animation:slide 70s linear infinite}
.tick-sep{color:var(--accent);margin-left:22px}
@keyframes slide{from{transform:translateX(0)}to{transform:translateX(-50%)}}
@media (prefers-reduced-motion:reduce){.tick-track{animation:none}}
.chips{display:flex;gap:8px;flex-wrap:wrap;padding:16px 0;border-bottom:1px solid var(--line)}
.chip{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;padding:9px 16px;border:1px solid var(--chip-border);background:var(--chip-bg);color:var(--ink);border-radius:var(--chip-radius);cursor:pointer}
.chip:hover{border-color:var(--accent);color:var(--accent)}
.chip.on{background:var(--accent);border-color:var(--accent);color:var(--on-accent);font-weight:600}
.layout{display:grid;grid-template-columns:1fr 360px;gap:32px;padding:24px 0 40px}
.sectlabel{display:flex;align-items:center;gap:14px;margin:6px 0 18px}
.sectlabel:after{content:"";flex:1;height:1px;background:var(--line)}
.story{cursor:pointer}
.story:hover h2{color:var(--accent)}
.story.hidden{display:none}
.story.big .thumb img{width:100%;height:340px;object-fit:cover;object-position:center 30%;display:block}
.thumb{position:relative;overflow:hidden;background:var(--line)}
.thumb img{transition:filter .25s;display:block}
html[data-theme="prisma"] .thumb img{filter:saturate(.9) contrast(1.03) sepia(.08) brightness(.99)}
html[data-theme="cripto"] .thumb img{filter:saturate(.7) brightness(.68) contrast(1.1)}
.thumb:after{content:"";position:absolute;inset:0;pointer-events:none}
html[data-theme="prisma"] .thumb:after{background:linear-gradient(180deg,rgba(244,237,220,.06),rgba(27,23,20,.10))}
html[data-theme="cripto"] .thumb:after{background:linear-gradient(180deg,rgba(24,26,32,.10),rgba(24,26,32,.42))}
.badge-ai,.badge-sec{position:absolute;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;padding:4px 7px;border-radius:2px}
.badge-ai{top:10px;left:10px;background:var(--accent);color:var(--on-accent);font-weight:600}
.badge-sec{bottom:10px;left:10px;background:var(--badge-sec-bg);color:var(--badge-sec-ink)}
h2{font-family:var(--display);font-weight:600;letter-spacing:-.015em;line-height:1.15;margin:14px 0 8px;font-size:var(--h2)}
.story.big h2{font-size:var(--h2-big);margin-top:16px}
.dek{margin:0 0 10px;color:var(--ink-2)}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin-top:34px;border-top:1px solid var(--line);padding-top:26px}
.grid .thumb img{width:100%;height:150px;object-fit:cover;display:block}
.grid h2{font-size:var(--h2-grid);margin-top:12px}
.grid .dek{font-size:var(--dek-size);color:var(--ink-2)}
.dot{margin:0 6px}
.empty{padding:26px 0;color:var(--muted);font-family:var(--mono);font-size:12px}
.rail{display:flex;flex-direction:column;gap:18px}
.card{border:1px solid var(--line);background:var(--paper);padding:18px;border-radius:var(--card-radius)}
.card h3{font-family:var(--display);font-size:21px;margin:0 0 4px}
.bar-row{display:grid;grid-template-columns:104px 1fr 26px;align-items:center;gap:8px;margin:7px 0}
.bar-row .label{white-space:nowrap}
.bar-row .val{text-align:right}
.bar{height:9px;background:var(--bar);border-radius:2px}
.legend{margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
.discl p{margin:6px 0 0;font-size:calc(16px*var(--scale));color:var(--ink-2)}
.discl a{color:var(--accent)}
.foot{border-top:1px solid var(--line);padding:18px 0 40px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.modal{position:fixed;inset:0;background:rgba(11,14,17,.72);display:none;z-index:50;padding:40px 20px;overflow:auto}
.modal.open{display:block}
.modal-card{max-width:820px;margin:0 auto;background:var(--paper);border:1px solid var(--line);border-radius:var(--card-radius);padding:28px 30px 34px}
.modal-card h2{font-size:calc(32px*var(--scale));margin-top:0}
.modal-body p{font-size:calc(17px*var(--scale));line-height:1.55}
.modal-body a{color:var(--accent)}
.modal-close{float:right;font-family:var(--mono);font-size:11px;letter-spacing:.1em;border:1px solid var(--line);background:transparent;color:var(--ink);padding:7px 11px;cursor:pointer;border-radius:var(--ctrl-radius)}
.proto{border:1px solid var(--accent);color:var(--accent);font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;padding:3px 7px;border-radius:2px}
"""

JS = """
const state = {sector:'all', q:''};
function apply(){
  document.querySelectorAll('.story').forEach(el=>{
    const okSector = state.sector==='all' || el.dataset.sector===state.sector || el.dataset.sectorEn===state.sector;
    const okQ = !state.q || (el.dataset.text||'').includes(state.q);
    el.classList.toggle('hidden', !(okSector && okQ));
  });
  document.querySelectorAll('.chip').forEach(c=>c.classList.toggle('on', c.dataset.sector===state.sector));
  document.querySelectorAll('section[data-stream]').forEach(s=>{
    const any = s.querySelectorAll('.story:not(.hidden)').length;
    const e = s.querySelector('.empty'); if(e) e.style.display = any ? 'none' : 'block';
  });
}
function setSector(s){ state.sector = s; apply(); }
function setLang(l){ document.body.dataset.lang = l;
  document.querySelectorAll('[data-setlang]').forEach(b=>b.classList.toggle('on', b.dataset.setlang===l));
  const sb = document.getElementById('searchbox');
  sb.placeholder = l==='it' ? 'Cerca nel briefing…' : 'Search the briefing…'; }
function toggleSearch(){ const b=document.getElementById('searchbox'); b.classList.toggle('show'); if(b.classList.contains('show')) b.focus(); }
function cycleScale(){ const cur=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--scale'))||1;
  const next = cur>1.07?1:(cur>0.97?1.1:1.02);
  document.documentElement.style.setProperty('--scale', next);
  document.getElementById('scalebtn').textContent = next===1?'Aa':(next<1?'Aa-':'Aa+'); }
function toggleTheme(){ document.documentElement.dataset.theme = document.documentElement.dataset.theme==='cripto'?'prisma':'cripto'; }
function openStory(id){ const d = FULL[id]; if(!d) return;
  document.getElementById('m-title').textContent = d.title;
  document.getElementById('m-meta').textContent = d.meta;
  document.getElementById('m-discl').innerHTML = d.discl;
  document.getElementById('m-body').innerHTML = d.body;
  document.getElementById('modal').classList.add('open'); document.body.style.overflow='hidden'; }
function closeStory(){ document.getElementById('modal').classList.remove('open'); document.body.style.overflow=''; }
document.addEventListener('keydown', e=>{ if(e.key==='Escape') closeStory(); });
"""

def build_blocks(items, lang, L, policy):
    newest = items[0]
    edition = fmt(newest["date_published"])
    tot = sum(i["_prisma"]["sourceCount"] for i in items)
    oggi = sum(1 for i in items if fmt(i["date_published"]).date() == edition.date())
    maxsrc = max(i["_prisma"]["sourceCount"] for i in items)
    full = {}

    def card(it, big=False):
        sec_it, sec_en = sector_of(it)
        dt = fmt(it["date_published"]).strftime("%H:%M")
        meta = L["fonte_sing"].format(n=it["_prisma"]["sourceCount"])
        img = f'<img src="{it["image"]}" alt="" loading="lazy">' if it.get("image") else ""
        full[it["id"]] = {"title": it["title"],
                          "meta": f"{meta} · {dt} UTC · {long_date(it['date_published'], lang)}",
                          "body": strip_aside(it.get("content_html", "")),
                          "discl": f'<div class="mono">{L["disclosure"]} · policy {it["_prisma"]["ai"]["policyVersion"]}</div>'}
        text = html.escape((it["title"] + " " + it.get("summary", "")).lower(), quote=True)
        return f'''<article class="story{' big' if big else ''}" data-sector="{sec_it}" data-sector-en="{sec_en}" data-text="{text}" tabindex="0" role="button" onclick="openStory('{it["id"]}')" onkeydown="if(event.key==='Enter')openStory('{it["id"]}')">
  <div class="thumb">{img}<span class="badge-ai">IA</span><span class="badge-sec">{sec_en if lang == 'en' else sec_it}</span></div>
  <div class="body">
    <h2>{html.escape(it["title"])}</h2>
    <p class="dek">{html.escape(it.get("summary", ""))}</p>
    <div class="meta"><span class="mono">{meta}</span><span class="dot">·</span><span class="mono">{dt} UTC</span></div>
  </div>
</article>'''

    ticker = "".join(f'<span class="tick-item">{html.escape(i["title"])}<span class="tick-sep">■</span></span>' for i in items[:8])
    chips = f'<button class="chip" data-sector="all" onclick="setSector(\'all\')">{L["tutte"]}</button>'
    for it_name, en_name, _ in SECTORS:
        key = en_name if lang == "en" else it_name
        chips += f'<button class="chip" data-sector="{key}" onclick="setSector(\'{key}\')">{key}</button>'
    other = "OTHER" if lang == "en" else "ALTRO"
    chips += f'<button class="chip" data-sector="{other}" onclick="setSector(\'{other}\')">{other}</button>'
    bars = "".join(f'<div class="bar-row"><span class="mono label">{fmt(i["date_published"]).strftime("%d/%m %H:%M")}</span>'
                   f'<span class="bar" style="width:{max(4, i["_prisma"]["sourceCount"]/maxsrc*100):.0f}%"></span>'
                   f'<span class="mono val">{i["_prisma"]["sourceCount"]}</span></div>' for i in items[:8])
    grid = "".join(card(i) for i in items[1:])
    return f'''
  <div class="edition" data-lang="{lang}">
    <div class="l">● {L["apertura"]} · {edition.strftime("%H:%M")} UTC · {long_date(newest["date_published"], lang)}</div>
    <div class="mono">{tot} {L["fonti"]} · {L["lingua"]} · {oggi} {L["brief_oggi"]}</div>
  </div>
  <div class="ticker" data-lang="{lang}">
    <span class="tick-label">{L["ultimora"]}</span>
    <div class="tick-wrap"><div class="tick-track">{ticker}{ticker}</div></div>
  </div>
  <nav class="chips" data-lang="{lang}">{chips}</nav>
  <div class="layout">
    <section data-stream data-lang="{lang}">
      <div class="sectlabel"><span class="mono">{L["apertura"]} · {long_date(newest["date_published"], lang)}</span></div>
      {card(newest, big=True)}
      <div class="grid">{grid}</div>
      <div class="empty" style="display:none">∅ nessun risultato</div>
    </section>
    <aside class="rail" data-lang="{lang}">
      <div class="card">
        <h3>{L["brief"]}: {oggi}</h3>
        <div class="mono">{tot} {L["fonti"]} · {L["fino"]}: {maxsrc}</div>
        <div class="legend mono">{L["copertura"]}</div>
        {bars}
        <div class="legend"><span class="mono">{L["copertura_note"]}</span></div>
      </div>
      <div class="card discl">
        <div class="mono">{L["disclosure"]}</div>
        <h3>{policy["short"]}</h3>
        <p>{policy["detail"]}</p>
        <p class="mono">Policy {policy["policyVersion"]} · {policy["reviewStatus"]} · {policy["image"]}</p>
        <p><a href="{policy["methodologyUrl"]}">{policy["methodologyLink"]} →</a></p>
      </div>
      <div class="card">
        <div class="mono">{L["come"]}</div>
        <p style="font-size:calc(16px*var(--scale));color:var(--ink-2);margin:8px 0 0">{L["come_txt"]}</p>
      </div>
    </aside>
  </div>''', full

d_it = json.load(open(feed_it, encoding="utf-8"))
d_en = json.load(open(feed_en, encoding="utf-8"))
policy_it = d_it["_prisma"]["ai"]
policy_en = d_en["_prisma"]["ai"]
blocks_it, full_it = build_blocks(d_it["items"], "it", LABELS["it"], policy_it)
blocks_en, full_en = build_blocks(d_en["items"], "en", LABELS["en"], policy_en)
FULL = {**full_it, **full_en}
full_js = json.dumps(FULL, ensure_ascii=False).replace("</", "<\\/")
policy = d_it["_prisma"]["ai"]

HTML = f'''<!DOCTYPE html>
<html lang="it" data-theme="cripto">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Cripto Capitale — briefing {long_date(d_it["items"][0]["date_published"], "it")}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..500&family=Fraunces:opsz,wght@9..144,400..800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body data-lang="it">
<div class="wrap">
  <div class="topbar">
    <div class="brand"><span class="mark"></span>CRIPTO CAPITALE <small>· PRISMA NEWS</small> <span class="proto">PROTOTIPO</span></div>
    <div class="actions">
      <input id="searchbox" type="search" placeholder="Cerca nel briefing…" oninput="state.q=this.value.trim().toLowerCase(); apply();">
      <button class="icon" onclick="toggleSearch()" title="Cerca (⌕)">⌕</button>
      <button class="icon" data-setlang="it" onclick="setLang('it')">IT</button>
      <button class="icon" data-setlang="en" onclick="setLang('en')">EN</button>
      <button class="icon" id="scalebtn" onclick="cycleScale()" title="Dimensione testo">Aa</button>
      <button class="icon" onclick="toggleTheme()" title="Design system">TEMA</button>
      <a class="icon" href="{policy["methodologyUrl"]}" title="Come lavora Prisma News" target="_blank" rel="noopener">?</a>
    </div>
  </div>
  {blocks_it}
  {blocks_en}
  <div class="foot">
    <span class="mono">{LABELS['it']['proto']} · {LABELS['it']['dati']} · generato {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</span>
    <span class="mono">20 {LABELS['it']['finestra']}</span>
  </div>
</div>

<div class="modal" id="modal" onclick="if(event.target===this)closeStory()">
  <div class="modal-card">
    <button class="modal-close" onclick="closeStory()">✕ {LABELS['it']['chiudi']}</button>
    <div id="m-discl"></div>
    <h2 id="m-title"></h2>
    <div class="mono" id="m-meta" style="margin-bottom:14px"></div>
    <div class="modal-body" id="m-body"></div>
  </div>
</div>

<script>
const FULL = {full_js};
{JS}
setLang('it');
</script>
</body>
</html>
'''
open(out_path, "w", encoding="utf-8").write(HTML)
print("scritto", out_path, len(HTML), "byte ·", len(d_it["items"]), "item IT +", len(d_en["items"]), "item EN")
