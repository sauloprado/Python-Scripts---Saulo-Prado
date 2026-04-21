# Cofre de Senhas

Cofre local de senhas com interface web, senha mestra e armazenamento criptografado.

## Objetivo

Criar uma aplicacao simples para uso pessoal que permita:

- guardar credenciais de forma local
- proteger tudo com uma senha mestra
- criptografar os dados antes de salvar em disco
- consultar, cadastrar e remover credenciais em uma interface web
- gerar senhas fortes automaticamente

## Stack

- Python
- Flask
- cryptography
- HTML, CSS e JavaScript

## Arquivos Principais

- `app.py`
- `requirements.txt`
- `templates/index.html`
- `static/styles.css`
- `static/app.js`

## Como Funciona

1. O usuario define uma senha mestra na primeira inicializacao.
2. O sistema deriva uma chave criptografica com PBKDF2.
3. O arquivo do cofre e salvo criptografado com Fernet.
4. A interface web local permite desbloquear e administrar as entradas.

## Execucao

```bash
pip install -r "Cofre de Senhas/requirements.txt"
python "Cofre de Senhas/app.py"
```

Depois, abra:

`http://127.0.0.1:5050`

## Arquivos Locais Gerados

- `vault.enc`
- `cofre.log`

Esses arquivos nao devem ir para o Git.
