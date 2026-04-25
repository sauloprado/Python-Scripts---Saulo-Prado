from __future__ import annotations

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

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # pragma: no cover
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception

from db import READINGS_DIR


try:
    TIMEZONE = ZoneInfo("America/Sao_Paulo")
except ZoneInfoNotFoundError:
    TIMEZONE = datetime.now().astimezone().tzinfo


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Noticias IA Web/1.0"
DEFAULT_TOPICS = [
    "ChatGPT",
    "Claude AI",
    "OpenAI",
    "Anthropic",
    "inteligencia artificial",
]


@dataclass
class NewsOptions:
    max_articles: int = 12
    days_back: int = 1
    topics: list[str] | None = None

    def normalized_topics(self) -> list[str]:
        topics = [topic.strip() for topic in (self.topics or []) if topic.strip()]
        return topics or DEFAULT_TOPICS


def clean_text(text: str) -> str:
    return " ".join(text.replace("\n", " ").replace("\r", " ").split())


def strip_html(text: str) -> str:
    text = unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return clean_text(text)


def extract_image_from_html(text: str) -> str:
    match = re.search(r"<img[^>]+src=[\"']([^\"']+)[\"']", text or "", flags=re.I)
    return clean_text(match.group(1)) if match else ""


def limit_text(text: str, limit: int = 540) -> str:
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def normalize_date(pub_date: str) -> datetime:
    date = parsedate_to_datetime(pub_date)
    if date.tzinfo is None:
        date = date.replace(tzinfo=TIMEZONE)
    return date.astimezone(TIMEZONE)


def rss_urls(topics: Iterable[str]) -> list[tuple[str, str]]:
    urls = []
    for topic in topics:
        query = quote_plus(topic)
        url = f"https://news.google.com/rss/search?q={query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        urls.append((topic, url))
    return urls


def fetch_xml(url: str) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def media_image(item: ET.Element, raw_description: str) -> str:
    for element in item.iter():
        tag = element.tag.lower()
        if tag.endswith("}content") or tag.endswith("}thumbnail") or tag.endswith("enclosure"):
            url = element.attrib.get("url", "")
            media_type = element.attrib.get("type", "")
            if url and ("image" in media_type or tag.endswith("}thumbnail")):
                return clean_text(url)

    return extract_image_from_html(raw_description)


def fetch_news(options: NewsOptions) -> list[dict]:
    articles: list[dict] = []
    seen_urls: set[str] = set()
    topics = options.normalized_topics()
    cutoff = datetime.now(TIMEZONE) - timedelta(days=options.days_back)

    for topic, url in rss_urls(topics):
        xml = fetch_xml(url)
        root = ET.fromstring(xml)

        for item in root.findall("./channel/item"):
            title = strip_html(item.findtext("title", default="Sem titulo"))
            article_url = clean_text(item.findtext("link", default=""))
            raw_summary = item.findtext("description", default="")
            summary = limit_text(strip_html(raw_summary) or "Resumo nao informado.")
            pub_date = item.findtext("pubDate", default="")
            source = strip_html(item.findtext("source", default="Google News"))

            if not article_url or article_url in seen_urls or not pub_date:
                continue

            published = normalize_date(pub_date)
            if published < cutoff:
                continue

            articles.append(
                {
                    "title": title,
                    "url": article_url,
                    "source": source,
                    "summary": summary,
                    "image_url": media_image(item, raw_summary),
                    "topic": topic,
                    "published_at": published.strftime("%Y-%m-%dT%H:%M:%S"),
                }
            )
            seen_urls.add(article_url)

    articles.sort(key=lambda article: article["published_at"], reverse=True)
    return articles[: options.max_articles]


def build_reading_text(articles: list[dict], options: NewsOptions) -> str:
    now = datetime.now(TIMEZONE)
    topics = ", ".join(options.normalized_topics())
    lines = [
        "Noticias IA Web",
        f"Gerado em: {now:%d/%m/%Y %H:%M}",
        f"Periodo: ultimos {options.days_back} dia(s)",
        f"Topicos: {topics}",
        f"Total: {len(articles)} noticia(s)",
        "",
        "=" * 78,
        "",
    ]

    for index, article in enumerate(articles, start=1):
        published = datetime.strptime(article["published_at"], "%Y-%m-%dT%H:%M:%S")
        lines.extend(
            [
                f"{index}. {article['title']}",
                f"Fonte: {article['source']}",
                f"Topico: {article['topic']}",
                f"Publicado em: {published:%d/%m/%Y %H:%M}",
                f"Resumo: {article['summary']}",
                f"Link: {article['url']}",
                "",
                "-" * 78,
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def save_reading_file(articles: list[dict], options: NewsOptions) -> Path:
    READINGS_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"noticias_ia_{datetime.now(TIMEZONE):%Y-%m-%d_%H%M%S}.txt"
    path = READINGS_DIR / filename
    path.write_text(build_reading_text(articles, options), encoding="utf-8-sig")
    return path
