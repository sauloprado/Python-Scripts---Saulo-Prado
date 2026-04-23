"""
Criado por: Saulo Prado
Versao: 2.00
Objetivo:
Pesquisar noticias de IA das ultimas 24 horas, montar um e-mail em texto e HTML
e salvar o resultado como arquivo .eml sem enviar nada automaticamente.
"""

from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from html import escape
import os
from pathlib import Path
import smtplib
import ssl
from urllib.error import URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


PASTA_BASE = Path(__file__).resolve().parent
LIMITE_NOTICIAS = 8
CONSULTA_GOOGLE_NEWS = (
    '(inteligencia artificial OR "artificial intelligence" OR ChatGPT OR OpenAI '
    'OR Anthropic OR Gemini OR Claude) when:1d'
)
URL_FEED = (
    "https://news.google.com/rss/search?"
    f"q={quote_plus(CONSULTA_GOOGLE_NEWS)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
)
ARQUIVO_SAIDA = "Noticias do Dia sobre IA - {data}.eml"
SMTP_SERVIDOR_PADRAO = "smtp.gmail.com"
SMTP_PORTA_PADRAO = 587


def buscar_feed_google_news(url_feed):
    # Faz a requisicao do feed RSS usando apenas bibliotecas padrao.
    requisicao = Request(
        url_feed,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0 Safari/537.36"
            )
        },
    )

    with urlopen(requisicao, timeout=20) as resposta:
        return resposta.read()


def limpar_titulo(titulo):
    # Remove espacos extras preservando o texto da manchete.
    return " ".join((titulo or "").split())


def extrair_fonte(item):
    fonte = item.find("source")
    return limpar_titulo(fonte.text) if fonte is not None and fonte.text else "Fonte nao informada"


def parsear_data_rss(texto_data):
    if not texto_data:
        return None

    try:
        return datetime.strptime(texto_data, "%a, %d %b %Y %H:%M:%S %Z")
    except ValueError:
        return None


def resumir_titulo(titulo):
    # Usa o proprio titulo como resumo curto para evitar inventar contexto.
    titulo_limpo = limpar_titulo(titulo)
    if len(titulo_limpo) <= 220:
        return titulo_limpo
    return titulo_limpo[:217].rstrip() + "..."


def coletar_noticias(xml_bytes, limite=LIMITE_NOTICIAS):
    raiz = ET.fromstring(xml_bytes)
    itens = []

    for item in raiz.findall("./channel/item"):
        titulo = limpar_titulo(item.findtext("title"))
        link = (item.findtext("link") or "").strip()
        publicado_em = parsear_data_rss(item.findtext("pubDate"))
        fonte = extrair_fonte(item)

        if not titulo or not link:
            continue

        itens.append(
            {
                "titulo": titulo,
                "link": link,
                "fonte": fonte,
                "publicado_em": publicado_em,
                "resumo": resumir_titulo(titulo),
            }
        )

        if len(itens) >= limite:
            break

    return itens


def formatar_horario(dt):
    if not dt:
        return "Horario indisponivel"
    return dt.strftime("%d/%m/%Y %H:%M UTC")


def criar_texto_email(noticias, data_referencia):
    linhas = [f"Noticias do Dia sobre IA - {data_referencia:%d/%m/%Y}", ""]

    for noticia in noticias:
        linhas.extend(
            [
                f"- {noticia['titulo']}",
                f"  Fonte: {noticia['fonte']}",
                f"  Publicado: {formatar_horario(noticia['publicado_em'])}",
                f"  Link: {noticia['link']}",
                "",
            ]
        )

    linhas.append("Este e-mail foi gerado automaticamente por um script Python.")
    return "\n".join(linhas)


def criar_card_html(noticia):
    publicado = formatar_horario(noticia["publicado_em"])
    return f"""
        <div style="padding:22px 24px;border:1px solid #e5e7eb;border-radius:14px;background:#ffffff;margin-bottom:16px;">
            <div style="font-size:12px;color:#6b7280;margin-bottom:8px;">
                {escape(noticia["fonte"])} | {escape(publicado)}
            </div>
            <h2 style="margin:0 0 10px;font-size:19px;line-height:1.35;color:#111827;">
                {escape(noticia["titulo"])}
            </h2>
            <p style="margin:0 0 14px;font-size:14px;line-height:1.7;color:#374151;">
                {escape(noticia["resumo"])}
            </p>
            <a href="{escape(noticia["link"], quote=True)}" target="_blank" style="display:inline-block;padding:10px 16px;background:#0f766e;color:#ffffff;text-decoration:none;border-radius:999px;font-size:13px;">
                Ler noticia
            </a>
        </div>
    """


def criar_html_email(noticias, data_referencia):
    cards = "".join(criar_card_html(noticia) for noticia in noticias)

    return f"""
    <html>
        <body style="margin:0;padding:24px;background:#f5f5f4;font-family:Arial,sans-serif;color:#1f2937;">
            <div style="max-width:760px;margin:0 auto;background:#fcfcfb;border-radius:22px;overflow:hidden;border:1px solid #e7e5e4;">
                <div style="padding:32px;background:linear-gradient(135deg,#0f172a,#0f766e);color:#ffffff;">
                    <div style="font-size:12px;letter-spacing:0.12em;text-transform:uppercase;opacity:0.82;">Resumo Diario</div>
                    <h1 style="margin:10px 0 8px;font-size:30px;line-height:1.2;">Noticias do Dia sobre IA</h1>
                    <p style="margin:0;font-size:15px;line-height:1.6;max-width:560px;opacity:0.92;">
                        Atualizacao automatica com noticias de inteligencia artificial publicadas nas ultimas 24 horas.
                    </p>
                    <p style="margin:14px 0 0;font-size:13px;opacity:0.82;">{data_referencia:%d/%m/%Y}</p>
                </div>
                <div style="padding:28px 24px 12px;">
                    {cards}
                </div>
                <div style="padding:0 24px 28px;font-size:12px;color:#6b7280;">
                    Este e-mail foi gerado automaticamente por um script Python. Nenhum envio foi realizado.
                </div>
            </div>
        </body>
    </html>
    """


def montar_email(remetente, destinatario, assunto, noticias, data_referencia):
    mensagem = EmailMessage()
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto
    mensagem["Date"] = format_datetime(datetime.now().astimezone())
    mensagem["Message-ID"] = make_msgid()

    mensagem.set_content(criar_texto_email(noticias, data_referencia))
    mensagem.add_alternative(criar_html_email(noticias, data_referencia), subtype="html")
    return mensagem


def salvar_rascunho_eml(mensagem, pasta_destino, data_referencia):
    nome_arquivo = ARQUIVO_SAIDA.format(data=data_referencia.strftime("%d_%m_%Y"))
    caminho_saida = pasta_destino / nome_arquivo
    caminho_saida.write_bytes(mensagem.as_bytes())
    return caminho_saida


def enviar_email_smtp(servidor_smtp, porta, usuario, senha, mensagem):
    contexto = ssl.create_default_context()

    with smtplib.SMTP(servidor_smtp, porta) as servidor:
        servidor.starttls(context=contexto)
        servidor.login(usuario, senha)
        servidor.send_message(mensagem)


def carregar_configuracao_env():
    remetente = os.getenv("EMAIL_REMETENTE", "saulosouzati@gmail.com")
    destinatario = os.getenv("EMAIL_DESTINATARIO", "saulosouza@outlook.com")
    servidor_smtp = os.getenv("SMTP_SERVIDOR", SMTP_SERVIDOR_PADRAO)
    porta_smtp = int(os.getenv("SMTP_PORTA", str(SMTP_PORTA_PADRAO)))
    senha = os.getenv("EMAIL_SENHA_APP", "").strip()

    if not senha:
        raise RuntimeError(
            "Defina a variavel de ambiente EMAIL_SENHA_APP com a senha de app do e-mail remetente."
        )

    return remetente, destinatario, servidor_smtp, porta_smtp, senha


def main():
    remetente, destinatario, servidor_smtp, porta_smtp, senha = carregar_configuracao_env()
    data_referencia = datetime.now()
    assunto = f"Noticias do Dia sobre IA | {data_referencia:%d/%m/%Y}"

    try:
        xml_feed = buscar_feed_google_news(URL_FEED)
    except URLError as erro:
        raise RuntimeError(
            "Nao foi possivel acessar o feed de noticias. "
            "Verifique sua conexao com a internet, firewall ou antivirus e tente novamente."
        ) from erro

    noticias = coletar_noticias(xml_feed)

    if not noticias:
        raise RuntimeError("Nenhuma noticia foi encontrada no feed consultado.")

    email = montar_email(
        remetente=remetente,
        destinatario=destinatario,
        assunto=assunto,
        noticias=noticias,
        data_referencia=data_referencia,
    )

    caminho_rascunho = salvar_rascunho_eml(email, PASTA_BASE, data_referencia)
    enviar_email_smtp(servidor_smtp, porta_smtp, remetente, senha, email)

    print("Rascunho criado com sucesso.")
    print(f"Arquivo salvo em: {caminho_rascunho}")
    print(f"E-mail enviado com sucesso para: {destinatario}")


if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print(f"Erro: {erro}")
