"""
Criado por: Saulo Prado
Versao: 1.00
Objetivo:
Criar uma base para envio de e-mails com formatacao HTML
agradavel e suporte a anexos usando Python.
"""

from email.message import EmailMessage
from mimetypes import guess_type
from pathlib import Path
import smtplib
import ssl


def criar_html_email(nome_destinatario, mensagem_principal):
    # Gera um corpo HTML simples, limpo e reutilizavel.
    return f"""
    <html>
        <body style="margin:0;padding:0;background-color:#f4f1ea;font-family:Arial,sans-serif;color:#1f2937;">
            <div style="max-width:640px;margin:32px auto;background:#ffffff;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;">
                <div style="background:linear-gradient(135deg,#1f4f46,#355f52);padding:28px 32px;color:#ffffff;">
                    <h1 style="margin:0;font-size:24px;">Mensagem Enviada por Automacao</h1>
                    <p style="margin:8px 0 0;font-size:14px;opacity:0.9;">Modelo inicial para e-mails mais elegantes e profissionais.</p>
                </div>
                <div style="padding:32px;">
                    <p style="margin-top:0;font-size:16px;">Ola, {nome_destinatario}.</p>
                    <p style="font-size:15px;line-height:1.7;">{mensagem_principal}</p>
                    <div style="margin:28px 0;padding:18px 20px;background:#f9fafb;border-left:4px solid #355f52;border-radius:8px;">
                        <p style="margin:0;font-size:14px;line-height:1.6;">
                            Este e-mail foi montado por um script Python com suporte a HTML e anexos.
                        </p>
                    </div>
                    <p style="font-size:15px;line-height:1.7;margin-bottom:0;">
                        Atenciosamente,<br>
                        <strong>Saulo Prado</strong>
                    </p>
                </div>
            </div>
        </body>
    </html>
    """


def anexar_arquivo(mensagem, caminho_arquivo):
    # Faz o anexo de um arquivo local, detectando o tipo automaticamente.
    arquivo = Path(caminho_arquivo)

    if not arquivo.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {arquivo}")

    mime_type, _ = guess_type(str(arquivo))
    if mime_type:
        maintype, subtype = mime_type.split("/", 1)
    else:
        maintype, subtype = "application", "octet-stream"

    with arquivo.open("rb") as conteudo:
        mensagem.add_attachment(
            conteudo.read(),
            maintype=maintype,
            subtype=subtype,
            filename=arquivo.name,
        )


def montar_email(remetente, destinatario, assunto, nome_destinatario, mensagem_principal, caminho_arquivo):
    # Monta a mensagem completa com texto simples, HTML e anexo.
    mensagem = EmailMessage()
    mensagem["From"] = remetente
    mensagem["To"] = destinatario
    mensagem["Subject"] = assunto

    mensagem.set_content(
        f"Ola, {nome_destinatario}.\n\n"
        f"{mensagem_principal}\n\n"
        "Este e-mail contem uma versao HTML e pode incluir anexo.\n\n"
        "Atenciosamente,\n"
        "Saulo Prado"
    )

    mensagem.add_alternative(
        criar_html_email(nome_destinatario, mensagem_principal),
        subtype="html",
    )

    if caminho_arquivo:
        anexar_arquivo(mensagem, caminho_arquivo)

    return mensagem


def enviar_email_smtp(servidor_smtp, porta, usuario, senha, mensagem):
    # Envia o e-mail por SMTP seguro com TLS.
    contexto = ssl.create_default_context()

    with smtplib.SMTP(servidor_smtp, porta) as servidor:
        servidor.starttls(context=contexto)
        servidor.login(usuario, senha)
        servidor.send_message(mensagem)


def main():
    # Exemplo inicial de configuracao.
    remetente = "seu_email@exemplo.com"
    destinatario = "destinatario@exemplo.com"
    assunto = "Envio automatico com anexo"
    nome_destinatario = "Nome da Pessoa"
    mensagem_principal = (
        "Segue em anexo o arquivo solicitado. "
        "Estou enviando esta mensagem por meio de uma automacao em Python."
    )
    caminho_arquivo = "caminho/do/arquivo.pdf"

    servidor_smtp = "smtp.gmail.com"
    porta = 587
    usuario = remetente
    senha = "SUA_SENHA_OU_SENHA_DE_APP"

    email = montar_email(
        remetente=remetente,
        destinatario=destinatario,
        assunto=assunto,
        nome_destinatario=nome_destinatario,
        mensagem_principal=mensagem_principal,
        caminho_arquivo=caminho_arquivo,
    )

    # Descomente a linha abaixo quando preencher os dados reais.
    # enviar_email_smtp(servidor_smtp, porta, usuario, senha, email)

    print("Modelo de e-mail criado com sucesso.")
    print("Preencha as configuracoes reais para realizar o envio.")


if __name__ == "__main__":
    main()
