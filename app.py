from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import ssl
import smtplib
from email.message import EmailMessage

# --- SMTP nastavenia ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "tepovacieprace.gava@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_TO = os.getenv("SMTP_TO", "tepovacieprace.gava@gmail.com")

def send_mail(subject: str, body: str, to: str | None = None) -> bool:
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


# --- TEXTY ---
INTENTS = {
    "termín": "📅 Rád ti pomôžem s termínom. Pošli mi model auta a dátum, ktorý ti vyhovuje, a ozveme sa.",
    "renovácia svetlometov": "✨ Renovácia svetlometov K2 Vapron ✨ Tvoje svetlá nemusia žiariť len v noci, ale aj na pohľad 😎 Pomocou K2 Vapron im vrátime pôvodný lesk a priehľadnosť 🔧💡 Odstránime zažltnutie, matný povrch a ochránime ich pred UV žiarením ☀️ 🚘 Výsledok? Čisté, jasné a ako nové svetlá – pripravené ukázať cestu 🌙",
    "čistenie interiéru": "🧼 Detailné čistenie interiéru 🧽✨ Každý detail má svoj význam 💺 Interiér tvojho auta si zaslúži viac než len vysávač – venujeme mu 100 % pozornosť 👀 Vyčistíme všetky zákutia, špáry, plasty, sedadlá aj koberce 🚗💨 Odstránime prach, škvrny a zápach, aby si sa cítil ako v novom aute 🌿 Po našej práci zostane interiér čistý, svieži a lesklý 🌟",
    "čistenie exteriéru": "🚘 Detailné čistenie exteriéru 💦✨ Tvoj lak si zaslúži špeciálnu starostlivosť, nie rýchlu umyvárku 🧽 Každý centimeter karosérie dôkladne umyjeme, dekontaminujeme od hrdze, asfaltu a nečistôt 🧴🔧 Používame šetrné produkty, ktoré chránia lak a zanechajú hlboký lesk 🌞 Po našom čistení je auto hladké na dotyk, lesklé na pohľad a pripravené na ochranu 💪",
    "keramická ochrana": "🛡️ Keramická ochrana laku K2 Gravon – až na 5 rokov ✨ Dopraj svojmu autu trvácnu ochranu, ktorá hneď vidieť 👀 K2 Gravon vytvára tvrdý keramický štít, ktorý chráni lak pred UV žiarením, špinou, soľou aj chemikáliami 🚘💎 Auto ostáva dlhšie čisté, voda sa krásne odperľuje 💧 a lesk vydrží roky 🌞 To nie je len lesk – to je ochrana, ktorú cítiš na každom pohľade 🔥",
    "ochranná ppf fólia quap": "Keď chceš, aby tvoj lak vyzeral dlhodobo ako nový, je tu PPF fólia QUAP 🚘 Chráni pred škrabancami, kamienkami, hmyzom aj chemikáliami 🧤 Samoregeneračný povrch zahojí drobné škrabance teplom ☀️🔥 Lak zostáva dokonale lesklý, hladký a stále chránený 💧 To najlepšie, čo môžeš dať svojmu autu.",
    "cenník": "<a href='https://gabatep.eu/cennik' target='_blank' rel='noopener'>💰 Otvor stránku Cenník</a>",
}

SUGGESTIONS = ["CENNÍK", "SVETLOMETY", "INTERIÉR", "EXTERIÉR", "KERAMICKÁ", "PPF"]

# --- WIDGET SCRIPT ---
WIDGET_JS = r"""
(function(){
  const RESPONSES = {
    "renovácia svetlometov": `""" + INTENTS["renovácia svetlometov"] + """`,
    "čistenie interiéru": `""" + INTENTS["čistenie interiéru"] + """`,
    "čistenie exteriéru": `""" + INTENTS["čistenie exteriéru"] + """`,
    "keramická ochrana": `""" + INTENTS["keramická ochrana"] + """`,
    "ochranná ppf fólia quap": `""" + INTENTS["ochranná ppf fólia quap"] + """`
  };

  const bubble=document.createElement('div');
  bubble.id='shopchat-bubble';
  bubble.textContent='Chat';
  document.body.appendChild(bubble);

  const panel=document.createElement('div');
  panel.id='shopchat-panel';
  panel.innerHTML=`
    <div id='shopchat-header'><span>GaVaTep Chat</span><button id='closechat'>×</button></div>
    <div id='shopchat-body'></div>
    <div id='shopchat-input'><input placeholder='Napíš správu...'><button>Poslať</button></div>
  `;
  document.body.appendChild(panel);
  panel.style.display='none';

  bubble.onclick=()=>panel.style.display='flex';
  panel.querySelector('#closechat').onclick=()=>panel.style.display='none';

  const body=panel.querySelector('#shopchat-body');
  const input=panel.querySelector('input');
  const send=panel.querySelector('button');

  function addMsg(txt,who){
    const d=document.createElement('div');
    d.className='msg '+who;
    if(who==='bot' && txt.includes('<a')) d.innerHTML=txt; else d.textContent=txt;
    body.appendChild(d);
    body.scrollTop=body.scrollHeight;
  }

  function addButtons(){
    const b=document.createElement('div');b.className='suggestions';
    ["Cenník","Renovácia svetlometov","Čistenie interiéru","Čistenie exteriéru","Keramická ochrana","Ochranná PPF fólia Quap"].forEach(t=>{
      const btn=document.createElement('button');btn.textContent=t;
      btn.onclick=()=>{
        addMsg(t,'user');
        const key=t.toLowerCase();
        if(RESPONSES[key]) setTimeout(()=>addMsg(RESPONSES[key],'bot'),200);
        else if(key.includes('cenn')) window.open('https://gabatep.eu/cennik','_blank');
      };
      b.appendChild(btn);
    });
    body.appendChild(b);
  }

  bubble.addEventListener('click',()=>{
    if(!body.dataset.init){
      addMsg('Ahoj 👋 Ako ti môžem pomôcť?','bot');
      addButtons();
      body.dataset.init='1';
    }
  });
})();
"""

# --- WIDGET CSS ---
WIDGET_CSS = r"""
#shopchat-bubble{
  position:fixed;right:20px;bottom:20px;width:60px;height:60px;
  border-radius:50%;background:#0f0f10;color:#d4af37;
  display:flex;align-items:center;justify-content:center;
  font-weight:700;cursor:pointer;z-index:9999;
  box-shadow:0 4px 20px rgba(0,0,0,.5);
}
#shopchat-panel{
  position:fixed;right:20px;bottom:90px;width:360px;max-width:95vw;
  height:500px;background:#0b0b0c;color:#fff;border-radius:12px;
  box-shadow:0 4px 40px rgba(0,0,0,.6);
  display:none;flex-direction:column;z-index:9998;
}
#shopchat-header{
  background:#0f0f10;color:#d4af37;padding:10px 14px;
  display:flex;justify-content:space-between;align-items:center;
  font-weight:700;
}
#shopchat-header button{background:none;border:none;color:#d4af37;font-size:20px;cursor:pointer}
#shopchat-body{flex:1;overflow:auto;padding:10px;font-size:14px}
#shopchat-input{display:flex;gap:8px;padding:10px;background:#0f0f10}
#shopchat-input input{flex:1;border-radius:8px;border:1px solid #333;background:#0b0b0c;color:#fff;padding:8px}
#shopchat-input button{background:#d4af37;border:none;color:#111;font-weight:700;padding:8px 12px;border-radius:8px;cursor:pointer}
.msg{margin:6px 0;padding:8px 12px;border-radius:10px;max-width:80%}
.msg.user{background:#1d3557;margin-left:auto}
.msg.bot{background:#2a2a2a}
.suggestions{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.suggestions button{border:1px solid #333;background:#0b0b0c;color:#d4af37;padding:6px 8px;border-radius:20px;cursor:pointer}
"""

app = FastAPI(title="GaVaTep Chat")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/widget.js")
async def widget_js():
    return PlainTextResponse(WIDGET_JS, media_type="application/javascript")

@app.get("/widget.css")
async def widget_css():
    return PlainTextResponse(WIDGET_CSS, media_type="text/css")

@app.post("/api/message")
async def message(payload: dict):
    text = (payload.get("text") or "").lower()
    if "cenn" in text:
        reply = INTENTS["cenník"]
    elif "svetlo" in text:
        reply = INTENTS["renovácia svetlometov"]
    elif "interi" in text:
        reply = INTENTS["čistenie interiéru"]
    elif "exteri" in text:
        reply = INTENTS["čistenie exteriéru"]
    elif "keram" in text:
        reply = INTENTS["keramická ochrana"]
    elif "ppf" in text:
        reply = INTENTS["ochranná ppf fólia quap"]
    else:
        reply = "Rozumiem. Môžem poslať info o službách alebo cenník."
    return JSONResponse({"reply": reply, "suggestions": SUGGESTIONS})
