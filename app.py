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
  bubble.innerHTML = '💬';
  document.body.appendChild(bubble);

  const panel=document.createElement('div');
  panel.id='shopchat-panel';
  panel.innerHTML=`
    <div id='shopchat-header'><span>GaVaTep</span><button id='closechat' aria-label='Zavrieť'>×</button></div>
    <div id='shopchat-body'></div>
    <div id='shopchat-input'><input placeholder='Napíš správu...'><button aria-label='Poslať'>Poslať</button></div>
  `;
  document.body.appendChild(panel);
  panel.style.display='none';

  const body=panel.querySelector('#shopchat-body');
  const input=panel.querySelector('input');
  const send=panel.querySelector('#shopchat-input button');

  function addMsg(txt,who){
    const d=document.createElement('div');
    d.className='msg '+who;
    // povolíme iba odkazy a naše PPF karty
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

  // PPF: cenník ako karty + následná otázka na kontakt
  function showPPFPricingFlow(){
    addMsg("Chceš spraviť cenník na svoje auto?",'bot');
    addButtons(["Áno","Nie"],(answer,wrap)=>{
      addMsg(answer,'user');
      wrap.remove();
      if(answer==="Áno"){
        const cards = `
<div class="ppf-cards">
  <div class="ppf-card">
    <div class="t">ŠTANDARD</div>
    <div class="d">(kapota, predný nárazník, predné svetlá, spätné zrkadlá)</div>
    <div class="p">od 800€</div>
  </div>
  <div class="ppf-card">
    <div class="t">PREMIUM</div>
    <div class="d">(kapota, predný nárazník, predné blatníky, predné svetlá, spätné zrkadlá, predná strecha, A stĺpiky)</div>
    <div class="p">od 1200€</div>
  </div>
  <div class="ppf-card">
    <div class="t">KOMPLET</div>
    <div class="d">(celé auto)</div>
    <div class="p">od 2400€</div>
  </div>
  <div class="ppf-card">
    <div class="t">INDIVIDUÁL</div>
    <div class="d">(balík na mieru vyskladaný podľa vás)</div>
    <div class="p">cena dohodou</div>
  </div>
</div>`;
        addMsg(cards,'bot');

        addMsg("Chceš nás kontaktovať?", 'bot');
        addButtons(["Áno","Nie"], (ans2, wrap2)=>{
          addMsg(ans2,'user');
          wrap2.remove();
          if(ans2==="Áno"){
            window.location.href="https://www.gavatep.eu/kontakt/";
          } else {
            addMsg("Jasné. Keď budeš chcieť, klikni na Cenník alebo napíš model auta a pripravíme presnú cenu. 🙂", 'bot');
          }
        }, 'actions contact');
      } else {
        addMsg("OK — keď budeš chcieť neskôr, ozvi sa. 🙂",'bot');
      }
    });
  }

  // Svetlomety: najprv pôvodný promo text, potom otázka s detailným postupom
  function showHeadlightSteps(){
    addMsg("Chceš vedieť ako vyzerá renovácia svetlometov a čo treba robiť potom?",'bot');
    addButtons(["Áno","Nie"],(answer,wrap)=>{
      addMsg(answer,'user');
      wrap.remove();
      if(answer==="Áno"){
        const detail = `✨ Renovácia svetlometov ✨
Počas renovácie odstránime zoxidovaný povrch svetlometov pomocou precízneho brúsenia – začíname nasucho, potom pokračujeme mokrým brúsením od zrnitosti 800 až po 3000. 🔧
Následne svetlá dôkladne odmastíme a aplikujeme K2 Vapron – špeciálnu tekutinu, ktorá sa po nahriatí odparí a chemicky zjednotí povrch plastu. Výsledok? 🌟 Čisté, priehľadné a ako nové svetlomety.
Ale tu to nekončí – takto zrenovované svetlá treba ochrániť.
🔹 Odporúčame keramickú ochranu K2 Gravon s trvácnosťou až 5 rokov,
alebo prémiové riešenie – PPF fóliu, ktorá chráni pred UV žiarením, škrabancami a má aj samoregeneračné vlastnosti. 💪
💡 Vaše svetlá budú nielen svietiť lepšie, ale aj vyzerať skvelo.`;
        addMsg(detail,'bot');
      } else {
        addMsg("V poriadku 🙂",'bot');
      }
    });
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
          setTimeout(()=>{
            addMsg(RESPONSES[key],'bot');           // najprv pôvodný text danej sekcie
            if(key.includes('ppf')) showPPFPricingFlow();     // PPF karty
            if(key.includes('svetlomet')) showHeadlightSteps(); // otázka k svetlám
          },200);
        }
      };
      b.appendChild(btn);
    });
    body.appendChild(b);
  }

  // otváranie/closing
  bubble.onclick=()=>{panel.style.display='flex'};
  panel.querySelector('#closechat').onclick=()=>panel.style.display='none';

  // prvé otvorenie = pozdrav + návrhy
  bubble.addEventListener('click',()=>{
    if(!body.dataset.init){
      addMsg('Ahoj 👋 Ako ti môžem pomôcť?','bot');
      addSuggestions();
      body.dataset.init='1';
    }
  });

  // odoslanie textu
  function sendIfNotEmpty(){
    const v=(input.value||"").trim();
    if(!v)return;
    addMsg(v,'user');input.value='';
    const low=v.toLowerCase();
    if(RESPONSES[low]){
      setTimeout(()=>{
        addMsg(RESPONSES[low],'bot');
        if(/ppf/.test(low)) showPPFPricingFlow();
        if(/svetlomet/.test(low)) showHeadlightSteps();
      },150);
      return;
    }
  }
  send.onclick=sendIfNotEmpty;
  input.addEventListener('keydown',e=>{if(e.key==='Enter')sendIfNotEmpty();});
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
  font:700 26px var(--font);cursor:pointer;z-index:999999;
  border:2px solid var(--gold);
  box-shadow:0 8px 30px rgba(0,0,0,.45),0 0 0 3px rgba(212,175,55,.15);
  transition:transform .2s ease, box-shadow .2s ease;
}
#shopchat-bubble:hover{transform:translateY(-2px);box-shadow:0 10px 36px rgba(0,0,0,.55),0 0 0 5px rgba(212,175,55,.22);}
#shopchat-panel{
  position:fixed;right:20px;bottom:96px;width:380px;max-width:95vw;height:520px;
  background:var(--bg);border-radius:16px;box-shadow:0 24px 60px rgba(0,0,0,.55),0 0 0 1px var(--muted) inset;
  display:none;flex-direction:column;overflow:hidden;z-index:999998;font-family:var(--font);
}
#shopchat-header{padding:12px 14px;background:var(--bg2);color:var(--gold);display:flex;justify-content:space-between;align-items:center;font-weight:700;border-bottom:1px solid var(--muted);}
#shopchat-header button{background:none;border:none;color:var(--gold);font-size:18px;cursor:pointer;}
#shopchat-body{flex:1;padding:12px;overflow:auto;background:var(--bg);color:var(--text);}
#shopchat-input{display:flex;gap:8px;padding:10px;background:var(--bg2);border-top:1px solid var(--muted);}
#shopchat-input input{flex:1;padding:10px 12px;border:1px solid var(--muted);border-radius:10px;background:var(--bg);color:var(--text);}
#shopchat-input button{padding:10px 12px;border-radius:10px;border:none;background:var(--gold);color:#111;font-weight:700;}
.msg{max-width:80%;margin:6px 0;padding:10px 12px;border-radius:12px;font:14px/1.35 var(--font);white-space:pre-line;}
.msg.user{background:#19324a;color:#e9f2ff;margin-left:auto;}
.msg.bot{background:#111214;color:var(--text);}
.suggestions,.actions{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;}
.suggestions button,.actions button{border:1px solid var(--muted);background:var(--bg);color:var(--gold);padding:6px 10px;border-radius:999px;font:12px var(--font);cursor:pointer;}

/* PPF karty */
.ppf-cards{
  display:grid;
  gap:8px;
  margin:8px 0;
}
.ppf-card{
  border:1px solid var(--muted);
  background:var(--bg);
  border-radius:10px;
  padding:10px 12px;
}
.ppf-card .t{font-weight:700;color:var(--gold);margin-bottom:4px;}
.ppf-card .d{font-size:13px;opacity:.9;}
.ppf-card .p{margin-top:6px;font-weight:700;}
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





