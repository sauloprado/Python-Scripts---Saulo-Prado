"""
Criado por: Saulo Prado
Versao: 1.00
Objetivo:
Criar um cofre local de senhas com interface web,
senha mestra e armazenamento criptografado.
"""

from __future__ import annotations

from base64 import urlsafe_b64encode
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import pbkdf2_hmac
from html.parser import HTMLParser
from pathlib import Path
from secrets import choice, token_hex, token_urlsafe
from string import ascii_letters, digits
from typing import Any
import json
import re

from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, jsonify, make_response, render_template, request
from icon_bank import list_icon_options, resolve_icon, resolve_icon_by_key


APP_DIR = Path(__file__).resolve().parent
VAULT_PATH = APP_DIR / "vault.enc"
LOG_PATH = APP_DIR / "cofre.log"
SESSION_COOKIE = "cofre_session"
PBKDF2_ITERATIONS = 390000
SESSION_STORE: dict[str, bytes] = {}
BASE_CATEGORIES = [
    "Geral",
    "Estudo",
    "Escolas",
    "Plataforma",
    "Ferramenta",
    "Nuvem",
    "TV",
    "Streaming",
    "Trabalho",
    "Email",
    "Financeiro",
    "Redes Sociais",
    "Desenvolvimento",
    "IA",
]

app = Flask(__name__, template_folder="templates", static_folder="static")


@dataclass
class VaultMetadata:
    salt: str
    iterations: int
    encrypted_data: str


class TextoDoHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.partes: list[str] = []

    def handle_data(self, data: str) -> None:
        texto = data.strip()
        if texto:
            self.partes.append(texto)

    def texto(self) -> str:
        return "\n".join(self.partes)


def registrar_log(mensagem: str) -> None:
    momento = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_PATH.open("a", encoding="utf-8") as arquivo:
        arquivo.write(f"{momento} | {mensagem}\n")


def resposta_json(payload: dict[str, Any], status: int = 200):
    response = make_response(jsonify(payload), status)
    response.headers["Cache-Control"] = "no-store"
    return response


def gerar_chave(master_password: str, salt: bytes, iterations: int) -> bytes:
    material = pbkdf2_hmac(
        "sha256",
        master_password.encode("utf-8"),
        salt,
        iterations,
        dklen=32,
    )
    return urlsafe_b64encode(material)


def estrutura_vazia() -> dict[str, Any]:
    return {
        "entries": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def cofre_existe() -> bool:
    return VAULT_PATH.exists()


def carregar_metadata() -> VaultMetadata:
    if not cofre_existe():
        raise FileNotFoundError("O cofre ainda nao foi inicializado.")

    raw = json.loads(VAULT_PATH.read_text(encoding="utf-8"))
    return VaultMetadata(
        salt=raw["salt"],
        iterations=int(raw["iterations"]),
        encrypted_data=raw["encrypted_data"],
    )


def descriptografar_cofre(chave: bytes) -> dict[str, Any]:
    metadata = carregar_metadata()
    fernet = Fernet(chave)

    try:
        conteudo = fernet.decrypt(metadata.encrypted_data.encode("utf-8"))
    except InvalidToken as erro:
        raise ValueError("Senha mestra invalida.") from erro

    return json.loads(conteudo.decode("utf-8"))


def salvar_cofre(chave: bytes, dados: dict[str, Any], salt_b64: str, iterations: int) -> None:
    dados["updated_at"] = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(dados, ensure_ascii=False, indent=2).encode("utf-8")
    encrypted = Fernet(chave).encrypt(payload).decode("utf-8")

    VAULT_PATH.write_text(
        json.dumps(
            {
                "salt": salt_b64,
                "iterations": iterations,
                "encrypted_data": encrypted,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def criar_sessao(chave: bytes):
    session_id = token_urlsafe(32)
    SESSION_STORE[session_id] = chave
    return session_id


def obter_sessao() -> tuple[str | None, bytes | None]:
    session_id = request.cookies.get(SESSION_COOKIE)
    if not session_id:
        return None, None
    return session_id, SESSION_STORE.get(session_id)


def limpar_sessao(response):
    session_id, _ = obter_sessao()
    if session_id:
        SESSION_STORE.pop(session_id, None)
    response.delete_cookie(SESSION_COOKIE)
    return response


def autenticacao_obrigatoria() -> tuple[str | None, bytes | None]:
    session_id, chave = obter_sessao()
    if not session_id or not chave:
        return None, None
    return session_id, chave


def gerar_senha_forte(tamanho: int = 20) -> str:
    especiais = "!@#$%&*()-_=+?"
    universo = ascii_letters + digits + especiais
    return "".join(choice(universo) for _ in range(tamanho))


def normalizar_entry(entry: dict[str, Any]) -> dict[str, Any]:
    icon_override = (entry.get("icon_override") or "").strip()
    icon = resolve_icon_by_key(icon_override) if icon_override else None
    if not icon:
        icon = resolve_icon(entry["service"], entry.get("category", "Geral"), entry.get("url", ""))
    return {
        "id": entry["id"],
        "category": entry.get("category", "Geral"),
        "service": entry["service"],
        "username": entry["username"],
        "password": entry["password"],
        "url": entry.get("url", ""),
        "notes": entry.get("notes", ""),
        "icon_override": icon_override,
        "created_at": entry["created_at"],
        "updated_at": entry["updated_at"],
        "icon": icon,
    }


def chave_duplicidade(entry: dict[str, Any]) -> str:
    category = (entry.get("category") or "Geral").strip().lower()
    service = (entry.get("service") or "").strip().lower()
    username = (entry.get("username") or "").strip().lower()
    url = (entry.get("url") or "").strip().lower()
    return "||".join([category, service, username, url])


def validar_entry_payload(dados_request: dict[str, Any]) -> tuple[str, str, str, str, str, str, str]:
    category = (dados_request.get("category") or "Geral").strip() or "Geral"
    service = (dados_request.get("service") or "").strip()
    username = (dados_request.get("username") or "").strip()
    password = (dados_request.get("password") or "").strip()
    url = (dados_request.get("url") or "").strip()
    notes = (dados_request.get("notes") or "").strip()
    icon_override = (dados_request.get("icon_override") or "").strip()

    if not service or not username or not password:
        raise ValueError("Servico, usuario e senha sao obrigatorios.")

    return category, service, username, password, url, notes, icon_override


def chave_duplicidade(entry: dict[str, Any]) -> str:
    category = (entry.get("category") or "Geral").strip().lower()
    service = (entry.get("service") or "").strip().lower()
    username = (entry.get("username") or "").strip().lower()
    url = (entry.get("url") or "").strip().lower()
    return "||".join([category, service, username, url])


def duplicate_groups(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grupos: dict[str, list[dict[str, Any]]] = {}
    for entry in entries:
        grupos.setdefault(chave_duplicidade(entry), []).append(entry)

    resultado: list[dict[str, Any]] = []
    for chave, itens in grupos.items():
        if len(itens) > 1:
            ordenados = sorted(itens, key=lambda item: item.get("created_at", ""))
            resultado.append(
                {
                    "key": chave,
                    "count": len(ordenados),
                    "entries": [normalizar_entry(item) for item in ordenados],
                }
            )
    return sorted(resultado, key=lambda grupo: grupo["count"], reverse=True)


def collect_categories(entries: list[dict[str, Any]]) -> list[str]:
    categorias = {categoria for categoria in BASE_CATEGORIES}
    for entry in entries:
        categoria = (entry.get("category") or "").strip()
        if categoria:
            categorias.add(categoria)
    return sorted(categorias, key=lambda item: item.lower())


def normalizar_nome_campo(nome: str) -> str:
    nome = nome.replace("\xa0", " ").strip().lower()
    mapa = {
        "categoria": "category",
        "nome": "service",
        "tipo": "category",
        "grupo": "category",
        "assunto": "category",
        "servico": "service",
        "serviço": "service",
        "plataforma": "service",
        "site": "service",
        "ferramenta": "service",
        "usuario": "username",
        "usuário": "username",
        "login": "username",
        "email": "username",
        "senha": "password",
        "password": "password",
        "url": "url",
        "link": "url",
        "observacoes": "notes",
        "observações": "notes",
        "obs": "notes",
        "notas": "notes",
    }
    return mapa.get(nome, nome)


def extrair_texto_colado(raw_text: str) -> str:
    raw_text = raw_text.replace("\xa0", " ")
    if "<" in raw_text and ">" in raw_text:
        parser = TextoDoHtmlParser()
        parser.feed(raw_text)
        texto = parser.texto()
        if texto.strip():
            return texto
    return raw_text


def parse_bulk_entries(raw_text: str, default_category: str = "Importados") -> list[dict[str, str]]:
    texto = extrair_texto_colado(raw_text)
    linhas = [linha.strip() for linha in texto.replace("\r", "\n").split("\n")]

    entries: list[dict[str, str]] = []
    current_category = default_category or "Importados"
    atual: dict[str, str] = {}
    markdown_headers: list[str] | None = None

    def finalizar_atual() -> None:
        nonlocal atual
        if atual.get("service") and atual.get("username") and atual.get("password"):
            atual.setdefault("category", current_category)
            entries.append(
                {
                    "category": atual.get("category", current_category),
                    "service": atual["service"],
                    "username": atual["username"],
                    "password": atual["password"],
                    "url": atual.get("url", ""),
                    "notes": atual.get("notes", ""),
                }
            )
        atual = {}

    for linha in linhas:
        linha = linha.replace("\xa0", " ").strip()
        if not linha:
            finalizar_atual()
            markdown_headers = None
            continue

        if linha.lower().startswith("categoria "):
            finalizar_atual()
            markdown_headers = None
            current_category = linha[10:].strip() or current_category
            continue

        if linha.startswith("###"):
            finalizar_atual()
            markdown_headers = None
            current_category = linha.removeprefix("###").strip() or current_category
            continue

        if linha.startswith("|") and linha.endswith("|"):
            colunas = [coluna.strip() for coluna in linha.strip("|").split("|")]

            if all(set(coluna) <= {"-", " "} for coluna in colunas):
                continue

            if markdown_headers is None:
                markdown_headers = [normalizar_nome_campo(coluna) for coluna in colunas]
                continue

            registro = dict(zip(markdown_headers, [coluna.replace("\xa0", " ").strip() for coluna in colunas]))
            service = (
                registro.get("service")
                or registro.get("escola")
                or registro.get("nome")
                or registro.get("plataforma")
                or registro.get("ferramenta")
                or ""
            ).strip()
            username = (registro.get("username") or "").strip()
            password = (registro.get("password") or "").strip()
            url = (registro.get("url") or "").strip()
            notes = (registro.get("notes") or "").strip()

            if password.lower().startswith("senha:"):
                password = password.split(":", 1)[1].strip()

            if service and username and password:
                entries.append(
                    {
                        "category": current_category,
                        "service": service,
                        "username": username,
                        "password": password,
                        "url": url,
                        "notes": notes,
                    }
                )
            continue

        if re.fullmatch(r"\[(.+)\]", linha):
            finalizar_atual()
            markdown_headers = None
            current_category = linha[1:-1].strip() or current_category
            continue

        if ":" not in linha and not atual:
            markdown_headers = None
            current_category = linha.strip()
            continue

        if ":" not in linha:
            atual["notes"] = f"{atual.get('notes', '')}\n{linha}".strip()
            continue

        chave_bruta, valor_bruto = linha.split(":", 1)
        chave = normalizar_nome_campo(chave_bruta)
        valor = valor_bruto.strip()

        if chave == "category":
            if atual:
                finalizar_atual()
            current_category = valor or current_category
            continue

        if chave == "service" and atual.get("service") and atual.get("username") and atual.get("password"):
            finalizar_atual()

        if chave in {"service", "username", "password", "url"}:
            atual[chave] = valor
        elif chave == "notes":
            atual["notes"] = f"{atual.get('notes', '')}\n{valor}".strip()
        else:
            atual["notes"] = f"{atual.get('notes', '')}\n{linha}".strip()

    finalizar_atual()
    return entries


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/status")
def status():
    _, chave = obter_sessao()
    return resposta_json(
        {
            "vault_exists": cofre_existe(),
            "unlocked": bool(chave),
        }
    )


@app.get("/api/icons")
def icons():
    return resposta_json({"icons": list_icon_options()})


@app.get("/api/categories")
def categories():
    _, chave = obter_sessao()
    if not chave:
        return resposta_json({"categories": BASE_CATEGORIES})

    dados = descriptografar_cofre(chave)
    return resposta_json({"categories": collect_categories(dados["entries"])})


@app.post("/api/setup")
def setup_vault():
    if cofre_existe():
        return resposta_json({"error": "O cofre ja foi criado."}, 409)

    dados = request.get_json(silent=True) or {}
    master_password = (dados.get("master_password") or "").strip()
    confirmation = (dados.get("confirmation") or "").strip()

    if len(master_password) < 12:
        return resposta_json({"error": "Use uma senha mestra com pelo menos 12 caracteres."}, 400)

    if master_password != confirmation:
        return resposta_json({"error": "A confirmacao da senha mestra nao confere."}, 400)

    salt = token_hex(16).encode("utf-8")
    chave = gerar_chave(master_password, salt, PBKDF2_ITERATIONS)
    dados_iniciais = estrutura_vazia()
    salvar_cofre(chave, dados_iniciais, salt.decode("utf-8"), PBKDF2_ITERATIONS)

    session_id = criar_sessao(chave)
    registrar_log("Cofre criado com sucesso.")
    response = resposta_json({"message": "Cofre inicializado com sucesso."}, 201)
    response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="Strict")
    return response


@app.post("/api/unlock")
def unlock_vault():
    if not cofre_existe():
        return resposta_json({"error": "O cofre ainda nao foi criado."}, 404)

    dados = request.get_json(silent=True) or {}
    master_password = (dados.get("master_password") or "").strip()

    if not master_password:
        return resposta_json({"error": "Informe a senha mestra."}, 400)

    metadata = carregar_metadata()
    chave = gerar_chave(master_password, metadata.salt.encode("utf-8"), metadata.iterations)

    try:
        descriptografar_cofre(chave)
    except ValueError as erro:
        registrar_log("Tentativa de desbloqueio com senha invalida.")
        return resposta_json({"error": str(erro)}, 401)

    session_id = criar_sessao(chave)
    registrar_log("Cofre desbloqueado com sucesso.")
    response = resposta_json({"message": "Cofre desbloqueado com sucesso."})
    response.set_cookie(SESSION_COOKIE, session_id, httponly=True, samesite="Strict")
    return response


@app.post("/api/lock")
def lock_vault():
    response = resposta_json({"message": "Cofre bloqueado."})
    registrar_log("Sessao do cofre encerrada.")
    return limpar_sessao(response)


@app.get("/api/entries")
def listar_entries():
    _, chave = autenticacao_obrigatoria()
    if not chave:
        return resposta_json({"error": "Cofre bloqueado."}, 401)

    dados = descriptografar_cofre(chave)
    entries = sorted(dados["entries"], key=lambda item: item["service"].lower())
    return resposta_json({"entries": [normalizar_entry(item) for item in entries]})


@app.post("/api/entries")
def criar_entry():
    _, chave = autenticacao_obrigatoria()
    if not chave:
        return resposta_json({"error": "Cofre bloqueado."}, 401)

    dados_request = request.get_json(silent=True) or {}
    try:
        category, service, username, password, url, notes, icon_override = validar_entry_payload(dados_request)
    except ValueError as erro:
        return resposta_json({"error": str(erro)}, 400)

    metadata = carregar_metadata()
    dados = descriptografar_cofre(chave)
    agora = datetime.now(timezone.utc).isoformat()
    nova_entry = {
        "id": token_urlsafe(12),
        "category": category,
        "service": service,
        "username": username,
        "password": password,
        "url": url,
        "notes": notes,
        "icon_override": icon_override,
        "created_at": agora,
        "updated_at": agora,
    }
    dados["entries"].append(nova_entry)
    salvar_cofre(chave, dados, metadata.salt, metadata.iterations)
    registrar_log(f"Credencial adicionada: {service}.")
    return resposta_json({"entry": normalizar_entry(nova_entry)}, 201)


@app.put("/api/entries/<entry_id>")
def atualizar_entry(entry_id: str):
    _, chave = autenticacao_obrigatoria()
    if not chave:
        return resposta_json({"error": "Cofre bloqueado."}, 401)

    dados_request = request.get_json(silent=True) or {}
    try:
        category, service, username, password, url, notes, icon_override = validar_entry_payload(dados_request)
    except ValueError as erro:
        return resposta_json({"error": str(erro)}, 400)

    metadata = carregar_metadata()
    dados = descriptografar_cofre(chave)

    for entry in dados["entries"]:
        if entry["id"] == entry_id:
            entry["category"] = category
            entry["service"] = service
            entry["username"] = username
            entry["password"] = password
            entry["url"] = url
            entry["notes"] = notes
            entry["icon_override"] = icon_override
            entry["updated_at"] = datetime.now(timezone.utc).isoformat()
            salvar_cofre(chave, dados, metadata.salt, metadata.iterations)
            registrar_log(f"Credencial atualizada: {service}.")
            return resposta_json({"entry": normalizar_entry(entry)})

    return resposta_json({"error": "Entrada nao encontrada."}, 404)


@app.post("/api/import")
def importar_entries():
    _, chave = autenticacao_obrigatoria()
    if not chave:
        return resposta_json({"error": "Cofre bloqueado."}, 401)

    dados_request = request.get_json(silent=True) or {}
    raw_text = (dados_request.get("raw_text") or "").strip()
    default_category = (dados_request.get("default_category") or "Importados").strip() or "Importados"

    if not raw_text:
        return resposta_json({"error": "Cole algum conteudo para importar."}, 400)

    importadas = parse_bulk_entries(raw_text, default_category)
    if not importadas:
        return resposta_json({"error": "Nenhuma credencial valida foi encontrada no texto colado."}, 400)

    metadata = carregar_metadata()
    dados = descriptografar_cofre(chave)
    agora = datetime.now(timezone.utc).isoformat()
    novas_entries: list[dict[str, Any]] = []
    chaves_existentes = {chave_duplicidade(item) for item in dados["entries"]}
    ignoradas = 0

    for item in importadas:
        chave_item = chave_duplicidade(item)
        if chave_item in chaves_existentes:
            ignoradas += 1
            continue

        entry = {
            "id": token_urlsafe(12),
            "category": item["category"],
            "service": item["service"],
            "username": item["username"],
            "password": item["password"],
            "url": item.get("url", ""),
            "notes": item.get("notes", ""),
            "icon_override": item.get("icon_override", ""),
            "created_at": agora,
            "updated_at": agora,
        }
        dados["entries"].append(entry)
        novas_entries.append(entry)
        chaves_existentes.add(chave_item)

    salvar_cofre(chave, dados, metadata.salt, metadata.iterations)
    registrar_log(
        f"Importacao em massa concluida com {len(novas_entries)} credencial(is) e {ignoradas} ignorada(s) por duplicidade."
    )
    return resposta_json(
        {
            "entries": [normalizar_entry(item) for item in novas_entries],
            "count": len(novas_entries),
            "skipped_duplicates": ignoradas,
        },
        201,
    )


@app.delete("/api/entries/<entry_id>")
def deletar_entry(entry_id: str):
    _, chave = autenticacao_obrigatoria()
    if not chave:
        return resposta_json({"error": "Cofre bloqueado."}, 401)

    metadata = carregar_metadata()
    dados = descriptografar_cofre(chave)
    entries = dados["entries"]
    filtradas = [entry for entry in entries if entry["id"] != entry_id]

    if len(filtradas) == len(entries):
        return resposta_json({"error": "Entrada nao encontrada."}, 404)

    dados["entries"] = filtradas
    salvar_cofre(chave, dados, metadata.salt, metadata.iterations)
    registrar_log(f"Credencial removida: {entry_id}.")
    return resposta_json({"message": "Entrada removida com sucesso."})


@app.get("/api/duplicates")
def listar_duplicados():
    _, chave = autenticacao_obrigatoria()
    if not chave:
        return resposta_json({"error": "Cofre bloqueado."}, 401)

    dados = descriptografar_cofre(chave)
    return resposta_json({"groups": duplicate_groups(dados["entries"])})


@app.post("/api/duplicates/remove")
def remover_duplicados():
    _, chave = autenticacao_obrigatoria()
    if not chave:
        return resposta_json({"error": "Cofre bloqueado."}, 401)

    dados_request = request.get_json(silent=True) or {}
    group_key = (dados_request.get("group_key") or "").strip()
    if not group_key:
        return resposta_json({"error": "Informe o grupo de duplicados."}, 400)

    metadata = carregar_metadata()
    dados = descriptografar_cofre(chave)
    grupos: dict[str, list[dict[str, Any]]] = {}
    for entry in dados["entries"]:
        grupos.setdefault(chave_duplicidade(entry), []).append(entry)

    itens = grupos.get(group_key)
    if not itens or len(itens) < 2:
        return resposta_json({"error": "Grupo de duplicados nao encontrado."}, 404)

    ordenados = sorted(itens, key=lambda item: item.get("created_at", ""))
    manter_id = ordenados[0]["id"]
    remover_ids = {item["id"] for item in ordenados[1:]}
    dados["entries"] = [entry for entry in dados["entries"] if entry["id"] not in remover_ids]
    salvar_cofre(chave, dados, metadata.salt, metadata.iterations)
    registrar_log(f"Duplicados removidos do grupo {group_key}, mantendo {manter_id}.")
    return resposta_json(
        {
            "message": "Duplicados removidos com sucesso.",
            "kept_id": manter_id,
            "removed_count": len(remover_ids),
        }
    )


@app.get("/api/generate-password")
def generate_password():
    tamanho_str = request.args.get("length", "20")
    try:
        tamanho = max(12, min(64, int(tamanho_str)))
    except ValueError:
        tamanho = 20
    return resposta_json({"password": gerar_senha_forte(tamanho)})


if __name__ == "__main__":
    registrar_log("Aplicacao iniciada.")
    app.run(host="127.0.0.1", port=5050, debug=False)
