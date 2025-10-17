
from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# --- Jednoduché odpovede (uprav podľa seba) ---
INTENTS = {
    "cennik": "💶 Interiér od 120€, jednokrokové leštenie od 200€, svetlomety od 30€/ks.Bez ochrany proti UV",
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
