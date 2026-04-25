"""
Criado por: Saulo Prado
Versao: 2.00
Objetivo:
Buscar noticias recentes sobre inteligencia artificial e gerar
um arquivo TXT local para leitura simples.
"""

from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


try:
    TIMEZONE = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    # Fallback para ambientes Windows/Python sem base tzdata instalada.
    TIMEZONE = datetime.now().astimezone().tzinfo


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
STATE_PATH = BASE_DIR / "estado_noticias.json"
LOG_PATH = BASE_DIR / "execucao.log"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python Noticias IA Local/2.0"

TOPICOS_PADRAO = [
    "ChatGPT",
    "Claude AI",
    "OpenAI",
    "Anthropic",
    "inteligencia artificial",
]


@dataclass
class Config:
    max_noticias: int
    dias_recentes: int
    pasta_saida: Path
    topicos: list[str]


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
    # O .env e opcional neste projeto local.
    if not caminho.exists():
        return {}

    valores: dict[str, str] = {}

    for linha in caminho.read_text(encoding="utf-8").splitlines():
        conteudo = linha.strip()
        if not conteudo or conteudo.startswith("#") or "=" not in conteudo:
            continue

        chave, valor = conteudo.split("=", 1)
        valores[chave.strip()] = valor.strip().strip('"').strip("'")

    return valores


def ler_inteiro(valor: str | None, padrao: int) -> int:
    if not valor:
        return padrao

    try:
        return int(valor)
    except ValueError:
        return padrao


def resolver_caminho_local(caminho: str | None, padrao: str) -> Path:
    valor = caminho or padrao
    destino = Path(valor)

    if not destino.is_absolute():
        destino = BASE_DIR / destino

    return destino


def carregar_config(args: argparse.Namespace) -> Config:
    dados = carregar_env(ENV_PATH)

    max_noticias = args.max_noticias or ler_inteiro(dados.get("MAX_NOTICIAS"), 10)
    dias_recentes = args.dias or ler_inteiro(dados.get("DIAS_RECENTES"), 1)
    pasta_saida = resolver_caminho_local(dados.get("PASTA_SAIDA"), "leituras")

    topicos_env = dados.get("TOPICOS", "")
    topicos = [topico.strip() for topico in topicos_env.split(",") if topico.strip()]

    return Config(
        max_noticias=max(1, max_noticias),
        dias_recentes=max(1, dias_recentes),
        pasta_saida=pasta_saida,
        topicos=topicos or TOPICOS_PADRAO,
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


def limpar_html(texto: str) -> str:
    sem_tags = re.sub(r"<[^>]+>", " ", unescape(texto))
    return limpar_texto(sem_tags)


def limitar_texto(texto: str, limite: int = 520) -> str:
    if len(texto) <= limite:
        return texto

    return f"{texto[: limite - 3].rstrip()}..."


def extrair_noticias(config: Config) -> list[Noticia]:
    noticias: list[Noticia] = []
    links_vistos: set[str] = set()
    limite_data = datetime.now(TIMEZONE) - timedelta(days=config.dias_recentes)

    for topico, url in gerar_urls_rss(config.topicos):
        try:
            xml = baixar_xml(url)
            raiz = ET.fromstring(xml)
        except Exception as erro:
            registrar_log(f"Falha ao consultar topico '{topico}': {erro}")
            continue

        for item in raiz.findall("./channel/item"):
            titulo = limpar_html(item.findtext("title", default="Sem titulo"))
            link = limpar_texto(item.findtext("link", default=""))
            resumo = limpar_html(item.findtext("description", default=""))
            pub_date = item.findtext("pubDate", default="")
            fonte = limpar_html(item.findtext("source", default="Google News"))

            if not link or link in links_vistos or not pub_date:
                continue

            publicada_em = normalizar_data(pub_date)
            if publicada_em < limite_data:
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
    return noticias[: config.max_noticias]


def criar_texto_noticias(noticias: list[Noticia], config: Config) -> str:
    agora = datetime.now(TIMEZONE)
    linhas = [
        "Noticias IA Local",
        f"Gerado em: {agora:%d/%m/%Y %H:%M}",
        f"Periodo consultado: ultimos {config.dias_recentes} dia(s)",
        f"Total encontrado: {len(noticias)} noticia(s)",
        "",
        "=" * 72,
        "",
    ]

    for indice, noticia in enumerate(noticias, start=1):
        resumo = limitar_texto(noticia.resumo or "Resumo nao informado.")
        publicada = noticia.publicada_em.strftime("%d/%m/%Y %H:%M")

        linhas.extend(
            [
                f"{indice}. {noticia.titulo}",
                f"Fonte: {noticia.fonte}",
                f"Topico: {noticia.topico}",
                f"Publicado em: {publicada}",
                f"Resumo: {resumo}",
                f"Link: {noticia.link}",
                "",
                "-" * 72,
                "",
            ]
        )

    return "\n".join(linhas).rstrip() + "\n"


def resolver_arquivo_saida(args: argparse.Namespace, config: Config) -> Path:
    if args.saida:
        caminho = Path(args.saida)
        if not caminho.is_absolute():
            caminho = BASE_DIR / caminho

        if caminho.suffix.lower() != ".txt":
            caminho = caminho / nome_arquivo_padrao()

        return caminho

    return config.pasta_saida / nome_arquivo_padrao()


def nome_arquivo_padrao() -> str:
    hoje = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    return f"noticias_ia_{hoje}.txt"


def salvar_txt(texto: str, caminho: Path) -> Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8-sig")
    return caminho


def salvar_estado(noticias: list[Noticia], caminho_saida: Path) -> None:
    estado = {
        "ultima_geracao": datetime.now(TIMEZONE).isoformat(),
        "arquivo_saida": str(caminho_saida),
        "links_gerados": [noticia.link for noticia in noticias],
    }

    with STATE_PATH.open("w", encoding="utf-8") as arquivo:
        json.dump(estado, arquivo, ensure_ascii=False, indent=2)


def criar_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Busca noticias recentes sobre IA e salva um resumo em TXT local."
    )
    parser.add_argument(
        "--max-noticias",
        type=int,
        help="Quantidade maxima de noticias no arquivo final.",
    )
    parser.add_argument(
        "--dias",
        type=int,
        help="Quantidade de dias recentes para considerar na busca.",
    )
    parser.add_argument(
        "--saida",
        help="Arquivo TXT ou pasta de saida. Padrao: leituras/noticias_ia_YYYY-MM-DD.txt.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra o texto no terminal sem salvar arquivo.",
    )
    return parser.parse_args()


def main() -> None:
    args = criar_args()
    config = carregar_config(args)

    try:
        registrar_log("Inicio da geracao local.")
        noticias = extrair_noticias(config)

        if not noticias:
            registrar_log("Nenhuma noticia recente encontrada.")
            print("Nenhuma noticia recente encontrada.")
            return

        texto = criar_texto_noticias(noticias, config)

        if args.dry_run:
            registrar_log(f"Dry-run concluido com {len(noticias)} noticia(s).")
            print(texto)
            return

        caminho_saida = resolver_arquivo_saida(args, config)
        salvar_txt(texto, caminho_saida)
        salvar_estado(noticias, caminho_saida)

        registrar_log(f"Arquivo TXT gerado com {len(noticias)} noticia(s): {caminho_saida}")
        print(f"Arquivo TXT gerado: {caminho_saida}")
    except Exception as erro:
        registrar_log(f"Erro: {erro}")
        raise


if __name__ == "__main__":
    main()
