# Noticias IA Local

Automacao para buscar noticias recentes sobre inteligencia artificial e gerar um arquivo TXT local para leitura simples.

## O Que Este Projeto Faz

- busca noticias sobre IA em feeds RSS
- prioriza temas como ChatGPT, Claude, OpenAI, Anthropic e inteligencia artificial
- gera um arquivo `.txt` com titulo, fonte, resumo, horario e link
- salva tudo localmente, sem envio de e-mail
- pode ser executado manualmente ou agendado no Windows

## Arquivos

- `gerar_noticias_ia_txt.py`
- `.env.example`
- `agendar_noticias_ia_local.ps1`

## Como Executar

```bash
python "gerar_noticias_ia_txt.py"
```

Por padrao, o arquivo sera salvo em:

```text
leituras/noticias_ia_YYYY-MM-DD.txt
```

## Opcoes Uteis

```bash
python "gerar_noticias_ia_txt.py" --max-noticias 15
python "gerar_noticias_ia_txt.py" --dias 2
python "gerar_noticias_ia_txt.py" --saida "minhas_noticias.txt"
python "gerar_noticias_ia_txt.py" --dry-run
```

## Configuracao Opcional

O script funciona sem `.env`.

Se quiser ajustar o comportamento padrao, crie um arquivo `.env` nesta pasta com base no `.env.example`.

Campos disponiveis:

- `MAX_NOTICIAS`
- `DIAS_RECENTES`
- `PASTA_SAIDA`
- `TOPICOS`

## Agendamento

O arquivo `agendar_noticias_ia_local.ps1` serve como base para registrar uma tarefa diaria no Windows Task Scheduler.

Antes de usar, ajuste:

- caminho do Python
- caminho do script
- horario desejado

## Arquivos Locais Gerados

- `leituras/*.txt`
- `execucao.log`
- `estado_noticias.json`

Esses arquivos sao locais e nao precisam ir para o Git.
