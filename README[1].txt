# ShopChat Minimal (Shoptet)
1) Nasadiť na hosting (Render/Railway/Fly/VPS).
   - Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - Env var: `ALLOWED_ORIGIN=https://tvoja-shoptet-domena.sk`

2) Po nasadení dostaneš URL, napr. `https://tvoj-bot.onrender.com`.

3) V Shoptete vlož do pätičky (pred </body>):
<link rel="stylesheet" href="https://tvoj-bot.onrender.com/widget.css">
<script>window.SHOPCHAT_API="https://tvoj-bot.onrender.com/api/message";</script>
<script src="https://tvoj-bot.onrender.com/widget.js"></script>

4) Úprava textov: v `app.py` v slovníku INTENTS.