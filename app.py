
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# --- Jednoduché odpovede (uprav podľa seba) ---
INTENTS = {
    "termín": "📅 Rád ti pomôžem s termínom. Pošli mi model auta a dátum, ktorý ti vyhovuje, a ozveme sa.",
    "renovácia svetlometov": "✨ Robíme brúsenie, leštenie aj ochranu svetlometov. Trvá to približne 200 minút.Všetko potrebne najdes sekcia cenník.",
    "čistenie interiéru": "🧽 Hĺbkové čistenie interiéru — sedačky, plasty, koberce aj všetky detaily.Všetko potrebne najdes sekcia cenník.",
    "čistenie exteriéru": "🚗 Umývanie karosérie, dekontaminácia laku a aplikácia vosku alebo ochrany.",
    "keramická ochrana": "🛡️ Keramická ochrana chráni lak, disky a okná až na 5 rokov. Lesk a ochrana v jednom.",
    "ochranná ppf fólia quap": "💎 Ochranná fólia Quap chráni lak pred kamienkami, škrabancami a UV žiarením.Všetko potrebne najdes sekcia cenník.",
    "cenník": "<a href='https://gabatep.eu/cennik' target='_blank'>💰 Otvor stránku Cenník</a>",
}

SUGGESTIONS = ["CENNÍK", "SVETLOMETY", "PPF", "TERMÍN"]

# --- Mini widget (CSS/JS) ---
WIDGET_JS = """
(function () {
  const API = (window.SHOPCHAT_API || '/api/message');

  // --- vytvorenie bubliny/panelu ---
  const bubble = document.createElement('div'); bubble.id='shopchat-bubble'; bubble.innerText='Chat';
  const panel  = document.createElement('div'); panel.id='shopchat-panel';
  const header = document.createElement('div'); header.id='shopchat-header';
  header.innerHTML = '<span>GaVaTep Chat</span><button id="shopchat-close" style="background:transparent;border:0;color:#d4af37;font-size:16px;cursor:pointer">×</button>';
  const body   = document.createElement('div'); body.id='shopchat-body';
  const input  = document.createElement('div'); input.id='shopchat-input';
  const field  = document.createElement('input'); field.placeholder='Napíš správu…';
  const send   = document.createElement('button'); send.innerText='Poslať';

  input.append(field, send);
  panel.append(header, body, input);
  document.body.append(bubble, panel);

  // auto-open iba pri prvej návšteve
  try {
    if (!localStorage.getItem('gavatep_chat_opened')) {
      panel.style.display = 'flex';
      localStorage.setItem('gavetaep_chat_opened', '1');
    }
  } catch(e){}

  function show(){ panel.style.display='flex'; }
  function hide(){ panel.style.display='none'; }
  bubble.onclick = show;
  header.querySelector('#shopchat-close').onclick = hide;

  function addMsg(text, who){
    const m = document.createElement('div');
    m.className = 'msg ' + who;
    m.textContent = text;
    body.appendChild(m);
    body.scrollTop = body.scrollHeight;
  }

  function addSuggestions(items){
    const wrap = document.createElement('div');
    wrap.className = 'suggestions';

    items.forEach((t) => {
      const b = document.createElement('button');
      b.textContent = t;

      // špeciálne: Cenník otvorí stránku
      if (t.toLowerCase() === 'cenník' || t.toLowerCase() === 'cennik') {
        b.addEventListener('click', (e) => {
          e.preventDefault();
          window.open('https://gavatep.eu/cennik', '_blank', 'noopener');
        });
      } else {
        // ostatné vypočítajú odpoveď ako doteraz
        b.addEventListener('click', () => {
          field.value = t;
          send.click();
        });
      }
      wrap.appendChild(b);
    });

    body.appendChild(wrap);
  }

  // greeting + návrhy
  addMsg('Ahoj! Ako sa máš? S čím ti môžem pomôcť?', 'bot');
  addSuggestions([
    'Termín',
    'Cenník',
    'Renovácia Svetlometov',
    'Čistenie interiéru',
    'Čistenie exteriéru',
    'Keramická Ochrana',
    'Ochranná PPF Folia Quap'
  ]);

  async function ask(text){
    addMsg(text, 'user'); field.value='';
    try{
      const r = await fetch(API,{method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text})});
      const j = await r.json();
      addMsg(j.reply || 'Skús to ešte raz 🙂', 'bot');
    }catch(_){
      addMsg('Ups, skúšam znova neskôr.', 'bot');
    }
  }

  send.onclick = () => {
    if ((field.value.trim()).length) ask(field.value.trim());
  };
  field.addEventListener('keydown', (ev) => { if(ev.key==='Enter') send.click(); });
})();
"""



WIDGET_CSS = """
#shopchat-bubble{
  position:fixed;right:20px;bottom:20px;width:60px;height:60px;border-radius:50%;
  background:#0f0f10;color:#d4af37;font:700 22px/1 system-ui;display:flex;align-items:center;justify-content:center;
  box-shadow:0 10px 30px rgba(0,0,0,.35), 0 0 0 2px #2a2a2a inset;cursor:pointer;transition:transform .2s ease, background .2s;
  z-index:9999
}
#shopchat-bubble:hover{transform:translateY(-2px);background:#151517}

#shopchat-panel{
  position:fixed;right:20px;bottom:90px;width:360px;max-width:92vw;height:520px;max-height:78vh;
  background:#0b0b0c;border-radius:16px;box-shadow:0 20px 48px rgba(0,0,0,.55), 0 0 0 1px #2a2a2a inset;
  display:none;flex-direction:column;overflow:hidden;z-index:9999
}
#shopchat-header{
  padding:12px 14px;background:#0f0f10;color:#d4af37;
  font:700 14px system-ui;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #2a2a2a
}
#shopchat-body{flex:1;padding:12px;overflow:auto;background:#0b0b0c}
#shopchat-input{display:flex;gap:8px;padding:10px;background:#0f0f10;border-top:1px solid #2a2a2a}
#shopchat-input input{
  flex:1;padding:10px 12px;border:1px solid #2a2a2a;border-radius:10px;background:#0b0b0c;color:#e9e9ea;font:14px system-ui
}
#shopchat-input button{
  padding:10px 12px;border-radius:10px;border:0;background:#d4af37;color:#121213;font:700 14px system-ui
}
.msg{max-width:80%;margin:6px 0;padding:10px 12px;border-radius:12px;font:14px/1.3 system-ui}
.msg.user{background:#19324a;color:#e9f2ff;margin-left:auto;border:1px solid #244a6b}
.msg.bot{background:#111214;color:#e9e9ea;border:1px solid #2a2a2a}
.suggestions{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.suggestions button{
  border:1px solid #2a2a2a;background:#0b0b0c;color:#d4af37;padding:6px 8px;border-radius:999px;font:12px system-ui;cursor:pointer
}
"""


app = FastAPI(title="ShopChat Minimal")

# Povolené domény (uprav v prostredí na tvoju Shoptet doménu)
ALLOWED = os.getenv("ALLOWED_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED] if ALLOWED != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/message")
async def message(payload: dict):
    text = (payload.get("text") or "").strip().lower()
    if "cenn" in text:
        reply = INTENTS["cennik"]
    elif "svetlo" in text:
        reply = INTENTS["svetlomety"]
    elif "ppf" in text:
        reply = INTENTS["ppf"]
    elif "term" in text or "rezerv" in text:
        reply = INTENTS["termín"]
    else:
        reply = "Rozumiem. Môžem poslať cenník, voľné termíny alebo info o PPF."
    return JSONResponse({"reply": reply, "suggestions": SUGGESTIONS})

@app.get("/widget.css")
async def widget_css():
    return PlainTextResponse(WIDGET_CSS, media_type="text/css")

@app.get("/widget.js")
async def widget_js():
    return PlainTextResponse(WIDGET_JS, media_type="application/javascript")
