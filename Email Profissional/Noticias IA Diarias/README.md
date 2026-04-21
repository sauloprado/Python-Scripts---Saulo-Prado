# Noticias IA Diarias

Automacao para buscar noticias recentes sobre IA e enviar um resumo diario por e-mail com layout HTML.

## O Que Este Projeto Faz

- busca noticias sobre IA em feeds RSS
- prioriza temas como ChatGPT, Claude, OpenAI, Anthropic e inteligencia artificial
- monta um e-mail com visual profissional
- envia automaticamente para um destinatario definido
- pode ser executado em segundo plano todos os dias no Windows

## Arquivos

- `enviar_noticias_ia.py`
- `.env.example`
- `agendar_noticias_ia.ps1`

## Como Funciona

1. O script carrega as configuracoes do arquivo `.env`.
2. Busca noticias em multiplos feeds RSS.
3. Filtra itens mais recentes.
4. Gera um resumo em HTML.
5. Envia o e-mail com SMTP.

## Modos De Execucao

- `python enviar_noticias_ia.py --dry-run`
- `python enviar_noticias_ia.py --test`

O modo `--dry-run` monta o fluxo sem enviar.

O modo `--test` tenta enviar imediatamente, mesmo que ja tenha havido envio no dia.

## Configuracao

Crie um arquivo `.env` nesta pasta com base no `.env.example`.

Campos principais:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `EMAIL_FROM`
- `EMAIL_TO`

## Agendamento Em Segundo Plano

O arquivo `agendar_noticias_ia.ps1` serve como base para registrar uma tarefa diaria no Windows Task Scheduler.

Antes de usar, ajuste:

- caminho do Python
- caminho do script
- horario desejado

## Log Local

O script grava eventos em `execucao.log` para facilitar diagnostico quando estiver rodando em segundo plano.

## Observacao

O projeto esta configurado para enviar ao endereco `saulosouza@outlook.com`.
