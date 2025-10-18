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

INTENTS = {
    "ochranná ppf fólia quap": "Keď chceš, aby tvoj lak vyzeral dlhodobo ako nový, je tu PPF fólia QUAP 🚘 Chráni pred škrabancami, kamienkami, hmyzom aj chemikáliami 🧤 Samoregeneračný povrch zahojí drobné škrabance teplom ☀️🔥 Lak zostáva dokonale lesklý, hladký a stále chránený 💧 To najlepšie, čo môžeš dať svojmu autu.",
    "cenník": "<a href='https://gavatep.eu/cennik' target='_blank' rel='noopener'>💰 Otvor stránku Cenník</a>",
}

SUGGESTIONS = ["CENNÍK", "SVETLOMETY", "INTERIÉR", "EXTERIÉR", "KERAMICKÁ", "PPF"]

WIDGET_JS = r"""
(function(){
  const RESPONSES = {
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

  const body=panel.querySelector('#shopchat-body');
  const input=panel.querySelector('input');
  const send=panel.querySelector('#shopchat-input button');

  function addMsg(txt,who){
    const d=document.createElement('div');
    d.className='msg '+who;
    if(who==='bot' && /<a\s/i.test(txt)) d.innerHTML=txt; else d.textContent=txt;
    body.appendChild(d);
    body.scrollTop=body.scrollHeight;
  }

  function addButtons(labels,onClick){
    const wrap=document.createElement('div');wrap.className='actions';
    labels.forEach(label=>{
      const b=document.createElement('button');
      b.textContent=label;
      b.onclick=()=>onClick(label,wrap);
      wrap.appendChild(b);
    });
    body.appendChild(wrap);
    body.scrollTop=body.scrollHeight;
  }

  // ---- Upravené rozloženie textu a otázka na kontakt ----
  function showPPFQuestion(){
    addMsg("Chceš spraviť cenník na svoje auto?",'bot');
    addButtons(["Áno","Nie"],(answer,wrap)=>{
      addMsg(answer,'user');
      wrap.remove();
      if(answer==="Áno"){
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

        addMsg("Chceš nás kontaktovať?", 'bot');
        addButtons(["Áno","Nie"], (ans2, wrap2)=>{
          addMsg(ans2,'user');
          wrap2.remove();
          if(ans2==="Áno"){
            window.location.href="https://www.gavatep.eu/kontakt/";
          } else {
            addMsg("Jasné. Keď budeš chcieť, klikni na Cenník alebo napíš model auta a pripravíme presnú cenu. 🙂",'bot');
          }
        });
      } else {
        addMsg("OK — ak chceš neskôr, ozvi sa, alebo napíš model auta a vyrobíme presnú kalkuláciu. 🙂",'bot');
      }
    });
  }
  // -------------------------------------------------------

  function addSuggestions(){
    const b=document.createElement('div');b.className='suggestions';
    ["Cenník","Ochranná PPF fólia Quap"].forEach(t=>{
      const btn=document.createElement('button');btn.textContent=t;
      btn.onclick=()=>{
        addMsg(t,'user');
        const key=t.toLowerCase();
        if(key.includes('cenn')) window.open('https://gavatep.eu/cennik','_blank','noopener');
        else if(RESPONSES[key]){
          setTimeout(()=>{
            addMsg(RESPONSES[key],'bot');
            if(key.includes('ppf')) showPPFQuestion();
          },200);
        }
      };
      b.appendChild(btn);
    });
    body.appendChild(b);
  }

  bubble.onclick=()=>panel.style.display='flex';
  panel.querySelector('#closechat').onclick=()=>panel.style.display='none';

  bubble.addEventListener('click',()=>{
    if(!body.dataset.init){
      addMsg('Ahoj 👋 Ako ti môžem pomôcť?','bot');
      addSuggestions();
      body.dataset.init='1';
    }
  });
})();
"""
WIDGET_CSS = r"""
#shopchat-bubble{position:fixed;right:20px;bottom:20px;width:60px;height:60px;border-radius:50%;background:#0f0f10;color:#d4af37;display:flex;align-items:center;justify-content:center;font-weight:700;cursor:pointer;z-index:9999;border:2px solid #d4af37}
#shopchat-panel{position:fixed;right:20px;bottom:90px;width:360px;height:500px;background:#0b0b0c;color:#fff;border-radius:12px;display:none;flex-direction:column;z-index:9998;font-family:Inter,system-ui}
.msg{white-space:pre-line;margin:6px 0;padding:8px 12px;border-radius:10px;max-width:80%}
.msg.user{background:#1d3557;margin-left:auto}
.msg.bot{background:#2a2a2a}
.actions button{border:1px solid #333;background:#0b0b0c;color:#d4af37;padding:6px 8px;border-radius:20px;margin-top:4px;cursor:pointer}
"""
app = FastAPI(title="GaVaTep Chat")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.get("/widget.js")
async def widget_js(): return PlainTextResponse(WIDGET_JS,media_type="application/javascript")
@app.get("/widget.css")
async def widget_css(): return PlainTextResponse(WIDGET_CSS,media_type="text/css")
@app.post("/api/message")
async def message(payload:dict):
    text=(payload.get("text") or "").lower()
    if "ppf" in text: reply=INTENTS["ochranná ppf fólia quap"]
    else: reply="Rozumiem. Môžem poslať info o službách alebo cenník."
    return JSONResponse({"reply":reply,"suggestions":SUGGESTIONS})
