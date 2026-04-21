# Configuracao E Passo A Passo

Este documento explica como a automacao de noticias diarias sobre IA foi montada, quais arquivos foram criados e como tudo funciona em conjunto.

## Objetivo Do Projeto

A proposta desta automacao e:

- buscar noticias recentes sobre inteligencia artificial
- filtrar assuntos como ChatGPT, Claude, OpenAI e Anthropic
- montar um e-mail com visual mais profissional
- enviar automaticamente para `saulosouza@outlook.com`
- permitir execucao diaria em segundo plano no Windows

## Estrutura Criada

Dentro da pasta `Email Profissional/Noticias IA Diarias/` foram criados estes arquivos:

- `enviar_noticias_ia.py`
- `.env.example`
- `.env`
- `agendar_noticias_ia.ps1`
- `README.md`
- `CONFIGURACAO_E_PASSO_A_PASSO.md`

## O Papel De Cada Arquivo

### `enviar_noticias_ia.py`

E o script principal.

Ele faz estas etapas:

1. le o arquivo `.env`
2. carrega as configuracoes de envio
3. consulta feeds RSS de noticias
4. filtra noticias recentes
5. monta um e-mail em texto e HTML
6. envia o e-mail via SMTP
7. registra o estado para evitar repeticao no mesmo dia

### `.env.example`

Serve como modelo de configuracao.

Ele mostra quais variaveis o script precisa para funcionar.

### `.env`

E o arquivo real com suas configuracoes locais.

Foi configurado com:

- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_USER=saulosouzati@gmail.com`
- `EMAIL_FROM=saulosouzati@gmail.com`
- `EMAIL_TO=saulosouza@outlook.com`

A senha nao foi colocada de verdade. No lugar dela ficou um placeholder para voce substituir com seguranca.

### `agendar_noticias_ia.ps1`

E um script PowerShell para criar uma tarefa agendada no Windows.

Essa tarefa pode executar o Python em horario fixo todos os dias, em segundo plano.

### `README.md`

Explica o modulo de forma resumida.

### `CONFIGURACAO_E_PASSO_A_PASSO.md`

Este arquivo que voce esta lendo agora.

## Como O Script Busca As Noticias

O script usa busca RSS do Google News.

Para cada topico, ele monta uma URL de RSS.

Topicos usados:

- `ChatGPT`
- `Claude AI`
- `OpenAI`
- `Anthropic`
- `inteligencia artificial`

Depois disso:

1. baixa o XML de cada feed
2. le os itens da lista
3. extrai titulo, link, data, resumo e fonte
4. mantem apenas noticias recentes
5. remove links repetidos

## Como O E-mail E Montado

O e-mail e criado com a classe `EmailMessage` do Python.

Ele tem duas versoes:

- texto simples
- HTML

Isso e importante porque:

- clientes de e-mail modernos mostram o HTML
- clientes mais limitados ainda conseguem ler a versao texto

## Como O HTML Foi Pensado

O HTML do e-mail foi feito com:

- cabecalho visual com gradiente
- blocos separados por noticia
- informacoes de topico, fonte e horario
- botao para abrir a noticia
- aparencia limpa e mais profissional

## Como O Envio Funciona

O envio usa:

- `smtplib`
- `ssl`

Fluxo:

1. conecta ao servidor SMTP do Gmail
2. ativa `starttls`
3. faz login com o usuario e a senha de app
4. envia a mensagem

## Por Que Foi Necessaria Senha De App

Para automacoes desse tipo com Gmail, o ideal e usar senha de app.

Ela e mais apropriada porque:

- evita usar a senha principal da conta
- funciona melhor em scripts SMTP
- pode ser revogada separadamente

## Como O Script Evita Repeticao

Foi criado o arquivo `estado_envio.json`.

Ele guarda:

- a ultima data de envio
- os links enviados no dia

Assim, se o script rodar mais de uma vez no mesmo dia, ele tenta nao repetir exatamente as mesmas noticias.

Esse arquivo esta no `.gitignore`, porque e um dado local de execucao.

## Como A Execucao Em Segundo Plano Funciona

No Windows, o agendamento pode ser feito com o Agendador de Tarefas.

O arquivo `agendar_noticias_ia.ps1` usa:

- `New-ScheduledTaskAction`
- `New-ScheduledTaskTrigger`
- `Register-ScheduledTask`

A ideia e:

1. apontar para `pythonw.exe`
2. informar o caminho do script
3. definir um horario diario
4. registrar a tarefa

O uso do `pythonw.exe` permite execucao sem abrir janela do terminal.

## Melhorias Adicionadas Depois

Para facilitar testes e manutencao, a automacao tambem recebeu:

- modo `--dry-run` para validar a busca sem enviar e-mail
- modo `--test` para forcar um envio imediato
- arquivo `execucao.log` para registrar o que aconteceu em cada execucao
- caminhos reais da sua maquina no `agendar_noticias_ia.ps1`

## O Que Ja Foi Feito

Estas etapas ja foram executadas:

1. criacao da pasta do projeto
2. criacao do script base de e-mail profissional
3. criacao do modulo de noticias diarias de IA
4. criacao do `.env.example`
5. criacao do `.env` com remetente Gmail e destinatario Outlook
6. criacao do script de agendamento
7. validacao de sintaxe com `python -m py_compile`
8. atualizacao do `README.md` principal
9. ajuste do `.gitignore` para proteger arquivos locais

## O Que Falta Para Funcionar De Verdade

Voce ainda precisa:

1. substituir `SMTP_PASSWORD` no `.env` pela sua senha de app do Gmail
2. ajustar o caminho real do Python no `agendar_noticias_ia.ps1`
3. ajustar o caminho real do arquivo `enviar_noticias_ia.py` no `agendar_noticias_ia.ps1`
4. executar o script manualmente uma vez para testar
5. registrar a tarefa agendada no Windows

## Comandos De Teste

Para validar sem enviar:

```bash
python "Email Profissional/Noticias IA Diarias/enviar_noticias_ia.py" --dry-run
```

Para testar envio real:

```bash
python "Email Profissional/Noticias IA Diarias/enviar_noticias_ia.py" --test
```

## Exemplo De Fluxo Final

Quando tudo estiver pronto, o comportamento esperado sera:

1. o Windows dispara a tarefa no horario definido
2. o Python executa `enviar_noticias_ia.py`
3. o script busca noticias recentes de IA
4. monta o e-mail em HTML
5. envia de `saulosouzati@gmail.com`
6. o destinatario `saulosouza@outlook.com` recebe o resumo do dia

## Observacoes Importantes

- o arquivo `.env` nao deve ser enviado para o GitHub
- a senha de app deve ficar apenas no ambiente local
- o script depende de acesso a internet para buscar noticias e enviar o e-mail
- se nao houver noticias novas, o script pode encerrar sem envio

## Resumo Tecnico

Tecnologias e recursos usados:

- Python
- `urllib.request`
- RSS do Google News
- `xml.etree.ElementTree`
- `EmailMessage`
- `smtplib`
- `ssl`
- PowerShell
- Windows Task Scheduler

## Proximo Passo Recomendado

O proximo passo mais util e fazer a versao 1.1 com:

- teste manual guiado
- log de execucao
- tratamento melhor de erros de rede
- opcao de resumo mais curto ou mais detalhado
- horario de envio configuravel
