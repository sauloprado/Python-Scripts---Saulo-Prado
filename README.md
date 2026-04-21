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
