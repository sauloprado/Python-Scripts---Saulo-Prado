# Configuracao E Passo A Passo

Este projeto gera um resumo local de noticias sobre inteligencia artificial em arquivo TXT.

## Ideia Central

A automacao nao envia e-mail.

Ela faz o seguinte:

1. consulta feeds RSS do Google News
2. busca topicos ligados a inteligencia artificial
3. filtra noticias recentes
4. monta um texto simples para leitura
5. salva um arquivo `.txt` local

## Arquivos Criados

- `gerar_noticias_ia_txt.py`
- `.env.example`
- `agendar_noticias_ia_local.ps1`
- `README.md`

## Script Principal

### `gerar_noticias_ia_txt.py`

Responsavel por:

- ler configuracoes opcionais do `.env`
- consultar os feeds RSS
- remover duplicidades por link
- limpar textos HTML vindos dos feeds
- ordenar as noticias mais recentes
- gerar o arquivo TXT em `leituras/`
- registrar logs em `execucao.log`

## Configuracao Opcional

O script funciona mesmo sem `.env`.

Se quiser personalizar, copie `.env.example` para `.env` e ajuste:

```text
MAX_NOTICIAS=10
DIAS_RECENTES=1
PASTA_SAIDA=leituras
TOPICOS=ChatGPT,Claude AI,OpenAI,Anthropic,inteligencia artificial
```

## Execucao Manual

Na pasta do projeto:

```bash
python gerar_noticias_ia_txt.py
```

Ou a partir da raiz do repositorio:

```bash
python "Noticias IA Local/gerar_noticias_ia_txt.py"
```

## Saida Gerada

O arquivo padrao segue este formato:

```text
Noticias IA Local
Gerado em: 25/04/2026 16:30
Periodo consultado: ultimos 1 dia(s)
Total encontrado: 10 noticia(s)

1. Titulo da noticia
Fonte: Nome da fonte
Topico: ChatGPT
Publicado em: 25/04/2026 15:10
Resumo: resumo limpo da noticia
Link: https://...
```

## Opcoes De Linha De Comando

Limitar quantidade:

```bash
python gerar_noticias_ia_txt.py --max-noticias 15
```

Buscar em mais dias:

```bash
python gerar_noticias_ia_txt.py --dias 2
```

Escolher saida:

```bash
python gerar_noticias_ia_txt.py --saida "noticias_hoje.txt"
```

Validar sem salvar:

```bash
python gerar_noticias_ia_txt.py --dry-run
```

## Agendamento No Windows

O arquivo `agendar_noticias_ia_local.ps1` cria uma tarefa diaria no Task Scheduler.

Antes de usar, confirme:

- caminho do `pythonw.exe`
- caminho do script `gerar_noticias_ia_txt.py`
- horario desejado

## Arquivos Locais

Estes arquivos sao gerados localmente e nao precisam ser versionados:

- `leituras/*.txt`
- `execucao.log`
- `estado_noticias.json`

## Observacao

O script ainda depende de internet para consultar os feeds RSS, mas todo o resultado fica salvo localmente em TXT.
