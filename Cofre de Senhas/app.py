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
from pathlib import Path
from secrets import choice, token_hex, token_urlsafe
from string import ascii_letters, digits
from typing import Any
import json

from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, jsonify, make_response, render_template, request


APP_DIR = Path(__file__).resolve().parent
VAULT_PATH = APP_DIR / "vault.enc"
LOG_PATH = APP_DIR / "cofre.log"
SESSION_COOKIE = "cofre_session"
PBKDF2_ITERATIONS = 390000
SESSION_STORE: dict[str, bytes] = {}

app = Flask(__name__, template_folder="templates", static_folder="static")


@dataclass
class VaultMetadata:
    salt: str
    iterations: int
    encrypted_data: str


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
    return {
        "id": entry["id"],
        "service": entry["service"],
        "username": entry["username"],
        "password": entry["password"],
        "url": entry.get("url", ""),
        "notes": entry.get("notes", ""),
        "created_at": entry["created_at"],
        "updated_at": entry["updated_at"],
    }


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
    service = (dados_request.get("service") or "").strip()
    username = (dados_request.get("username") or "").strip()
    password = (dados_request.get("password") or "").strip()
    url = (dados_request.get("url") or "").strip()
    notes = (dados_request.get("notes") or "").strip()

    if not service or not username or not password:
        return resposta_json({"error": "Servico, usuario e senha sao obrigatorios."}, 400)

    metadata = carregar_metadata()
    dados = descriptografar_cofre(chave)
    agora = datetime.now(timezone.utc).isoformat()
    nova_entry = {
        "id": token_urlsafe(12),
        "service": service,
        "username": username,
        "password": password,
        "url": url,
        "notes": notes,
        "created_at": agora,
        "updated_at": agora,
    }
    dados["entries"].append(nova_entry)
    salvar_cofre(chave, dados, metadata.salt, metadata.iterations)
    registrar_log(f"Credencial adicionada: {service}.")
    return resposta_json({"entry": normalizar_entry(nova_entry)}, 201)


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
