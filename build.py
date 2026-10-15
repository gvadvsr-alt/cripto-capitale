#!/usr/bin/env python3
"""Genera una pagina 'briefing' per Cripto Capitale a partire dal feed JSON di Refracto.
Struttura ripresa da prismanews.com/en (15/10/2026); contenuti SOLO dal feed.
Uso: python3 build.py <feed.json> <out.html>
"""
import json, sys, html, re, datetime

feed_path, out_path = sys.argv[1], sys.argv[2]
d = json.load(open(feed_path, encoding="utf-8"))
items = d["items"]

# --- tassonomia PROPOSTA (il feed ha tag quasi vuoti: 1 solo valore) -----------------
SECTORS = [
    ("MERCATI", r"bitcoin|btc|ether|eth\b|mercato|quotazion|prezzo|vendite|liquidaz|etf|indice|s&p|rally|ribass|prezz"),
    ("REGOLAMENTAZIONE", r"regolament|norm|legge|sec\b|regolator|commissione|governo|stablecoin|genius act|autorità|vigilanza|tassa"),
    ("SICUREZZA", r"cybersicurezza|attacc|hack|vulnerab|sicurezza|furto|exploit|dati personali|violazion"),
    ("INFRASTRUTTURE", r"exchange|piattaforma|protocollo|blockchain|rete|hyperliquid|deribit|opzioni|derivati|wallet|stablecoin"),
    ("FINANZA TRADIZIONALE", r"banca|bank|fondo|istituto|azione|ipo|asset manager|treasur|pension"),
]
def sector_of(it):
    txt = (it.get("title","") + " " + it.get("summary","")).lower()
    for name, pat in SECTORS:
        if re.search(pat, txt):
            return name
    return "ALTRO"

def fmt_date(iso):
    dt = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return dt

def it_date(iso):
    dt = fmt_date(iso)
    giorni = ["lunedì","martedì","mercoledì","giovedì","venerdì","sabato","domenica"]
    mesi = ["gennaio","febbraio","marzo","aprile","maggio","giugno","luglio","agosto","settembre","ottobre","novembre","dicembre"]
    return f"{giorni[dt.weekday()]} {dt.day} {mesi[dt.month-1]} {dt.year}"

def plain(content_html):
    t = re.sub(r"<[^>]+>", " ", content_html or "")
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t).strip()
    # togli la disclosure iniziale
    t = re.sub(r"^.*?Scopri di più\s*", "", t, flags=re.S)
    return t

newest = items[0]
edition = fmt_date(d["items"][0]["date_published"])
tot_fonti = sum(i["_prisma"]["sourceCount"] for i in items)
tot_lingue = max(i["_prisma"]["languageCount"] for i in items)
oggi = sum(1 for i in items if fmt_date(i["date_published"]).date() == edition.date())
policy = d["_prisma"]["ai"]

def card(it, big=False):
    s = sector_of(it)
    dt = fmt_date(it["date_published"]).strftime("%H:%M")
    meta = f'sintesi di {it["_prisma"]["sourceCount"]} fonti'
    img = f'<img src="{it["image"]}" alt="" loading="lazy">' if it.get("image") else ""
    cls = "story big" if big else "story"
    return f'''<article class="{cls}" data-sector="{s}">
  <div class="thumb">{img}<span class="badge-ai">IA</span><span class="badge-sec">{s}</span></div>
  <div class="body">
    <h2>{html.escape(it["title"])}</h2>
    <p class="dek">{html.escape(it.get("summary",""))}</p>
    <div class="meta"><span class="mono">{meta}</span><span class="dot">·</span><span class="mono">{dt} UTC</span></div>
  </div>
</article>'''

ticker = "".join(f'<span class="tick-item">{html.escape(i["title"])}<span class="tick-sep">■</span></span>' for i in items[:8])

chip_names = ["TUTTO"] + [s for s, _ in SECTORS] + ["ALTRO"]
chips = "".join(f'<button class="chip{" on" if n=="TUTTO" else ""}">{n}</button>' for n in chip_names)

max_src = max(i["_prisma"]["sourceCount"] for i in items)
bars = "".join(
    f'<div class="bar-row"><span class="mono label">{fmt_date(i["date_published"]).strftime("%d/%m %H:%M")}</span>'
    f'<span class="bar" style="width:{max(4, i["_prisma"]["sourceCount"]/max_src*100):.0f}%"></span>'
    f'<span class="mono val">{i["_prisma"]["sourceCount"]}</span></div>'
    for i in items[:8])

grid = "".join(card(i) for i in items[1:])

HTML = f'''<!DOCTYPE html>
<html lang="it" data-theme="prisma">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cripto Capitale — briefing di {it_date(newest["date_published"])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,300..700;1,6..72,300..500&family=Fraunces:opsz,wght@9..144,400..800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
/* ============ DESIGN SYSTEM — due temi ============
   tema "prisma"  = token letti da prismanews.com/en il 15/10/2026: carta #f4eddc, inchiostro #1b1714,
                    accento #b9091b, teal #0096a7, ambra #cfa200, bordi #d8cfbc;
                    font Newsreader (corpo 19px), Fraunces (titoli), JetBrains Mono (metadati 11.5px).
   tema "cripto"  = design system Binance (sito crypto n.1 per visite mensili, letto il 15/10/2026):
                    #181A20 / superfici #202630 · #29313D · bordi #333B47 · testo #EAECEF · unico accento #FCD535
                    · semantici #2EBD85 / #F6465D, font IBM Plex Sans.                        */
:root{{
  --bg:#f4eddc; --paper:#faf6ec; --ink:#1b1714; --ink-2:#3d362e; --muted:#7b7263;
  --line:#d8cfbc; --line-2:#c9bfa8; --accent:#b9091b; --accent-2:#b82027; --teal:#0096a7; --amber:#cfa200;
  --display:"Fraunces",Georgia,serif; --body:"Newsreader",Georgia,serif; --mono:"JetBrains Mono",ui-monospace,Menlo,monospace;
  --body-size:19px; --maxw:1280px;
}}
html[data-theme="cripto"]{{
  --bg:#181A20; --paper:#202630; --ink:#EAECEF; --ink-2:#EAECEF; --muted:#929AA5;
  --line:#333B47; --line-2:#333B47; --accent:#FCD535; --accent-2:#F0B90B; --teal:#2EBD85; --amber:#FCD535;
  --display:"IBM Plex Sans",Arial,sans-serif; --body:"IBM Plex Sans",Arial,sans-serif; --mono:"IBM Plex Sans",Arial,sans-serif;
}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font-family:var(--body);font-size:var(--body-size);line-height:1.45}}
.mono{{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}}
a{{color:inherit}}
.wrap{{max-width:var(--maxw);margin:0 auto;padding:0 24px}}

/* topbar */
.topbar{{display:flex;align-items:center;justify-content:space-between;padding:14px 0;border-bottom:1px solid var(--line)}}
.brand{{display:flex;align-items:center;gap:10px;font-family:var(--display);font-weight:800;letter-spacing:-.02em;font-size:22px}}
.brand .mark{{width:26px;height:26px;background:var(--accent);display:inline-block;clip-path:polygon(50% 0,100% 100%,0 100%)}}
.brand small{{font-family:var(--mono);font-size:11.5px;font-weight:400;color:var(--muted);letter-spacing:.14em}}
.actions{{display:flex;align-items:center;gap:14px}}
.icon{{width:34px;height:34px;border:1px solid var(--line);display:grid;place-items:center;font-family:var(--mono);font-size:12px;background:transparent;color:var(--ink);cursor:pointer}}
.icon.wide{{width:auto;padding:0 12px}}
.toggle{{border:1px solid var(--line);background:transparent;color:var(--ink);font-family:var(--mono);font-size:11px;letter-spacing:.06em;padding:9px 12px;cursor:pointer}}

/* edition */
.edition{{display:flex;justify-content:space-between;gap:16px;padding:10px 0;border-bottom:1px solid var(--line)}}
.edition .l{{color:var(--accent);font-family:var(--mono);font-size:11.5px;letter-spacing:.1em;text-transform:uppercase}}

/* ticker */
.ticker{{display:flex;align-items:center;gap:14px;border-bottom:1px solid var(--line);padding:12px 0;overflow:hidden}}
.tick-label{{background:var(--accent);color:#fff;font-family:var(--mono);font-size:11px;letter-spacing:.12em;padding:5px 9px;white-space:nowrap;position:relative;z-index:2}}
.tick-wrap{{flex:1;overflow:hidden;min-width:0}}
.tick-track{{display:flex;gap:22px;white-space:nowrap;font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;animation:slide 70s linear infinite}}
.tick-sep{{color:var(--accent);margin-left:22px}}
@keyframes slide{{from{{transform:translateX(0)}}to{{transform:translateX(-50%)}}}}
@media (prefers-reduced-motion:reduce){{.tick-track{{animation:none}}}}

/* chips */
.chips{{display:flex;gap:8px;flex-wrap:wrap;padding:16px 0;border-bottom:1px solid var(--line)}}
.chip{{font-family:var(--mono);font-size:11.5px;letter-spacing:.08em;padding:9px 16px;border:1px solid var(--line-2);background:transparent;color:var(--ink);border-radius:999px;cursor:pointer}}
.chip.on{{background:var(--accent);border-color:var(--accent);color:#fff}}
html[data-theme="cripto"] .chip.on{{color:#202630;font-weight:600}}
html[data-theme="cripto"] .tick-label{{color:#202630;font-weight:700}}
html[data-theme="cripto"] .badge-sec{{background:#29313D;color:#EAECEF}}

/* layout */
.layout{{display:grid;grid-template-columns:1fr 360px;gap:32px;padding:24px 0 40px}}
.sectlabel{{display:flex;align-items:center;gap:14px;margin:6px 0 18px}}
.sectlabel:after{{content:"";flex:1;height:1px;background:var(--line)}}
.story.big .thumb img{{width:100%;height:340px;object-fit:cover;object-position:center 30%;display:block}}
.thumb{{position:relative;overflow:hidden;background:var(--line)}}
/* le immagini AI del feed sono chiare e fuori gamma: le porto dentro il tema con un grade,
   non le rigenero (per quello serve un modello di immagini: vedi nota nel footer) */
.thumb img{{transition:filter .25s;display:block}}
html[data-theme="prisma"] .thumb img{{filter:saturate(.9) contrast(1.03) sepia(.08) brightness(.99)}}
html[data-theme="cripto"] .thumb img{{filter:saturate(.7) brightness(.68) contrast(1.1)}}
.thumb:after{{content:"";position:absolute;inset:0;pointer-events:none}}
html[data-theme="prisma"] .thumb:after{{background:linear-gradient(180deg,rgba(244,237,220,.06),rgba(27,23,20,.10))}}
html[data-theme="cripto"] .thumb:after{{background:linear-gradient(180deg,rgba(24,26,32,.10),rgba(24,26,32,.42))}}
.badge-ai,.badge-sec{{position:absolute;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;padding:4px 7px}}
.badge-ai{{top:10px;left:10px;background:var(--accent);color:#fff}}
html[data-theme="cripto"] .badge-ai{{color:#202630;font-weight:700}}
.badge-sec{{bottom:10px;left:10px;background:rgba(244,237,220,.92);color:#1b1714}}
h2{{font-family:var(--display);font-weight:700;letter-spacing:-.015em;line-height:1.12;margin:14px 0 8px;font-size:27px}}
.story.big h2{{font-size:40px;margin-top:16px}}
.dek{{margin:0 0 10px;color:var(--ink-2)}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin-top:34px;border-top:1px solid var(--line);padding-top:26px}}
.grid .thumb img{{width:100%;height:150px;object-fit:cover;display:block}}
.grid h2{{font-size:19px;margin-top:12px}}
.grid .dek{{font-size:16px;color:var(--ink-2)}}
.dot{{margin:0 6px}}

/* rail */
.rail{{display:flex;flex-direction:column;gap:18px}}
.card{{border:1px solid var(--line);background:var(--paper);padding:18px}}
.card h3{{font-family:var(--display);font-size:21px;margin:0 0 4px}}
.bar-row{{display:grid;grid-template-columns:104px 1fr 26px;align-items:center;gap:8px;margin:7px 0}}
.bar{{height:9px;background:var(--teal)}}
.bar-row .val{{text-align:right}}
.bar-row .label{{white-space:nowrap}}
.legend{{margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}}
.discl p{{margin:6px 0 0;font-size:16px;color:var(--ink-2)}}
.discl a{{color:var(--accent)}}
.foot{{border-top:1px solid var(--line);padding:18px 0 40px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}}
</style>
</head>
<body>
<div class="wrap">
  <div class="topbar">
    <div class="brand"><span class="mark"></span>CRIPTO CAPITALE <small>· PRISMA NEWS</small></div>
    <div class="actions">
      <button class="icon">⌕</button>
      <button class="icon">▤</button>
      <button class="icon wide">IT ▾</button>
      <button class="toggle" onclick="document.documentElement.dataset.theme = document.documentElement.dataset.theme==='prisma'?'cripto':'prisma'">TEMA</button>
      <button class="icon">Aa</button>
      <button class="icon wide">ACCEDI</button>
    </div>
  </div>

  <div class="edition">
    <div class="l">● Edizione delle {edition.strftime("%H:%M")} UTC · {it_date(newest["date_published"])}</div>
    <div class="mono">{tot_fonti} fonti · lingua IT · {oggi} briefing oggi</div>
  </div>

  <div class="ticker">
    <span class="tick-label">ULTIM'ORA</span>
    <div class="tick-wrap"><div class="tick-track">{ticker}{ticker}</div></div>
  </div>

  <nav class="chips">{chips}</nav>

  <div class="layout">
    <section>
      <div class="sectlabel"><span class="mono">Apertura · {it_date(newest["date_published"])}</span></div>
      {card(newest, big=True)}
      <div class="grid">{grid}</div>
    </section>

    <aside class="rail">
      <div class="card">
        <h3>Briefing di oggi: {oggi}</h3>
        <div class="mono">{tot_fonti} fonti · fino a {tot_lingue} lingue per sintesi</div>
        <div class="legend mono">Fonti per briefing</div>
        {bars}
        <div class="legend"><span class="mono">Quante testate diverse sostengono ogni sintesi. Dato del feed (sourceCount).</span></div>
      </div>
      <div class="card discl">
        <div class="mono">Trasparenza</div>
        <h3>{policy["short"]}</h3>
        <p>{policy["detail"]}</p>
        <p class="mono">Policy {policy["policyVersion"]} · revisione: {policy["reviewStatus"]} · immagini {policy["image"].lower()}</p>
        <p><a href="{policy["methodologyUrl"]}">{policy["methodologyLink"]} →</a></p>
      </div>
      <div class="card">
        <div class="mono">Come leggere questa pagina</div>
        <p style="font-size:16px;color:var(--ink-2);margin:8px 0 0">Ogni titolo è una sintesi multi-fonte: il numero accanto dice quante testate la sostengono. Le categorie sono una proposta di navigazione, non un dato del feed (che ha tag quasi vuoti).</p>
      </div>
    </aside>
  </div>

  <div class="foot">
    <span class="mono">Prototipo non pubblicato · dati: feed Refracto Cripto Capitale (staging) · generato il {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</span>
    <span class="mono">20 item nel feed · finestra 12–15 ottobre 2026</span>
  </div>
</div>
</body>
</html>
'''
open(out_path, "w", encoding="utf-8").write(HTML)
print("scritto", out_path, len(HTML), "byte ·", len(items), "item ·", oggi, "briefing oggi")
