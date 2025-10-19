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
    "strojné leštenie": "✨ Strojné leštenie laku ✨\nLeštenie nie je len o lesku – je to proces, pri ktorom navraciame laku hĺbku, jas a zrkadlový odraz. 🔍✨\nPoužívame excentrické aj rotačné leštičky, vďaka čomu vieme prispôsobiť postup presne podľa stavu laku.\n🔹 Jednokrokové leštenie – odstráni približne 60–70 % nedokonalostí, ideálne pri menej poškodenom laku.\n🔹 Viackrokové leštenie – dokáže dosiahnuť až 90–95 % korekcie, čím sa lak dostáva do takmer dokonalého stavu. 💎\nPred samotným leštením vždy auto dôkladne umyjeme, dekontaminujeme a pripravíme povrch. Každý detail riešime so zákazníkom osobne – vysvetlíme, čo sa dá spraviť, čo má zmysel a čo by bolo zbytočné. 🤝\n💰 Cena strojného leštenia začína od 200 €\nV cene jednokrokového leštenia je zahrnuté aj kompletné umytie a dekontaminácia laku.\n🚘 Výsledok? Auto, ktoré znovu žiari – ako nové",
    "cenník": "<a href='https://gavatep.eu/cennik' target='_blank' rel='noopener'>💰 Otvor stránku Cenník</a>",
}

SUGGESTIONS = ["Cenník","Renovácia svetlometov","Čistenie interiéru","Čistenie exteriéru","Keramická ochrana","Ochranná PPF fólia Quap","Strojné leštenie"]


# --- FRONTEND ---
WIDGET_JS = r"""
(function(){
  const RESPONSES = {
    "renovácia svetlometov": `""" + INTENTS["renovácia svetlometov"] + """`,
    "čistenie interiéru": `""" + INTENTS["čistenie interiéru"] + """`,
    "čistenie exteriéru": `""" + INTENTS["čistenie exteriéru"] + """`,
    "keramická ochrana": `""" + INTENTS["keramická ochrana"] + """`,
    "ochranná ppf fólia quap": `""" + INTENTS["ochranná ppf fólia quap"] + """`,
    "strojné leštenie": `""" + INTENTS["strojné leštenie"] + """`
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
    ["Cenník","Renovácia svetlometov","Čistenie interiéru","Čistenie exteriéru","Keramická ochrana","Ochranná PPF fólia Quap","Strojné leštenie"].forEach(t=>{
      const btn=document.createElement('button');btn.textContent=t;
      btn.onclick=()=>{
        addMsg(t,'user');
        const key=t.toLowerCase();
        if(key.includes('cenn')) {
          window.open('https://gavatep.eu/cennik','_blank','noopener');
          return;
        }
        if(RESPONSES[key]){
          setTimeout(()=>addMsg(RESPONSES[key],'bot'),200);
        }
      };
      b.appendChild(btn);
    });
    body.appendChild(b);
  }

  const audio = new Audio("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg");
  bubble.onclick=()=>{
    panel.style.display='flex';
    audio.currentTime = 0;
    audio.play().catch(()=>{});
  };
  panel.querySelector('#closechat').onclick=()=>panel.style.display='none';

  bubble.addEventListener('click', () => {
    if (!body.dataset.init) {
      addMsg('Ahoj ! Ako sa máš ? S čím ti môžem pomôcť ?','bot');
      addSuggestions();
      body.dataset.init = '1';
    }
  });

  (function setupTeaser(){
    try {
      if (sessionStorage.getItem('shopchat_teased')) return;
      bubble.classList.add('has-badge');
      const tip = document.createElement('div');
      tip.id = 'shopchat-teaser';
      tip.setAttribute('role','status');
      tip.setAttribute('aria-live','polite');
      tip.textContent = 'Máš správu – klikni';
      document.body.appendChild(tip);
      requestAnimationFrame(() => tip.classList.add('visible'));
      tip.addEventListener('click', () => {
        tip.remove();
        bubble.classList.remove('has-badge');
        bubble.click();
      });
      sessionStorage.setItem('shopchat_teased','1');
    } catch(_) {}
  })();

  function sendIfNotEmpty(){
    const v=(input.value||"").trim();
    if(!v)return;
    addMsg(v,'user');input.value='';
    const low=v.toLowerCase();
    if(RESPONSES[low]){
      setTimeout(()=>addMsg(RESPONSES[low],'bot'),150);
      return;
    }
  }
  send.onclick=sendIfNotEmpty;
  input.addEventListener('keydown',e=>{if(e.key==='Enter')sendIfNotEmpty();});
})();
"""

WIDGET_CSS = r"""(tvoj CSS tu ostáva celý tak, ako bol – nemenil sa)"""

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
    elif "lešten" in text or "lesteni" in text:
        reply = INTENTS["strojné leštenie"]
    else:
        reply = "Rozumiem. Môžem poslať info o službách alebo cenník."
    return JSONResponse({"reply": reply, "suggestions": SUGGESTIONS})






