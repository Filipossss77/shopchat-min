
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# --- Jednoduché odpovede (uprav podľa seba) ---
INTENTS = {
    "cennik": "💶 Interiér od 69€, jednokrokové leštenie od 149€, svetlomety od 40€/ks.",
    "svetlomety": "🔦 Renovácia: brúsenie + leštenie + ochrana (60–90 min).",
    "ppf": "🛡️ PPF (QUAP): ochrana proti mikroškrabancom a kamienkom.",
    "termín": "📅 Pošli model auta + preferovaný dátum/čas, ozveme sa."
}
SUGGESTIONS = ["CENNÍK", "SVETLOMETY", "PPF", "TERMÍN"]

# --- Mini widget (CSS/JS) ---
WIDGET_CSS = """
#shopchat-bubble{position:fixed;right:20px;bottom:20px;width:56px;height:56px;border-radius:50%;box-shadow:0 8px 24px rgba(0,0,0,.2);display:flex;align-items:center;justify-content:center;cursor:pointer;background:#111;color:#fff;font:600 20px/1 system-ui;z-index:9999}
#shopchat-panel{position:fixed;right:20px;bottom:90px;width:340px;max-width:92vw;height:480px;max-height:70vh;background:#fff;border-radius:16px;box-shadow:0 20px 40px rgba(0,0,0,.25);display:none;flex-direction:column;overflow:hidden;z-index:9999}
#shopchat-header{padding:12px;background:#111;color:#fff;font:600 14px system-ui;display:flex;align-items:center;justify-content:space-between}
#shopchat-body{flex:1;padding:12px;overflow:auto;background:#fafafa}
#shopchat-input{display:flex;gap:8px;padding:10px;background:#fff;border-top:1px solid #eee}
#shopchat-input input{flex:1;padding:10px 12px;border:1px solid #ddd;border-radius:10px;font:14px system-ui}
#shopchat-input button{padding:10px 12px;border-radius:10px;border:0;background:#111;color:#fff;font:600 14px system-ui}
.msg{max-width:80%;margin:6px 0;padding:10px 12px;border-radius:12px;font:14px/1.3 system-ui}
.msg.user{background:#dff0ff;margin-left:auto}
.msg.bot{background:#fff;border:1px solid #eee}
.suggestions{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.suggestions button{border:1px solid #ddd;background:#fff;padding:6px 8px;border-radius:999px;font:12px system-ui;cursor:pointer}
"""

WIDGET_JS = r"""
(function(){
  const API = (window.SHOPCHAT_API || "/api/message");
  const bubble = document.createElement('div'); bubble.id='shopchat-bubble'; bubble.innerText='💬';
  const panel = document.createElement('div'); panel.id='shopchat-panel';
  const header = document.createElement('div'); header.id='shopchat-header';
  header.innerHTML='<span>Detailing Chat</span><button id="shopchat-close" style="background:transparent;border:0;color:#fff;font:16px">✕</button>';
  const body = document.createElement('div'); body.id='shopchat-body';
  const input = document.createElement('div'); input.id='shopchat-input';
  input.innerHTML='<input id="shopchat-text" placeholder="Napíš správu…"/><button id="shopchat-send">Poslať</button>';
  panel.appendChild(header); panel.appendChild(body); panel.appendChild(input);
  document.body.appendChild(bubble); document.body.appendChild(panel);

  const closeBtn = header.querySelector('#shopchat-close');
  const textEl = input.querySelector('#shopchat-text');
  const sendBtn = input.querySelector('#shopchat-send');

  bubble.onclick=()=>{ panel.style.display='flex'; bubble.style.display='none'; textEl.focus(); };
  closeBtn.onclick=()=>{ panel.style.display='none'; bubble.style.display='flex'; };

  function addMsg(text, who){ const d=document.createElement('div'); d.className='msg '+(who||'bot'); d.textContent=text; body.appendChild(d); body.scrollTop=body.scrollHeight; }
  function addSuggestions(list){ if(!list||!list.length) return; const w=document.createElement('div'); w.className='suggestions';
    list.forEach(s=>{ const b=document.createElement('button'); b.textContent=s; b.onclick=()=>{ textEl.value=s; send(); }; w.appendChild(b);});
    body.appendChild(w); body.scrollTop=body.scrollHeight;
  }

  async function send(){
    const text = textEl.value.trim(); if(!text) return;
    addMsg(text,'user'); textEl.value='';
    try{
      const res = await fetch(API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
      const data = await res.json();
      addMsg(data.reply||''); addSuggestions(data.suggestions||[]);
    }catch(e){ addMsg('Ups, vypadok. Skús neskôr.'); }
  }
  sendBtn.onclick=send; textEl.addEventListener('keydown', e=>{ if(e.key==='Enter') send(); });

  setTimeout(()=>{ bubble.click(); addMsg('Ahoj! Pomôžem s cenníkom, termínom alebo PPF.'); addSuggestions(['CENNÍK','SVETLOMETY','PPF','TERMÍN']); }, 700);
})();
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
