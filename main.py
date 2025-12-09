import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
from telegram import Bot

TELEGRAM_TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"
CHECK_INTERVAL_MINUTES = 2

bot = Bot(token=TELEGRAM_TOKEN)
ultimo_conteudo = None

def montar_url_trt2():
    hoje = datetime.now().strftime("%d-%m-%Y")
    base = "https://in.gov.br/leiturajornal"
    params = (
        f"?data={hoje}"
        "&secao=do2"
        "&org=Poder%20Judici%C3%A1rio"
        "&org_sub=Tribunal%20Regional%20do%20Trabalho%20da%202%C2%AA%20Regi%C3%A3o"
    )
    return base + params

def buscar_conteudo():
    url = montar_url_trt2()
    r = requests.get(url, timeout=30)
    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    artigos = soup.find_all("div", class_="texto-dou")
    conteudo = "\n\n".join([a.get_text(strip=True) for a in artigos])

    return conteudo if conteudo.strip() else None

def monitorar():
    global ultimo_conteudo
    bot.send_message(chat_id=CHAT_ID, text="🔎 Bot iniciado no Render!")

    while True:
        conteudo = buscar_conteudo()

        if conteudo and conteudo != ultimo_conteudo:
            bot.send_message(
                chat_id=CHAT_ID,
                text="📢 *Atualização encontrada no DOU para o TRT-2!*\n\n" +
                     conteudo[:3900],
                parse_mode="Markdown"
            )
            ultimo_conteudo = conteudo

        time.sleep(CHECK_INTERVAL_MINUTES * 60)

monitorar()
