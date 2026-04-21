# Python Scripts - Saulo Prado

Colecao pessoal de scripts Python voltados para automacao, produtividade, testes praticos e aprendizado aplicado.

Este repositorio reune pequenos projetos uteis do dia a dia, com foco em organizacao, clareza de codigo e evolucao continua. A ideia nao e apenas guardar arquivos, mas construir uma base reutilizavel de automacoes reais.

## Visao Geral

Aqui voce vai encontrar scripts que ajudam a:

- automatizar tarefas repetitivas
- acelerar rotinas operacionais
- registrar aprendizados com projetos praticos
- transformar estudos em codigo reutilizavel
- manter um historico versionado da evolucao tecnica

## Projeto Em Destaque

### Noticias IA Diarias por E-mail

Uma das automacoes mais interessantes deste repositorio e o projeto de envio diario de noticias sobre inteligencia artificial por e-mail.

Essa automacao foi criada para:

- buscar noticias recentes sobre ChatGPT, Claude, OpenAI, Anthropic e IA em geral
- montar um resumo em HTML com visual mais profissional
- enviar automaticamente para um destinatario definido
- funcionar em segundo plano com agendamento diario no Windows

Arquivos principais:

- `Email Profissional/Noticias IA Diarias/enviar_noticias_ia.py`
- `Email Profissional/Noticias IA Diarias/agendar_noticias_ia.ps1`
- `Email Profissional/Noticias IA Diarias/CONFIGURACAO_E_PASSO_A_PASSO.md`

Esse projeto representa bem a proposta do repositorio: transformar uma necessidade real do dia a dia em uma automacao util, documentada e reutilizavel.

## Estrutura Atual

### `Acesso Xeprium/`

Automacao de acesso a plataforma Xperiun com Python e Selenium.

Arquivo principal:

- `Acesso_Xperium.py`

O script realiza:

- abertura automatica do navegador
- captura de credenciais via terminal
- preenchimento do formulario de login
- tentativa de clique e envio do acesso
- validacao basica do resultado
- registro local de acessos bem-sucedidos

### `Email Profissional/`

Base inicial para envio de e-mails com HTML, anexos e estrutura pronta para evoluir para automacoes mais sofisticadas.

Arquivo principal:

- `Email_Profissional_Com_Anexo.py`

O projeto foi pensado para permitir:

- mensagens com visual mais elegante
- envio com anexo
- padronizacao de comunicacoes recorrentes
- futura expansao para historico, templates e envio em lote

### `Email Profissional/Noticias IA Diarias/`

Automacao pensada para buscar noticias recentes sobre inteligencia artificial e enviar um resumo diario por e-mail de forma automatica.

Arquivos principais:

- `enviar_noticias_ia.py`
- `.env.example`
- `agendar_noticias_ia.ps1`

O projeto ja nasce preparado para:

- consolidar noticias sobre ChatGPT, Claude, OpenAI e Anthropic
- montar um resumo em HTML
- enviar para um destinatario fixo todos os dias
- rodar em segundo plano com agendamento no Windows

### `Cofre de Senhas/`

Aplicacao local com interface web para armazenamento de credenciais com senha mestra e arquivo criptografado.

Arquivos principais:

- `app.py`
- `requirements.txt`
- `templates/index.html`

O projeto foi desenhado para:

- guardar senhas localmente com criptografia
- usar senha mestra para desbloqueio
- oferecer cadastro, consulta e exclusao de credenciais
- gerar senhas fortes automaticamente

## Tecnologias Utilizadas

- Python 3
- Selenium
- WebDriver Manager

## Como Executar

1. Instale as dependencias:

```bash
pip install selenium webdriver-manager
```

2. Execute o script:

```bash
python "Acesso Xeprium/Acesso_Xperium.py"
```

## Padrao Do Repositorio

Os scripts deste repositorio seguem uma linha simples:

- objetivo claro no cabecalho do arquivo
- comentarios diretos e uteis
- foco em automacao pratica
- organizacao por pastas conforme o projeto cresce
- versionamento para manter historico e confiabilidade

## O Que Nao Vai Para O Git

Arquivos locais, temporarios ou gerados automaticamente ficam fora do versionamento, como:

- `__pycache__/`
- arquivos `.pyc`
- arquivos de workspace do VS Code
- logs e historicos locais

## Proximos Passos

- adicionar novas automacoes por categoria
- criar um `requirements.txt` conforme o repositorio crescer
- incluir mais instrucoes de uso por subpasta
- padronizar estrutura e documentacao de cada script

## Sobre Este Repositorio

Este projeto funciona como laboratorio pratico, biblioteca pessoal de automacoes e vitrine tecnica em construcao.

Se a ideia for evoluir isso no GitHub, o caminho natural e separar os scripts por contexto, por exemplo:

- `automacao-web`
- `arquivos-e-planilhas`
- `utilitarios`
- `estudos`

---

Criado e mantido por **Saulo Prado**.
