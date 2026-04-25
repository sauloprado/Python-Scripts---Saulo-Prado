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

### Noticias IA Web

Uma das automacoes mais interessantes deste repositorio e o projeto web local de noticias sobre inteligencia artificial.

Essa automacao foi criada para:

- buscar noticias recentes sobre ChatGPT, Claude, OpenAI, Anthropic e IA em geral
- permitir login local com usuario e senha
- mostrar as noticias em uma interface React moderna
- salvar os resultados em SQLite e em arquivos `.txt`
- funcionar como uma aplicacao com frontend e backend locais

Arquivos principais:

- `Noticias IA Web/backend/app.py`
- `Noticias IA Web/backend/news_service.py`
- `Noticias IA Web/frontend/src/App.jsx`
- `Noticias IA Web/README.md`

Esse projeto representa bem a proposta do repositorio: transformar uma necessidade real do dia a dia em uma automacao util, documentada e reutilizavel.

## Estrutura Atual

### `Acesso Xperium/`

Automacao de acesso a plataforma Xperium com Python e Selenium.

Arquivo principal:

- `Acesso_Xperium.py`

O script realiza:

- abertura automatica do navegador
- captura de credenciais via terminal
- preenchimento do formulario de login
- tentativa de clique e envio do acesso
- validacao basica do resultado
- registro local de acessos bem-sucedidos

### `Noticias IA Web/`

Aplicacao web local para buscar noticias recentes sobre inteligencia artificial, salvar historico no SQLite e gerar arquivos TXT para leitura.

Arquivos principais:

- `backend/app.py`
- `backend/db.py`
- `backend/news_service.py`
- `frontend/src/App.jsx`

O projeto ja nasce preparado para:

- consolidar noticias sobre ChatGPT, Claude, OpenAI e Anthropic
- autenticar o acesso com usuario e senha
- gerar novas buscas pelo navegador
- exibir cards de leitura com imagens quando disponiveis
- salvar as noticias em `storage/leituras/` e `storage/db/`

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
- Flask
- React
- SQLite
- RSS

## Como Executar

### Noticias IA Web

Backend:

```bash
cd "Noticias IA Web/backend"
python app.py
```

Frontend:

```bash
cd "Noticias IA Web/frontend"
npm install
npm run dev
```

### Acesso Xperium

Instale as dependencias:

```bash
pip install selenium webdriver-manager
```

Execute o script:

```bash
python "Acesso Xperium/Acesso_Xperium.py"
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
