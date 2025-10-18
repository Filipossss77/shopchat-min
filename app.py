from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os, ssl, smtplib
from email.message import EmailMessage

# --- SMTP (ak používaš odosielanie e-mailov) ---
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "tepovacieprace.gava@gmail.com")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
SMTP_TO   = os.getenv("SMTP_TO", "tepovacieprace.gava@gmail.com")

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


# --- TEXTY (ponechané podľa tvojho zadania) ---
INTENTS = {
    "termín": "📅 Rád ti pomôžem s termínom. Pošli mi model auta a dátum, ktorý ti vyhovuje, a ozveme sa.",
    "renovácia svetlometov": "✨ Renovácia svetlometov K2 Vapron ✨ Tvoje svetlá nemusia žiariť len v noci, ale aj na pohľad 😎 Pomocou K2 Vapron im vrátime pôvodný lesk a priehľadnosť 🔧💡 Odstránime zažltnutie, matný povrch a ochránime ich pred UV žiarením ☀️ 🚘 Výsledok? Čisté, jasné a ako nové svetlá – pripravené ukázať cestu 🌙",
    "čistenie interiéru": "🧼 Detailné čistenie interiéru 🧽✨ Každý detail má svoj význam 💺 Interiér tvojho auta si zaslúži viac než len vysávač – venujeme mu 100 % pozornosť 👀 Vyčistíme všetky zákutia, špáry, plasty, sedadlá aj koberce 🚗💨 Odstránime prach, škvrny a zápach, aby si sa cítil ako v novom aute 🌿 Po našej práci zostane interiér čistý, svieži a lesklý 🌟",
    "čistenie exteriéru": "🚘 Detailné čistenie exteriéru 💦✨ Tvoj lak si zaslúži špeciálnu starostlivosť, nie rýchlu umyvárku 🧽 Každý centimeter karosérie dôkladne umyjeme, dekontaminujeme od hrdze, asfaltu a nečistôt 🧴🔧 Používame šetrné produkty, ktoré chránia lak a zanechajú hlboký lesk 🌞 Po našom čistení je auto hladké na dotyk, lesklé na pohľad a pripravené na ochranu 💪",
    "keramická ochrana": "🛡️ Keramická ochrana laku K2 Gravon – až na 5 rokov ✨ Dopraj svojmu autu trvácnu ochranu, ktorá hneď vidieť 👀 K2 Gravon vytvára tvrdý keramický štít, ktorý chráni lak pred UV žiarením, špinou, soľou aj chemikáliami 🚘💎 Auto ostáva dlhšie čisté, voda sa krásne odperľuje 💧 a lesk vydrží roky 🌞 To nie je len lesk – to je ochrana, ktorú cítiš na každom pohľade 🔥",
    "ochranná ppf fólia quap": "Keď chceš, aby tvoj lak vyzeral dlhodobo ako nový, je tu PPF fólia QUAP 🚘 Chráni pred škrabancami, kamienkami, hmyzom aj chemikáliami 🧤 Samoregeneračný povrch zahojí drobné škrabance teplom ☀️🔥 Lak zostáva dokonale lesklý, hladký a stále chránený 💧 To najlepšie, čo môžeš dať svojmu autu.",
    "cenník": "<a href='https://gavatep.eu/cennik' target='_blank' rel='noopener'>💰 Otvor stránku Cenník</a>",
}

SUGGESTIONS = ["Cenník","Renovácia Svetlometov","Čistenie interiéru","Čistenie exteriéru","Keramická Ochrana","Ochranná PPF Folia Quap"]


# --- FRONTEND (návrat k pôvodnému vzhľadu/štýlu) ---
WIDGET_JS = r"""
(function () {
  // Lokálne odpovede (klik hneď vypíše text)
  const RESPONSES = {
    "renovácia svetlometov": `""" + INTENTS["renovácia svetlometov"] + """`,
    "čistenie interiéru": `""" + INTENTS["čistenie interiéru"] + """`,
    "čistenie exteriéru": `""" + INTENTS["čistenie exteriéru"] + """`,
    "keramická ochrana": `""" + INTENTS["keramická ochrana"] + """`,
    "ochranná ppf fólia quap": `""" + INTENTS["ochranná ppf fólia quap"] + """`,
    "ochranná ppf folia quap": `""" + INTENTS["ochranná ppf fólia quap"] + """`
  };

  // UI (pôvodná bublina a panel)
  const bubble = document.createElement('div'); bubble.id='shopchat-bubble'; bubble.innerText='Chat';
  const panel  = document.createElement('div'); panel.id='shopchat-panel';
  const header = document.createElement('div'); header.id='shopchat-header';
  header.innerHTML = '<span>GaVaTep Chat</span><button id="shopchat-close" aria-label="Zavrieť" style="background:transparent;border:0;color:#d4af37;font-size:16px;cursor:pointer">×</button>';
  const body   = document.createElement('div'); body.id='shopchat-body';
  const input  = document.createElement('div'); input.id='shopchat-input';
  const field  = document.createElement('input'); field.placeholder='Napíš správu…'; field.setAttribute('aria-label','Správa');
  const send   = document.createElement('button'); send.innerText='Poslať'; send.setAttribute('aria-label','Poslať správu');

  input.append(field, send);
  panel.append(header, body, input);
  document.body.append(bubble, panel);

  panel.style.display = 'none'; // neotvárať automaticky

  function show(){ panel.style.display='flex'; }
  function hide(){ panel.style.display='none'; }
  bubble.onclick = show;
  header.querySelector('#shopchat-close').onclick = hide;

  function addMsg(text, who){
    const m = document.createElement('div');
    m.className = 'msg ' + who;
    if (who === 'bot' && /<a\s/i.test(text)) m.innerHTML = text;
    else m.textContent = text;
    body.appendChild(m);
    body.scrollTop = body.scrollHeight;
    return m;
  }

  function addSuggestions(items){
    const prev = body.querySelector('.suggestions'); if (prev) prev.remove();
    const wrap = document.createElement('div'); wrap.className = 'suggestions';
    items.forEach((t) => {
      const b = document.createElement('button'); b.textContent = t;
      if (t.toLowerCase().includes('cenn')) {
        b.addEventListener('click', (e) => { e.preventDefault(); window.open('https://gavatep.eu/cennik','_blank','noopener'); });
      } else {
        b.addEventListener('click', () => {
          const key = t.toLowerCase();
          addMsg(t, 'user');
          if (RESPONSES[key]) {
            setTimeout(() => {
              addMsg(RESPONSES[key], 'bot');
              if (key.includes('ppf')) showPPFQuestion(); // PPF follow-up nechávame
            }, 200);
          } else {
            field.value = t; send.click();
          }
        });
      }
      wrap.appendChild(b);
    });
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  // PPF follow-up (cenník + kontakt) — iba text/flow, bez zmien štýlu
  function showPPFQuestion(){
    addMsg("Chceš spraviť cenník na svoje auto?", 'bot');
    const actions = document.createElement('div'); actions.className='actions';
    ["Áno","Nie"].forEach(lbl=>{
      const btn=document.createElement('button'); btn.textContent=lbl;
      btn.onclick=()=>{
        addMsg(lbl,'user'); actions.remove();
        if(lbl==="Áno"){
          const pricing = 
`ŠTANDARD
(kapota, predný nárazník, predné svetlá, spätné zrkadlá)
od 800 €

PREMIUM
(kapota, predný nárazník, predné blatníky, predné svetlá, spätné zrkadlá, predná strecha, A stĺpiky)
od 1200 €

KOMPLET
(celé auto)
od 2400 €

INDIVIDUÁL
(balík na mieru vyskladaný podľa vás)
cena dohodou`;
          addMsg(pricing,'bot');

          // otázka na kontakt
          addMsg("Chceš nás kontaktovať?", 'bot');
          const contact = document.createElement('div'); contact.className='actions';
          ["Áno","Nie"].forEach(c=>{
            const b=document.createElement('button'); b.textContent=c;
            b.onclick=()=>{
              addMsg(c,'user'); contact.remove();
              if(c==="Áno"){ window.location.href="https://www.gavatep.eu/kontakt/"; }
              else { addMsg("V pohode. Keď budeš chcieť, napíš model auta a pripravíme presnú cenu. 🙂",'bot'); }
            };
            contact.appendChild(b);
          });
          body.appendChild(contact);

        } else {
          addMsg("OK — keď budeš chcieť neskôr, ozvi sa. 🙂",'bot');
        }
      };
      actions.appendChild(btn);
    });
    body.appendChild(actions);
    body.scrollTop = body.scrollHeight;
  }

  // Pozdrav a návrhy až po prvom otvorení
  bubble.addEventListener('click', () => {
    if (!body.dataset.greeted) {
      addMsg('Ahoj! Ako sa máš? S čím ti môžem pomôcť?', 'bot');
      addSuggestions(%s);
      body.dataset.greeted = '1';
    }
  });

  async function ask(text){
    addMsg(text, 'user'); field.value='';
    try{
      const r = await fetch('/api/message', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text}) });
      if (!r.ok) throw new Error();
      const j = await r.json();
      addMsg(j.reply || 'Skús to ešte raz 🙂', 'bot');
      if ((/ppf|fólia|folia/i).test(text)) showPPFQuestion();
    }catch(_){ addMsg('Ups, skúšam znova neskôr.', 'bot'); }
  }

  function sendIfNotEmpty(){ const v=field.value.trim(); if(v.length) ask(v); }
  send.onclick = sendIfNotEmpty;
  field.addEventListener('keydown', (ev) => { if(ev.key==='Enter') sendIfNotEmpty(); });
})();
""" % (str(SUGGESTIONS)))

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
.msg{max-width:80%;margin:6px 0;padding:10px 12px;border-radius:12px;font:14px/1.3 system-ui;white-space:pre-line}
.msg.user{background:#19324a;color:#e9f2ff;margin-left:auto;border:1px solid #244a6b}
.msg.bot{background:#111214;color:#e9e9ea;border:1px solid #2a2a2a;white-space:pre-line}
.suggestions{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.suggestions button{
  border:1px solid #2a2a2a;background:#0b0b0c;color:#d4af37;padding:6px 8px;border-radius:999px;font:12px system-ui;cursor:pointer
}
.actions{display:flex;gap:8px;margin-top:8px}
.actions button{
  border:1px solid #2a2a2a;background:#0b0b0c;color:#e9e9ea;padding:6px 10px;border-radius:10px;font:12px system-ui;cursor:pointer
}
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
