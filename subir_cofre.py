"""
Launcher do Cofre de Senhas.

Executa o fluxo completo:
1. garante as dependencias do projeto
2. sobe o servidor local do cofre
3. abre o navegador automaticamente
"""

from __future__ import annotations

from pathlib import Path
import socket
import subprocess
import sys
import time
import webbrowser


ROOT_DIR = Path(__file__).resolve().parent
COFRE_DIR = ROOT_DIR / "Cofre de Senhas"
APP_PATH = COFRE_DIR / "app.py"
REQUIREMENTS_PATH = COFRE_DIR / "requirements.txt"
HOST = "127.0.0.1"
PORT = 5050
COFRE_URL = f"http://{HOST}:{PORT}"


def porta_esta_aberta(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conexao:
        conexao.settimeout(0.5)
        return conexao.connect_ex((host, port)) == 0


def garantir_estrutura() -> None:
    if not COFRE_DIR.exists():
        raise FileNotFoundError(f"Pasta do cofre nao encontrada: {COFRE_DIR}")
    if not APP_PATH.exists():
        raise FileNotFoundError(f"Arquivo principal nao encontrado: {APP_PATH}")
    if not REQUIREMENTS_PATH.exists():
        raise FileNotFoundError(f"Arquivo de dependencias nao encontrado: {REQUIREMENTS_PATH}")


def instalar_dependencias() -> None:
    print("Verificando dependencias do cofre...")
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)],
        cwd=str(ROOT_DIR),
    )


def iniciar_servidor() -> subprocess.Popen[bytes]:
    print("Iniciando servidor do cofre...")
    creationflags = 0
    if sys.platform.startswith("win"):
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    return subprocess.Popen(
        [sys.executable, str(APP_PATH)],
        cwd=str(COFRE_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creationflags,
    )


def aguardar_servidor(timeout: int = 20) -> bool:
    inicio = time.time()
    while time.time() - inicio < timeout:
        if porta_esta_aberta(HOST, PORT):
            return True
        time.sleep(1)
    return False


def abrir_navegador() -> None:
    print(f"Abrindo navegador em {COFRE_URL} ...")
    webbrowser.open(COFRE_URL)


def main() -> None:
    try:
        garantir_estrutura()

        if porta_esta_aberta(HOST, PORT):
            print("O servidor do cofre ja esta em execucao.")
            abrir_navegador()
            return

        instalar_dependencias()
        processo = iniciar_servidor()

        if not aguardar_servidor():
            if processo.poll() is not None:
                raise RuntimeError("O servidor foi encerrado logo apos a inicializacao.")
            raise TimeoutError("O servidor nao respondeu dentro do tempo esperado.")

        print("Servidor do cofre iniciado com sucesso.")
        abrir_navegador()
    except Exception as erro:
        print(f"Falha ao subir o cofre: {erro}")
        input("Pressione Enter para fechar...")
        raise


if __name__ == "__main__":
    main()
