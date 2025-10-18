from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import ssl
import smtplib
from email.message import EmailMessage

# --- SMTP nastavenia (cez env premenné) ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # 465=SSL, 587=STARTTLS
SMTP_USER = os.getenv("SMTP_USER", "tepovacieprace.gava@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_TO   = os.getenv("SMTP_TO", "tepovacieprace.gava@gmail.com")

def send_mail(subject: str, body: str, to: str | None = None) -> bool:
    """Jednoduché odoslanie mailu cez SMTP. Vráti True/False."""
    try:
        recipient = to or SMTP_TO
        if not (SMTP_HOST and SMTP_USER and SMTP_PASS and recipient):
            print("MAIL: chýba SMTP konfigurácia")
            return False

        msg = EmailMessage()
        msg["From"] = SMTP_FROM or SMTP_USER
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)

        ctx = ssl.create_default_context()

        if SMTP_PORT == 465:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
                s.ehlo()
                s.starttls(context=ctx)
                s.ehlo()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)

        return True

    except Exception as e:
        print("MAIL_ERROR:", e)
        return False


# --- Odpovede podľa tém ---
INTENTS = {
    "termín": "📅 Rád ti pomôžem s termínom. Pošli mi model auta a dátum, ktorý ti vyhovuje, a ozveme sa.",
    "renovácia svetlometov": "💡 Renovácia svetlometov len za 30 € ks.Bez Ochrany proti UV žiareniu Obnova čírosti, ochrana a profesionálny výsledok.",
    "čistenie interiéru": "🧽 Čisteniu interiéru venujeme maximálnu pozornosť — detailné čistenie všetkých povrchov, sedačiek aj plastov. Našu pracu si viete pozret na našom instagrame link na stranke ",
    "čistenie exteriéru": "🚗 Exterier zahřna detailne umývanie karosérie, dekontaminácia laku-živica,asfalt,náletova Hrzda.",
    "keramická ochrana": "🛡️ Keramická ochrana zabezpečí lesk a odolnosť až na 5 rokov.",
    "ochranná ppf fólia quap": "💎 PPF fólia je najlepšia ochrana, aká existuje — chráni  vozidla pred poškodením ako sú škrabance, kamienky, nečistoty, UV žiarenie. Hydrofóbnosť ma ako jednu zo svojich top vlastnosti.Samozrejme aj samoregenracia ktora patri asi uplne hore čo sa tika ochrany laku a taktiez zaruka 10 rokov na vyblednutie a popraskanie ",
    "cenník": "<a href='https://gabatep.eu/cennik' target='_blank' rel='noopener'>💰 Otvor stránku Cenník</a>",
}

SUGGESTIONS = ["CENNÍK", "SVETLOMETY", "PPF"]

# --- Mini widget (CSS/JS) ---
WIDGET_JS = r"""
(function () {
  const API = (window.SHOPCHAT_API || 'https://shopchat-min-2.onrender.com/api/message');

  // --- Preddefinované odpovede (lokálna mapa pre rýchle odpovede bez volania na server) ---
  const RESPONSES = {
    "renovácia svetlometov": "💡 Renovácia svetlometov len za 30 €. Obnova čírosti, ochrana a profesionálny výsledok.",
    "čistenie interiéru": "🧽 Čisteniu interiéru venujeme maximálnu pozornosť — detailné čistenie všetkých povrchov, sedačiek aj plastov.",
    "čistenie exteriéru": "🚗 Je to pekne čisté a lesklé — umývanie karosérie, dekontaminácia laku a aplikácia ochrany.",
    "keramická ochrana": "🛡️ Keramická ochrana zabezpečí lesk a odolnosť až na 5 rokov.",
    "ochranná ppf folia quap": "💎 PPF fólia je najlepšia ochrana, aká existuje — chráni lak pred kamienkami, škrabancami aj UV žiarením."
  };

  // --- UI ---
  const bubble = document.createElement('div'); bubble.id='shopchat-bubble'; bubble.innerText='Chat';
  const panel  = document.createElement('div'); panel.id='shopchat-panel';
  const header = document.createElement('div'); header.id='shopchat-header';
  header.innerHTML = '<span>GaVaTep Chat</span><button id="shopchat-close" style="background:transparent;border:0;color:#d4af37;font-size:16px;cursor:pointer" aria-label="Zavrieť">×</button>';
  const body   = document.createElement('div'); body.id='shopchat-body';
  const input  = document.createElement('div'); input.id='shopchat-input';
  const field  = document.createElement('input'); field.placeholder='Napíš správu…'; field.setAttribute('aria-label','Správa');
  const send   = document.createElement('button'); send.innerText='Poslať'; send.setAttribute('aria-label','Poslať správu');

  input.append(field, send);
  panel.append(header, body, input);
  document.body.append(bubble, panel);

  try {
    if (!localStorage.getItem('gavatep_chat_opened')) {
      panel.style.display = 'flex';
      localStorage.setItem('gavatep_chat_opened', '1');
    }
  } catch(e){}

  function show(){ panel.style.display='flex'; }
  function hide(){ panel.style.display='none'; }
  bubble.onclick = show;
  header.querySelector('#shopchat-close').onclick = hide;

  function addMsg(text, who){
    const m = document.createElement('div');
    m.className = 'msg ' + who;
    if (who === 'bot' && /<a\s/i.test(text)) {
      m.innerHTML = text;
    } else {
      m.textContent = text;
    }
    body.appendChild(m);
    body.scrollTop = body.scrollHeight;
  }

  function addSuggestions(items){
    // odstráni predchádzajúce návrhy ak sú
    const prev = body.querySelector('.suggestions');
    if (prev) prev.remove();

    const wrap = document.createElement('div');
    wrap.className = 'suggestions';

    items.forEach((t) => {
      const b = document.createElement('button');
      b.textContent = t;

      // Cenník otvorí stránku priamo
      if (t.toLowerCase() === 'cenník' || t.toLowerCase() === 'cennik') {
        b.addEventListener('click', (e) => {
          e.preventDefault();
          window.open('https://gavatep.eu/cennik', '_blank', 'noopener');
        });
      } else {
        b.addEventListener('click', () => {
          // ak máme lokálnu odpoveď v RESPONSES, zobrazíme ju okamžite
          const key = t.toLowerCase();
          if (RESPONSES[key]) {
            addMsg(t, 'user');
            // krátke načasovanie, aby to vyzeralo prirodzene
            setTimeout(() => addMsg(RESPONSES[key], 'bot'), 250);
            return;
          }
          // inak pošleme text na backend (fallback)
          field.value = t;
          send.click();
        });
      }
      wrap.appendChild(b);
    });

    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  // greeting + návrhy
  addMsg('Ahoj! Ako sa máš? S čím ti môžem pomôcť?', 'bot');
  addSuggestions([
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
      const r = await fetch(API, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({text})
      });
      if (!r.ok) throw new Error('HTTP '+r.status);
      const j = await r.json();
      addMsg(j.reply || 'Skús to ešte raz 🙂', 'bot');

      // voliteľne zobraz návrhy z API
      if (Array.isArray(j.suggestions) && j.suggestions.length) {
        addSuggestions(j.suggestions);
      }
    }catch(_){
      addMsg('Ups, skúšam znova neskôr.', 'bot');
    }
  }

  function sendIfNotEmpty(){
    const v = field.value.trim();
    if (v.length) ask(v);
  }

  send.onclick = sendIfNotEmpty;
  field.addEventListener('keydown', (ev) => { if(ev.key==='Enter') sendIfNotEmpty(); });
})();
"""

WIDGET_CSS = r"""
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

ALLOWED = os.getenv("ALLOWED_ORIGIN", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED] if ALLOWED != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def healthz():
    return JSONResponse({"ok": True})

@app.post("/api/message")
async def message(payload: dict):
    raw = (payload.get("text") or "").strip()
    low = raw.lower()

    if low.startswith("termín:") or low.startswith("termin:"):
        subject = "Žiadosť o termín - web chat"
        body = f"Správa od návštevníka:\n\n{raw}"
        ok = send_mail(subject=subject, body=body)
        if ok:
            return JSONResponse({"reply": "Ďakujem! Poslal som to do e-mailu. Ozveme sa čoskoro. 📬","suggestions": SUGGESTIONS})
        else:
            return JSONResponse({"reply": "Mrzí ma to, e-mail sa nepodarilo odoslať. Skúste prosím ešte raz alebo nás kontaktujte telefonicky.","suggestions": SUGGESTIONS})

    if "cenn" in low:
        reply = INTENTS["cenník"]
    elif "svetlo" in low:
        reply = INTENTS["renovácia svetlometov"]
    elif "ppf" in low:
        reply = INTENTS["ochranná ppf fólia quap"]
    elif "term" in low or "rezerv" in low:
        reply = "📅 Rád ti pomôžem s termínom. Pošli mi model auta a dátum, ktorý ti vyhovuje, a ozveme sa."
    elif "interi" in low:
        reply = INTENTS["čistenie interiéru"]
    elif "exteri" in low or "umýv" in low or "umyv" in low:
        reply = INTENTS["čistenie exteriéru"]
    elif "keram" in low:
        reply = INTENTS["keramická ochrana"]
    else:
        reply = "Rozumiem. Môžem poslať cenník, voľné termíny alebo info o PPF."

    return JSONResponse({"reply": reply, "suggestions": SUGGESTIONS})

@app.get("/widget.css")
async def widget_css():
    return PlainTextResponse(WIDGET_CSS, media_type="text/css")

@app.get("/widget.js")
async def widget_js():
    return PlainTextResponse(WIDGET_JS, media_type="application/javascript")
