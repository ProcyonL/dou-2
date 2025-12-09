import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Bot

# ------------------------------------------------------------
# VARIÁVEIS DE AMBIENTE (Render → Environment → Add Variable)
# ------------------------------------------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL_MINUTES = int(os.getenv("CHECK_INTERVAL_MINUTES", 2))

bot = Bot(token=TELEGRAM_TOKEN)


# ------------------------------------------------------------
# MONTA A URL DO DOU (TRT-2)
# ------------------------------------------------------------
def montar_url_trt2():
    return "https://www.in.gov.br/leiturajornal?secao=do3&orgao=TRIBUNAL%20REGIONAL%20DO%20TRABALHO%20DA%202%C2%AA%20REGI%C3%83O"


# ------------------------------------------------------------
# BUSCA O CONTEÚDO DO DOU
# ------------------------------------------------------------
def buscar_conteudo():
    url = montar_url_trt2()

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        )
    }

    try:
        r = requests.get(url, headers=headers, timeout=30)
    except Exception:
        return None

    if r.status_code != 200:
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    artigos = soup.find_all("div", class_="texto-dou")

    conteudo = "\n\n".join(a.get_text(strip=True) for a in artigos)
    return conteudo if conteudo.strip() else None


# ------------------------------------------------------------
# LOOP PRINCIPAL QUE VERIFICA E NOTIFICA
# ------------------------------------------------------------
def main():
    ultimo_conteudo = None
    bot.send_message(chat_id=CHAT_ID, text="🤖 Bot iniciado com sucesso no Render!")

    while True:
        print("⏳ Verificando DOU...")

        conteudo = buscar_conteudo()

        if not conteudo:
            print("⚠️ Nada encontrado.")
        else:
            if conteudo != ultimo_conteudo:
                bot.send_message(chat_id=CHAT_ID, text="📄 *Novo conteúdo encontrado no DOU!*", parse_mode="Markdown")
                bot.send_message(chat_id=CHAT_ID, text=conteudo[:3900])
                ultimo_conteudo = conteudo
                print("📨 Conteúdo enviado!")

        time.sleep(CHECK_INTERVAL_MINUTES * 60)


# ------------------------------------------------------------
# INÍCIO
# ------------------------------------------------------------
if __name__ == "__main__":
    if TELEGRAM_TOKEN is None or CHAT_ID is None:
        print("❌ ERRO: Variáveis TELEGRAM_TOKEN e CHAT_ID não configuradas no Render.")
    else:
        main()

