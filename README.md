# Scripts Python

Repositório pessoal de scripts Python criados para automatizar tarefas do dia a dia, testar ideias rapidamente e consolidar estudos com projetos práticos.

Aqui a proposta é simples: manter soluções úteis, reaproveitáveis e bem documentadas, em vez de deixar cada script perdido em pastas locais.

## Objetivo

Este repositório serve para:

- centralizar automações em Python
- organizar estudos aplicados em projetos reais
- versionar melhorias com segurança
- facilitar manutenção e reaproveitamento de código
- construir um portfólio técnico simples e honesto

## Estrutura Atual

No momento, o projeto contém:

- `Acesso Xeprium/`
  Script de automação de login na plataforma Xperiun usando Selenium.

## Script Em Destaque

### `Acesso_Xperium.py`

Automatiza o processo de acesso à plataforma Xperiun com abertura do navegador, preenchimento de credenciais e tentativa de validação do login.

**Principais pontos:**

- solicita e-mail e senha no terminal
- usa `Selenium` para interagir com a página
- tenta localizar e acionar o botão de login de forma flexível
- verifica indícios de sucesso após a autenticação
- registra acessos bem-sucedidos em arquivo local

## Como Executar

1. Tenha o Python 3 instalado.
2. Instale as dependências necessárias.
3. Execute o script pelo terminal.

```bash
pip install selenium webdriver-manager
python "Acesso Xeprium/Acesso_Xperium.py"
```

## Boas Práticas Deste Repositório

- scripts com cabeçalho descritivo
- comentários objetivos para facilitar manutenção
- foco em automações úteis e diretas
- separação entre código, arquivos gerados e configurações locais

## Arquivos Que Não Devem Ir Para O Git

Alguns arquivos são locais ou gerados automaticamente e não fazem sentido no versionamento:

- `__pycache__/`
- arquivos `.pyc`
- arquivos de workspace do VS Code
- históricos locais como `historico_acessos_xperium.txt`

## Próximos Passos Sugeridos

- adicionar novos scripts por tema ou sistema
- criar um `requirements.txt` por projeto ou um geral para a pasta
- incluir exemplos de uso em cada subpasta
- padronizar nomes, versões e objetivos nos cabeçalhos

## Sobre O Versionamento

Subir esta pasta para o Git vale muito a pena, principalmente porque:

- protege seu progresso
- facilita voltar versões antigas
- deixa sua evolução visível
- transforma scripts soltos em um acervo técnico organizado

O principal cuidado é não versionar dados sensíveis, históricos locais, credenciais, arquivos temporários ou configurações muito pessoais do editor.

---

Criado e mantido por **Saulo Prado**.
