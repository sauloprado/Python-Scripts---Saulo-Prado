"""
Banco local de icones visuais por servico/categoria.

Preferencia:
1. favicon real por dominio conhecido
2. favicon derivado da URL cadastrada
3. fallback com sigla e cor
"""

from __future__ import annotations

from urllib.parse import urlparse


ICON_CATALOG: list[dict[str, object]] = [
    {"key": "netflix", "aliases": ["netflix"], "domain": "netflix.com", "glyph": "N", "bg": "#111111", "fg": "#E50914"},
    {"key": "prime-video", "aliases": ["prime video", "amazon prime", "primevideo"], "domain": "primevideo.com", "glyph": "PV", "bg": "#0F171E", "fg": "#00A8E1"},
    {"key": "disney-plus", "aliases": ["disney", "disney plus", "disney+"], "domain": "disneyplus.com", "glyph": "D+", "bg": "#0C1445", "fg": "#7FDBFF"},
    {"key": "max", "aliases": ["max", "hbo max", "hbo"], "domain": "max.com", "glyph": "M", "bg": "#18003A", "fg": "#9B5CFF"},
    {"key": "youtube", "aliases": ["youtube"], "domain": "youtube.com", "glyph": "YT", "bg": "#FFFFFF", "fg": "#FF0000"},
    {"key": "spotify", "aliases": ["spotify"], "domain": "spotify.com", "glyph": "SP", "bg": "#191414", "fg": "#1DB954"},
    {"key": "globoplay", "aliases": ["globoplay"], "domain": "globoplay.globo.com", "glyph": "GP", "bg": "#FFFFFF", "fg": "#FF4F00"},
    {"key": "discord", "aliases": ["discord"], "domain": "discord.com", "glyph": "DS", "bg": "#5865F2", "fg": "#FFFFFF"},
    {"key": "gmail", "aliases": ["gmail", "google mail"], "domain": "mail.google.com", "glyph": "G", "bg": "#FFFFFF", "fg": "#EA4335"},
    {"key": "google", "aliases": ["google", "google workspace", "google classroom", "google drive"], "domain": "google.com", "glyph": "G", "bg": "#FFFFFF", "fg": "#4285F4"},
    {"key": "microsoft", "aliases": ["microsoft", "outlook", "office 365", "teams", "onedrive"], "domain": "microsoft.com", "glyph": "MS", "bg": "#F3F8FF", "fg": "#0078D4"},
    {"key": "notion", "aliases": ["notion"], "domain": "notion.so", "glyph": "N", "bg": "#FFFFFF", "fg": "#111111"},
    {"key": "figma", "aliases": ["figma"], "domain": "figma.com", "glyph": "F", "bg": "#2D2D2D", "fg": "#A259FF"},
    {"key": "github", "aliases": ["github"], "domain": "github.com", "glyph": "GH", "bg": "#111827", "fg": "#FFFFFF"},
    {"key": "gitlab", "aliases": ["gitlab"], "domain": "gitlab.com", "glyph": "GL", "bg": "#FFF3EA", "fg": "#FC6D26"},
    {"key": "bitbucket", "aliases": ["bitbucket"], "domain": "bitbucket.org", "glyph": "BB", "bg": "#EAF2FF", "fg": "#0052CC"},
    {"key": "slack", "aliases": ["slack"], "domain": "slack.com", "glyph": "SL", "bg": "#4A154B", "fg": "#FFFFFF"},
    {"key": "zoom", "aliases": ["zoom"], "domain": "zoom.us", "glyph": "ZM", "bg": "#EAF3FF", "fg": "#2D8CFF"},
    {"key": "trello", "aliases": ["trello"], "domain": "trello.com", "glyph": "TR", "bg": "#EAF3FF", "fg": "#0079BF"},
    {"key": "jira", "aliases": ["jira"], "domain": "atlassian.com", "glyph": "JR", "bg": "#EAF2FF", "fg": "#0052CC"},
    {"key": "canva", "aliases": ["canva"], "domain": "canva.com", "glyph": "CV", "bg": "#E8FBFF", "fg": "#00C4CC"},
    {"key": "udemy", "aliases": ["udemy"], "domain": "udemy.com", "glyph": "U", "bg": "#FFF0FA", "fg": "#A435F0"},
    {"key": "fgv", "aliases": ["fgv"], "domain": "fgv.br", "glyph": "FGV", "bg": "#EAF2FF", "fg": "#003A70"},
    {"key": "santander", "aliases": ["santander", "santander academy"], "domain": "santanderopenacademy.com", "glyph": "SA", "bg": "#FFF1EF", "fg": "#EC0000"},
    {"key": "voitto", "aliases": ["voitto", "grupo voitto"], "domain": "voitto.com.br", "glyph": "VT", "bg": "#FFF7EA", "fg": "#F39C12"},
    {"key": "xperiun", "aliases": ["xperiun", "xperium", "xeprium"], "domain": "app.xperiun.com", "glyph": "XP", "bg": "#EEF8F2", "fg": "#16A085"},
    {"key": "ninja-excel", "aliases": ["ninja do excel", "excel"], "domain": "ninjadoexcel.com.br", "glyph": "XL", "bg": "#EDF9F1", "fg": "#217346"},
    {"key": "aws", "aliases": ["aws", "amazon web services"], "domain": "aws.amazon.com", "glyph": "AWS", "bg": "#232F3E", "fg": "#FF9900"},
    {"key": "azure", "aliases": ["azure", "microsoft azure"], "domain": "azure.microsoft.com", "glyph": "AZ", "bg": "#EAF6FF", "fg": "#007FFF"},
    {"key": "gcp", "aliases": ["gcp", "google cloud", "google cloud platform"], "domain": "cloud.google.com", "glyph": "GCP", "bg": "#FFFFFF", "fg": "#4285F4"},
    {"key": "oracle-cloud", "aliases": ["oracle cloud", "oci", "oracle"], "domain": "oracle.com", "glyph": "OCI", "bg": "#FFF1EF", "fg": "#C74634"},
    {"key": "cloudflare", "aliases": ["cloudflare"], "domain": "cloudflare.com", "glyph": "CF", "bg": "#FFF6EE", "fg": "#F38020"},
    {"key": "digitalocean", "aliases": ["digitalocean"], "domain": "digitalocean.com", "glyph": "DO", "bg": "#EAF4FF", "fg": "#0080FF"},
    {"key": "vercel", "aliases": ["vercel"], "domain": "vercel.com", "glyph": "V", "bg": "#111111", "fg": "#FFFFFF"},
    {"key": "firebase", "aliases": ["firebase"], "domain": "firebase.google.com", "glyph": "FB", "bg": "#FFF8E8", "fg": "#FFCA28"},
    {"key": "docker", "aliases": ["docker"], "domain": "docker.com", "glyph": "DK", "bg": "#EAF6FF", "fg": "#2496ED"},
    {"key": "kubernetes", "aliases": ["kubernetes", "k8s"], "domain": "kubernetes.io", "glyph": "K8", "bg": "#EEF3FF", "fg": "#326CE5"},
    {"key": "linux", "aliases": ["linux", "ubuntu"], "domain": "ubuntu.com", "glyph": "LX", "bg": "#FFF3EB", "fg": "#E95420"},
    {"key": "openai", "aliases": ["openai", "chatgpt"], "domain": "openai.com", "glyph": "AI", "bg": "#F3F9F7", "fg": "#10A37F"},
    {"key": "anthropic", "aliases": ["anthropic", "claude"], "domain": "anthropic.com", "glyph": "CL", "bg": "#F8F1E8", "fg": "#8C6239"},
    {"key": "tv", "aliases": ["tv", "iptv", "televisao", "televisão"], "domain": "", "glyph": "TV", "bg": "#F2F4F8", "fg": "#2C3E50"},
    {"key": "cloud", "aliases": ["nuvem", "cloud"], "domain": "", "glyph": "CLD", "bg": "#EAF7FF", "fg": "#3498DB"},
    {"key": "school", "aliases": ["escola", "estudo", "curso", "learning"], "domain": "", "glyph": "EDU", "bg": "#EEF8FF", "fg": "#2980B9"},
    {"key": "tool", "aliases": ["ferramenta", "tool"], "domain": "", "glyph": "TL", "bg": "#EEF8F2", "fg": "#16A085"},
]


def _normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def _favicon_url(domain_or_url: str) -> str:
    return f"https://www.google.com/s2/favicons?sz=128&domain_url={domain_or_url}"


def _extract_domain(url: str) -> str:
    if not url:
        return ""
    raw = url.strip()
    if "://" not in raw:
        raw = f"https://{raw}"
    parsed = urlparse(raw)
    return parsed.netloc or parsed.path


def resolve_icon(service: str, category: str = "Geral", url: str = "") -> dict[str, str]:
    service_key = _normalize(service)
    category_key = _normalize(category)
    url_domain = _extract_domain(url)

    for item in ICON_CATALOG:
        for alias in item["aliases"]:
            alias_key = _normalize(str(alias))
            if alias_key and alias_key in service_key:
                domain = str(item.get("domain") or "")
                return {
                    "key": str(item["key"]),
                    "glyph": str(item["glyph"]),
                    "bg": str(item["bg"]),
                    "fg": str(item["fg"]),
                    "image_url": _favicon_url(domain) if domain else "",
                }

    if url_domain:
        return {
            "key": "url-domain",
            "glyph": "".join(part[0] for part in service.split()[:2]).upper()[:3] or "ID",
            "bg": "#EAF2F8",
            "fg": "#2C3E50",
            "image_url": _favicon_url(url_domain),
        }

    for item in ICON_CATALOG:
        for alias in item["aliases"]:
            alias_key = _normalize(str(alias))
            if alias_key and alias_key == category_key:
                domain = str(item.get("domain") or "")
                return {
                    "key": str(item["key"]),
                    "glyph": str(item["glyph"]),
                    "bg": str(item["bg"]),
                    "fg": str(item["fg"]),
                    "image_url": _favicon_url(domain) if domain else "",
                }

    letras = "".join(parte[0] for parte in service.split()[:2]).upper() or "ID"
    return {
        "key": "fallback",
        "glyph": letras[:3],
        "bg": "#EAF2F8",
        "fg": "#2C3E50",
        "image_url": "",
    }


def resolve_icon_by_key(icon_key: str) -> dict[str, str] | None:
    wanted = _normalize(icon_key)
    for item in ICON_CATALOG:
        if _normalize(str(item["key"])) == wanted:
            domain = str(item.get("domain") or "")
            return {
                "key": str(item["key"]),
                "glyph": str(item["glyph"]),
                "bg": str(item["bg"]),
                "fg": str(item["fg"]),
                "image_url": _favicon_url(domain) if domain else "",
            }
    return None


def list_icon_options() -> list[dict[str, str]]:
    options: list[dict[str, str]] = []
    for item in ICON_CATALOG:
        domain = str(item.get("domain") or "")
        options.append(
            {
                "key": str(item["key"]),
                "glyph": str(item["glyph"]),
                "bg": str(item["bg"]),
                "fg": str(item["fg"]),
                "image_url": _favicon_url(domain) if domain else "",
            }
        )
    return options
