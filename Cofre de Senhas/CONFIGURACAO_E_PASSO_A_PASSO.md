# Configuracao E Passo A Passo

Este projeto foi criado para armazenar senhas localmente com uma camada real de seguranca, sem salvar credenciais em texto puro.

## Ideia Central

A aplicacao funciona como um cofre local.

Em vez de guardar senhas em:

- `.txt`
- `.json`
- `.html`
- planilhas

ela faz o seguinte:

1. recebe uma senha mestra
2. deriva uma chave criptografica a partir dela
3. criptografa os dados antes de salvar
4. so libera o conteudo depois do desbloqueio correto

## Componentes

### `app.py`

Backend Flask com:

- inicializacao do cofre
- desbloqueio
- sessao local em memoria
- CRUD das entradas
- gerador de senha forte

### `templates/index.html`

Interface principal do projeto.

Ela mostra:

- tela de criacao da senha mestra
- tela de desbloqueio
- dashboard com as credenciais salvas

### `static/styles.css`

Estilo visual da interface.

### `static/app.js`

Controla a interacao do navegador com as rotas da API.

### `vault.enc`

Arquivo local criptografado do cofre.

Nao vai para o Git.

## Decisoes De Seguranca

- senha mestra nao fica salva em texto
- arquivo do cofre fica criptografado
- sessao desbloqueada fica apenas em memoria no processo Python
- cookie guarda apenas um identificador aleatorio de sessao
- senhas podem ser geradas com aleatoriedade criptografica

## Fluxo Geral

1. abrir o app local no navegador
2. criar senha mestra na primeira vez
3. desbloquear o cofre
4. adicionar servico, usuario, senha e observacoes
5. consultar as credenciais conforme necessario

## Observacao Importante

Se a senha mestra for perdida, o conteudo do cofre nao podera ser recuperado com facilidade. Isso faz parte do modelo de seguranca.
