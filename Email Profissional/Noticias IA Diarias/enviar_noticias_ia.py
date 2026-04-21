"""
Criado por: Saulo Prado
Versao: 1.00
Objetivo:
Buscar noticias recentes sobre inteligencia artificial e
enviar um resumo diario por e-mail com HTML elegante.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import parsedate_to_datetime
from html import escape
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
import json
import smtplib
import ssl
import xml.etree.ElementTree as ET

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


try:
    TIMEZONE = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    # Fallback para ambientes Windows/Python sem base tzdata instalada.
    TIMEZONE = datetime.now().astimezone().tzinfo
BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
STATE_PATH = BASE_DIR / "estado_envio.json"
LOG_PATH = BASE_DIR / "execucao.log"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python Noticias IA Bot/1.0"

TOPICOS = [
    "ChatGPT",
    "Claude AI",
    "OpenAI",
    "Anthropic",
    "inteligencia artificial",
]


@dataclass
class Config:
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str | None
    email_from: str
    email_to: str
    email_subject_prefix: str
    max_noticias: int


@dataclass
class Noticia:
    titulo: str
    link: str
    fonte: str
    resumo: str
    publicada_em: datetime
    topico: str


def registrar_log(mensagem: str) -> None:
    momento = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as arquivo:
        arquivo.write(f"{momento} | {mensagem}\n")


def carregar_env(caminho: Path) -> dict[str, str]:
    # Carrega um arquivo .env simples sem depender de bibliotecas externas.
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo de configuracao nao encontrado: {caminho}. "
            f"Crie-o com base em {caminho.with_suffix('.example').name}."
        )

    valores: dict[str, str] = {}

    for linha in caminho.read_text(encoding="utf-8").splitlines():
        conteudo = linha.strip()
        if not conteudo or conteudo.startswith("#") or "=" not in conteudo:
            continue

        chave, valor = conteudo.split("=", 1)
        valores[chave.strip()] = valor.strip().strip('"').strip("'")

    return valores


def carregar_config(*, exigir_senha: bool) -> Config:
    dados = carregar_env(ENV_PATH)

    senha = dados.get("SMTP_PASSWORD")

    if exigir_senha and senha in {"", None, "COLOQUE_SUA_SENHA_DE_APP_AQUI"}:
        raise ValueError(
            "Preencha a variavel SMTP_PASSWORD no arquivo .env com a senha de app do Gmail."
        )

    return Config(
        smtp_host=dados["SMTP_HOST"],
        smtp_port=int(dados.get("SMTP_PORT", "587")),
        smtp_user=dados["SMTP_USER"],
        smtp_password=senha,
        email_from=dados["EMAIL_FROM"],
        email_to=dados["EMAIL_TO"],
        email_subject_prefix=dados.get("EMAIL_SUBJECT_PREFIX", "Noticias do Dia sobre IA"),
        max_noticias=int(dados.get("MAX_NOTICIAS", "10")),
    )


def gerar_urls_rss(topicos: Iterable[str]) -> list[tuple[str, str]]:
    # Usa a busca RSS do Google News por topico.
    urls = []
    for topico in topicos:
        query = quote_plus(topico)
        url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        urls.append((topico, url))
    return urls


def baixar_xml(url: str) -> str:
    requisicao = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(requisicao, timeout=20) as resposta:
        return resposta.read().decode("utf-8", errors="replace")


def normalizar_data(pub_date: str) -> datetime:
    data = parsedate_to_datetime(pub_date)
    if data.tzinfo is None:
        data = data.replace(tzinfo=TIMEZONE)
    return data.astimezone(TIMEZONE)


def limpar_texto(texto: str) -> str:
    return " ".join(texto.replace("\n", " ").replace("\r", " ").split())


def extrair_noticias() -> list[Noticia]:
    noticias: list[Noticia] = []
    links_vistos: set[str] = set()
    limite = datetime.now(TIMEZONE) - timedelta(days=1)

    for topico, url in gerar_urls_rss(TOPICOS):
        xml = baixar_xml(url)
        raiz = ET.fromstring(xml)

        for item in raiz.findall("./channel/item"):
            titulo = limpar_texto(item.findtext("title", default="Sem titulo"))
            link = limpar_texto(item.findtext("link", default=""))
            resumo = limpar_texto(item.findtext("description", default=""))
            pub_date = item.findtext("pubDate", default="")
            fonte = limpar_texto(item.findtext("source", default="Google News"))

            if not link or link in links_vistos or not pub_date:
                continue

            publicada_em = normalizar_data(pub_date)
            if publicada_em < limite:
                continue

            noticias.append(
                Noticia(
                    titulo=titulo,
                    link=link,
                    fonte=fonte,
                    resumo=resumo,
                    publicada_em=publicada_em,
                    topico=topico,
                )
            )
            links_vistos.add(link)

    noticias.sort(key=lambda noticia: noticia.publicada_em, reverse=True)
    return noticias


def carregar_estado() -> dict[str, object]:
    if not STATE_PATH.exists():
        return {"ultima_data_envio": "", "links_enviados": []}

    with STATE_PATH.open("r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_estado(noticias: list[Noticia]) -> None:
    estado = {
        "ultima_data_envio": datetime.now(TIMEZONE).strftime("%Y-%m-%d"),
        "links_enviados": [noticia.link for noticia in noticias],
    }

    with STATE_PATH.open("w", encoding="utf-8") as arquivo:
        json.dump(estado, arquivo, ensure_ascii=False, indent=2)


def filtrar_noticias_nao_enviadas(noticias: list[Noticia], limite: int) -> list[Noticia]:
    estado = carregar_estado()
    hoje = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    links_enviados = set(estado.get("links_enviados", []))

    if estado.get("ultima_data_envio") != hoje:
        links_enviados = set()

    filtradas = [noticia for noticia in noticias if noticia.link not in links_enviados]
    return filtradas[:limite]


def criar_html_email(noticias: list[Noticia]) -> str:
    hoje = datetime.now(TIMEZONE).strftime("%d/%m/%Y")

    cards = []
    for noticia in noticias:
        cards.append(
            f"""
            <div style="padding:22px 24px;border:1px solid #e5e7eb;border-radius:14px;background:#ffffff;margin-bottom:16px;">
                <div style="font-size:12px;color:#6b7280;margin-bottom:8px;">
                    {escape(noticia.topico)} | {escape(noticia.fonte)} | {noticia.publicada_em.strftime("%H:%M")}
                </div>
                <h2 style="margin:0 0 10px;font-size:19px;line-height:1.35;color:#111827;">
                    {escape(noticia.titulo)}
                </h2>
                <p style="margin:0 0 14px;font-size:14px;line-height:1.7;color:#374151;">
                    {escape(noticia.resumo)[:320]}
                </p>
                <a href="{escape(noticia.link)}" style="display:inline-block;padding:10px 16px;background:#0f766e;color:#ffffff;text-decoration:none;border-radius:999px;font-size:13px;">
                    Ler noticia
                </a>
            </div>
            """
        )

    return f"""
    <html>
        <body style="margin:0;padding:24px;background:#f5f5f4;font-family:Arial,sans-serif;color:#1f2937;">
            <div style="max-width:760px;margin:0 auto;background:#fcfcfb;border-radius:22px;overflow:hidden;border:1px solid #e7e5e4;">
                <div style="padding:32px;background:linear-gradient(135deg,#0f172a,#0f766e);color:#ffffff;">
                    <div style="font-size:12px;letter-spacing:0.12em;text-transform:uppercase;opacity:0.82;">Resumo Diario</div>
                    <h1 style="margin:10px 0 8px;font-size:30px;line-height:1.2;">Noticias do Dia sobre IA</h1>
                    <p style="margin:0;font-size:15px;line-height:1.6;max-width:560px;opacity:0.92;">
                        Atualizacao automatica com destaques sobre ChatGPT, Claude, OpenAI, Anthropic e o ecossistema de inteligencia artificial.
                    </p>
                    <p style="margin:14px 0 0;font-size:13px;opacity:0.82;">{hoje}</p>
                </div>
                <div style="padding:28px 24px 12px;">
                    {''.join(cards)}
                </div>
                <div style="padding:0 24px 28px;font-size:12px;color:#6b7280;">
                    Este e-mail foi gerado automaticamente por um script Python.
                </div>
            </div>
        </body>
    </html>
    """


def montar_email(config: Config, noticias: list[Noticia]) -> EmailMessage:
    hoje = datetime.now(TIMEZONE).strftime("%d/%m/%Y")
    assunto = f"{config.email_subject_prefix} | {hoje}"

    linhas = [
        f"Noticias do Dia sobre IA - {hoje}",
        "",
    ]

    for noticia in noticias:
        linhas.extend(
            [
                f"- {noticia.titulo}",
                f"  Fonte: {noticia.fonte}",
                f"  Link: {noticia.link}",
                "",
            ]
        )

    mensagem = EmailMessage()
    mensagem["From"] = config.email_from
    mensagem["To"] = config.email_to
    mensagem["Subject"] = assunto
    mensagem.set_content("\n".join(linhas))
    mensagem.add_alternative(criar_html_email(noticias), subtype="html")

    return mensagem


def enviar_email(config: Config, mensagem: EmailMessage) -> None:
    if not config.smtp_password:
        raise ValueError("SMTP_PASSWORD nao configurado.")

    contexto = ssl.create_default_context()

    with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=30) as servidor:
        servidor.starttls(context=contexto)
        servidor.login(config.smtp_user, config.smtp_password)
        servidor.send_message(mensagem)


def criar_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Busca noticias recentes sobre IA e envia um resumo por e-mail."
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Executa o envio imediatamente e registra logs mais claros para validacao manual.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Busca as noticias e monta o e-mail, mas nao envia.",
    )
    return parser.parse_args()


def main() -> None:
    args = criar_args()
    config = carregar_config(exigir_senha=not args.dry_run)

    try:
        registrar_log("Inicio da execucao.")
        noticias = extrair_noticias()

        if args.test:
            noticias_para_enviar = noticias[: config.max_noticias]
        else:
            noticias_para_enviar = filtrar_noticias_nao_enviadas(noticias, config.max_noticias)

        if not noticias_para_enviar:
            registrar_log("Nenhuma noticia nova encontrada para envio.")
            print("Nenhuma noticia nova encontrada para envio.")
            return

        mensagem = montar_email(config, noticias_para_enviar)

        if args.dry_run:
            registrar_log(f"Dry-run concluido com {len(noticias_para_enviar)} noticia(s).")
            print(f"Dry-run concluido com {len(noticias_para_enviar)} noticia(s).")
            return

        enviar_email(config, mensagem)

        if not args.test:
            salvar_estado(noticias_para_enviar)

        registrar_log(f"E-mail enviado com {len(noticias_para_enviar)} noticia(s).")
        print(f"E-mail enviado com {len(noticias_para_enviar)} noticia(s).")
    except Exception as erro:
        registrar_log(f"Erro: {erro}")
        raise


if __name__ == "__main__":
    main()
