from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os, ssl, smtplib
from email.message import EmailMessage

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "tepovacieprace.gava@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_TO = os.getenv("SMTP_TO", "tepovacieprace.gava@gmail.com")


def send_mail(subject: str, body: str, to: str | None = None) -> bool:
    try:
        recipient = to or SMTP_TO
        msg = EmailMessage()
        msg["From"] = SMTP_FROM
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.set_content(body)
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=ctx) as s:
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
    "cenník": "<a href='https://gavatep.eu/cennik' target='_blank' rel='noopener'>💰 Otvor stránku Cenník</a>",
}

SUGGESTIONS = ["Cenník","Renovácia svetlometov","Čistenie interiéru","Čistenie exteriéru","Keramická ochrana","Ochranná PPF fólia Quap"]


# --- FRONTEND ---
WIDGET_JS = r"""
(function(){
  const RESPONSES = {
    "renovácia svetlometov": `""" + INTENTS["renovácia svetlometov"] + """`,
    "čistenie interiéru": `""" + INTENTS["čistenie interiéru"] + """`,
    "čistenie exteriéru": `""" + INTENTS["čistenie exteriéru"] + """`,
    "keramická ochrana": `""" + INTENTS["keramická ochrana"] + """`,
    "ochranná ppf fólia quap": `""" + INTENTS["ochranná ppf fólia quap"] + """`
  };

  // 💬 bublina vpravo dole
  const bubble = document.createElement('div');
  bubble.id = 'shopchat-bubble';
  bubble.innerHTML = 'Chat';
  document.body.appendChild(bubble);

  const panel=document.createElement('div');
  panel.id='shopchat-panel';
  panel.innerHTML=`
    <div id='shopchat-header'><span>Chat</span><button id='closechat' aria-label='Zavrieť'>×</button></div>
    <div id='shopchat-body'></div>
    <div id='shopchat-input'><input placeholder='Napíš správu...'><button aria-label='Poslať'>Poslať</button></div>
  `;
  document.body.appendChild(panel);
  panel.style.display='none';

  // zvuk pri otvorení + automatické otvorenie
  const audio = new Audio("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg");
  function openChat(){
    panel.style.display = 'flex';
    try {
      audio.currentTime = 0;
      audio.play();
    } catch(_) {}
  }
  window.addEventListener('load', ()=>{ openChat(); });

  const body=panel.querySelector('#shopchat-body');
  const input=panel.querySelector('input');
  const send=panel.querySelector('#shopchat-input button');

  function addMsg(txt,who){
    const d=document.createElement('div');
    d.className='msg '+who;
    if(who==='bot' && /<a\s|class="ppf-cards"/i.test(txt)) d.innerHTML=txt;
    else d.textContent=txt;
    body.appendChild(d);
    body.scrollTop=body.scrollHeight;
  }

  function addButtons(labels,onClick,cls='actions'){
    const wrap=document.createElement('div');
    wrap.className=cls;
    labels.forEach(label=>{
      const b=document.createElement('button');
      b.textContent=label;
      b.onclick=()=>onClick(label,wrap);
      wrap.appendChild(b);
    });
    body.appendChild(wrap);
    body.scrollTop=body.scrollHeight;
  }

  function addSuggestions(){
    const b=document.createElement('div');b.className='suggestions';
    ["Cenník","Renovácia svetlometov","Čistenie interiéru","Čistenie exteriéru","Keramická ochrana","Ochranná PPF fólia Quap"].forEach(t=>{
      const btn=document.createElement('button');btn.textContent=t;
      btn.onclick=()=>{
        addMsg(t,'user');
        const key=t.toLowerCase();
        if(key.includes('cenn')) {
          window.open('https://gavatep.eu/cennik','_blank','noopener');
          return;
        }
        if(RESPONSES[key]){
          setTimeout(()=>{ addMsg(RESPONSES[key],'bot'); },200);
        }
      };
      b.appendChild(btn);
    });
    body.appendChild(b);
  }

  bubble.addEventListener('click',()=>{
    panel.style.display='flex';
    try {
      audio.currentTime = 0;
      audio.play();
    } catch(_) {}
    if(!body.dataset.init){
      addMsg('Ahoj 👋 Ako ti môžem pomôcť?','bot');
      addSuggestions();
      body.dataset.init='1';
    }
  });
})();
"""

WIDGET_CSS = r"""
:root{
  --gold:#d4af37;
  --bg:#0b0b0c;
  --bg2:#0f0f10;
  --text:#e9e9ea;
  --muted:#2a2a2a;
  --font: Inter, system-ui, "Segoe UI", Roboto, Arial, sans-serif;
}
#shopchat-bubble{
  position:fixed;right:20px;bottom:20px;width:64px;height:64px;border-radius:50%;
  background:var(--bg2);color:var(--gold);
  display:flex;align-items:center;justify-content:center;
  font:700 20px var(--font);cursor:pointer;z-index:999999;
  border:2px solid var(--gold);
  box-shadow:0 0 15px rgba(212,175,55,0.4),0 8px 30px rgba(0,0,0,.45);
  background-image:linear-gradient(120deg,rgba(212,175,55,0.3) 0%,transparent 40%,rgba(212,175,55,0.3) 80%);
  background-size:200% 200%;
  animation:shine 4s linear infinite;
  transition:transform .2s ease, box-shadow .2s ease;
}
@keyframes shine {
  0% {background-position:200% 0;}
  100% {background-position:-200% 0;}
}
#shopchat-bubble:hover{transform:translateY(-2px);box-shadow:0 10px 36px rgba(0,0,0,.55),0 0 0 5px rgba(212,175,55,.22);}
#shopchat-panel{
  position:fixed;right:20px;bottom:96px;width:380px;max-width:95vw;height:520px;
  background:var(--bg);border-radius:16px;box-shadow:0 24px 60px rgba(0,0,0,.55),0 0 0 1px var(--muted) inset;
  display:none;flex-direction:column;overflow:hidden;z-index:999998;font-family:var(--font);
}
#shopchat-header{
  padding:12px 14px;
  background:linear-gradient(90deg,#0f0f10 0%,#1a1a1b 40%,#0f0f10 80%);
  color:var(--gold);
  display:flex;
  justify-content:space-between;
  align-items:center;
  font-weight:700;
  border-bottom:1px solid var(--muted);
  border-top:1px solid var(--gold);
  background-size:200% 200%;
  animation:shimmer 4s linear infinite;
}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
#shopchat-body{flex:1;padding:12px;overflow:auto;background:var(--bg);color:var(--text);}
#shopchat-input{display:flex;gap:8px;padding:10px;background:var(--bg2);border-top:1px solid var(--muted);}
#shopchat-input input{flex:1;padding:10px 12px;border:1px solid var(--muted);border-radius:10px;background:var(--bg);color:var(--text);}
#shopchat-input button{padding:10px 12px;border-radius:10px;border:none;background:var(--gold);color:#111;font-weight:700;}
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
    elif "ppf" in text or "fólia" in text or "folia" in text:
        reply = INTENTS["ochranná ppf fólia quap"]
    else:
        reply = "Rozumiem. Môžem poslať info o službách alebo cenník."
    return JSONResponse({"reply": reply, "suggestions": SUGGESTIONS})








