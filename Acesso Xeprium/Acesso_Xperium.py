"""
Criado por: Saulo Prado
Versao: 1.10
Objetivo: Automacao de acesso a plataforma
Automatizar o acesso a plataforma Xperiun usando Selenium,
realizando a abertura do navegador, o preenchimento das
credenciais e a tentativa de confirmacao do login.
"""

from getpass import getpass
from datetime import datetime
from pathlib import Path
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# URL da pagina de login.
LOGIN_URL = "https://app.xperiun.com/entrar"
BASE_DIR = Path(__file__).resolve().parent
HISTORICO_ARQUIVO = BASE_DIR / "historico_acessos_xperium.txt"

# Seletores dos campos principais do formulario.
# Aqui usamos CSS Selector porque os inputs de e-mail e senha
# tendem a ser mais estaveis do que classes geradas dinamicamente.
EMAIL_SELECTOR = (By.CSS_SELECTOR, "input[type='email']")
PASSWORD_SELECTOR = (By.CSS_SELECTOR, "input[type='password']")

# Seletor mais flexivel para o botao de login.
# Como a pagina foi feita em Bubble, o elemento clicavel pode variar:
# pode ser um <button>, um elemento com role='button'
# ou ate uma div/span/a estilizada como botao.
LOGIN_BUTTON_SELECTOR = (
    By.XPATH,
    "//button[contains(., 'Entrar')]"
    " | //button[@type='submit']"
    " | //input[@type='submit']"
    " | //*[@role='button' and contains(normalize-space(.), 'Entrar')]"
    " | //*[(self::div or self::span or self::a) and contains(normalize-space(.), 'Entrar')]",
)


def solicitar_credenciais():
    # Se houver terminal interativo, mantemos a experiencia simples por texto.
    if sys.stdin.isatty():
        email = input("Digite seu e-mail: ").strip()
        senha = getpass("Digite sua senha: ").strip()
    else:
        # Ao clicar em Run no VS Code ou em outros launchers, nem sempre existe
        # um terminal interativo. Nesse caso abrimos caixas de dialogo simples.
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        email = simpledialog.askstring(
            "Acesso Xperium",
            "Digite seu e-mail:",
            parent=root,
        )
        senha = simpledialog.askstring(
            "Acesso Xperium",
            "Digite sua senha:",
            parent=root,
            show="*",
        )
        root.destroy()

        email = (email or "").strip()
        senha = (senha or "").strip()

    # Valida se ambos os campos foram preenchidos.
    # Se algum estiver vazio, interrompe a execucao com uma mensagem clara.
    if not email or not senha:
        raise ValueError("E-mail e senha precisam ser informados.")

    # Retorna os dois valores para serem usados no login.
    return email, senha


def criar_driver():
    # Cria as configuracoes do Chrome.
    # Aqui voce pode adicionar opcoes futuramente, como modo headless.
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")

    # O webdriver_manager baixa e gerencia automaticamente a versao correta
    # do ChromeDriver, evitando precisar instalar manualmente.
    service = Service(ChromeDriverManager().install())

    # Cria e devolve a instancia do navegador Chrome pronta para uso.
    return webdriver.Chrome(service=service, options=chrome_options)


def registrar_acesso_bem_sucedido(email):
    # Registra em arquivo texto apenas os logins confirmados como bem-sucedidos.
    momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"{momento} | acesso bem-sucedido | {email}\n"

    with open(HISTORICO_ARQUIVO, "a", encoding="utf-8") as arquivo:
        arquivo.write(linha)


def clicar_botao_login(driver, wait):
    # Aguarda candidatos ao clique aparecerem e tenta o mais promissor primeiro.
    candidatos = wait.until(EC.presence_of_all_elements_located(LOGIN_BUTTON_SELECTOR))

    for botao in candidatos:
        try:
            # Ignora elementos invisiveis ou sem area clicavel real.
            if not botao.is_displayed():
                continue

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
            wait.until(lambda d: botao.is_enabled())

            # Tenta o clique nativo primeiro.
            botao.click()
            return
        except Exception:
            try:
                # Se o Selenium nao conseguir clicar, dispara o clique por JavaScript.
                driver.execute_script("arguments[0].click();", botao)
                return
            except Exception:
                continue

    raise RuntimeError("Nao foi possivel clicar no botao Entrar.")


def aguardar_resultado_login(driver, wait):
    try:
        # Primeiro tenta detectar mudanca de URL.
        # Em muitos sistemas, apos o login a pagina redireciona para outra rota.
        wait.until(EC.url_changes(LOGIN_URL))
        return "success", f"Login concluido. Nova URL: {driver.current_url}"
    except TimeoutException:
        # Se a URL nao mudou dentro do tempo de espera, seguimos para outra checagem.
        pass

    try:
        # Outra pista de sucesso e o formulario desaparecer da tela.
        # Se o campo de e-mail sumir, pode significar que a tela de login saiu.
        wait.until(EC.invisibility_of_element_located(EMAIL_SELECTOR))
        return "success", "O formulario de login sumiu da tela, sinal de que o acesso pode ter sido concluido."
    except TimeoutException:
        # Se nem a URL mudou nem o formulario sumiu, nao temos confirmacao forte.
        pass

    # Retorna um aviso em vez de erro, porque pode existir algum comportamento
    # especifico do site que nao foi capturado por essas validacoes.
    return "warning", "Nao houve confirmacao clara de sucesso. Verifique se apareceu alguma mensagem de erro na tela."


def testar_login():
    # Mensagem inicial para informar ao usuario que o processo comecou.
    print("Iniciando processo de login...")

    # Coleta credenciais digitadas no terminal.
    email, senha = solicitar_credenciais()

    # Abre o navegador.
    driver = criar_driver()

    # Define um tempo maximo de espera de 30 segundos para cada condicao.
    # Isso evita falhas por carregamento lento da pagina.
    wait = WebDriverWait(driver, 30)

    try:
        # Acessa a pagina de login.
        driver.get(LOGIN_URL)
        print("Aguardando campos de login ficarem visiveis...")

        # Espera o campo de e-mail ficar clicavel e depois digita o valor informado.
        wait.until(EC.element_to_be_clickable(EMAIL_SELECTOR)).send_keys(email)

        # Espera o campo de senha ficar clicavel e depois digita a senha.
        campo_senha = wait.until(EC.element_to_be_clickable(PASSWORD_SELECTOR))
        campo_senha.send_keys(senha)

        # Alguns formularios enviam com Enter; tentamos isso antes do clique visual.
        campo_senha.send_keys(Keys.ENTER)

        # Se a URL nao mudar rapidamente, seguimos para o clique do botao.
        try:
            WebDriverWait(driver, 3).until(EC.url_changes(LOGIN_URL))
        except TimeoutException:
            clicar_botao_login(driver, wait)

        # Verifica sinais de sucesso ou falta de confirmacao apos a tentativa de login.
        status, mensagem = aguardar_resultado_login(driver, wait)
        print(mensagem)

        if status == "success":
            registrar_acesso_bem_sucedido(email)
            print(f"Historico atualizado em: {HISTORICO_ARQUIVO}")

        # Se nao houve confirmacao clara, mostra a URL atual para ajudar no diagnostico.
        if status != "success":
            print(f"URL atual apos tentativa de login: {driver.current_url}")

        # Em execucao por terminal, aguardamos confirmacao textual.
        # Em execucao por clique, mostramos uma caixa simples.
        if sys.stdin.isatty():
            input("Pressione Enter para fechar o navegador...")
        else:
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showinfo(
                "Acesso Xperium",
                "Clique em OK para fechar o navegador.",
                parent=root,
            )
            root.destroy()
    except Exception as erro:
        # Captura qualquer erro inesperado e mostra uma mensagem amigavel.
        print(f"Ocorreu um erro durante o login: {erro}")
        if not sys.stdin.isatty():
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            messagebox.showerror("Acesso Xperium", f"Ocorreu um erro durante o login:\n{erro}", parent=root)
            root.destroy()
    finally:
        # Fecha o navegador sempre, mesmo em caso de erro.
        # O finally garante a limpeza dos recursos.
        driver.quit()


if __name__ == "__main__":
    # Executa o script apenas quando o arquivo for rodado diretamente.
    # Se ele for importado em outro script, esta parte nao sera executada.
    testar_login()
