<p align="center">
<img src="assets/capa.png" alt="Python Scripts" width="100%">
</p>

<h1 align="center">Python Scripts</h1>
<p align="center"><i>Automações do dia a dia em Python: notícias de IA, cofre de senhas e acesso automatizado</i></p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white" alt="Flask">
<img src="https://img.shields.io/badge/React-20232A?style=flat-square&logo=react&logoColor=white" alt="React">
<img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
<img src="https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white" alt="Selenium">
<img src="https://img.shields.io/badge/status-em%20andamento-F59E0B?style=flat-square" alt="status: em andamento">
</p>

## Sumário

- [Sobre](#sobre)
- [Projetos](#projetos)
- [Como funciona](#como-funciona)
- [Tecnologias](#tecnologias)
- [Como executar](#como-executar)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Padrões do repositório](#padrões-do-repositório)
- [Autor](#autor)

## Sobre

Coleção de **automações reais do dia a dia**, construídas para resolver necessidades práticas e registrar a evolução técnica. Cada pasta é um projeto independente, documentado e pronto para rodar localmente.

## Projetos

| Projeto | O que faz | Stack |
| --- | --- | --- |
| [**Notícias IA Web**](Noticias%20IA%20Web/) | Busca notícias recentes sobre ChatGPT, Claude, OpenAI e Anthropic, com login local, interface React e histórico em SQLite e `.txt` | Flask · React · SQLite · RSS |
| [**Cofre de Senhas**](Cofre%20de%20Senhas/) | Cofre local com senha mestra, dados criptografados em disco e gerador de senhas fortes | Flask · cryptography |
| [**Acesso Xperium**](Acesso%20Xperium/) | Automatiza o login na plataforma Xperium: abre o navegador, preenche o formulário e registra os acessos | Selenium · WebDriver Manager |

## Como funciona

```mermaid
flowchart LR
    subgraph N[Notícias IA Web]
        N1[Fontes RSS] --> N2[news_service.py] --> N3[(SQLite)]
        N2 --> N4[storage/leituras/*.txt]
        N3 --> N5[Interface React]
    end
    subgraph C[Cofre de Senhas]
        C1[Senha mestra] --> C2[app.py] --> C3[(Arquivo criptografado)]
    end
```

## Tecnologias

| Tecnologia | Uso |
| --- | --- |
| Python 3 | Base de todas as automações |
| Flask | Backends locais (Notícias IA e Cofre) |
| React + Vite | Frontend do Notícias IA Web |
| SQLite | Histórico das notícias |
| cryptography | Criptografia do cofre |
| Selenium + WebDriver Manager | Automação de navegador |

## Como executar

**Notícias IA Web**

```bash
# backend
cd "Noticias IA Web/backend"
pip install -r requirements.txt
python app.py

# frontend (outro terminal)
cd "Noticias IA Web/frontend"
npm install
npm run dev
```

**Cofre de Senhas** — o launcher instala as dependências, sobe o servidor e abre o navegador:

```bash
python subir_cofre.py
```

**Acesso Xperium**

```bash
pip install selenium webdriver-manager
python "Acesso Xperium/Acesso_Xperium.py"
```

## Estrutura do repositório

```text
Python-Scripts---Saulo-Prado/
├── Acesso Xperium/
│   └── Acesso_Xperium.py
├── Cofre de Senhas/
│   ├── app.py
│   ├── icon_bank.py
│   ├── requirements.txt
│   ├── static/  (app.js, styles.css)
│   └── templates/index.html
├── Noticias IA Web/
│   ├── backend/  (app.py, db.py, news_service.py, requirements.txt)
│   ├── frontend/ (React + Vite)
│   └── storage/  (db/, leituras/)
├── assets/capa.png
└── subir_cofre.py
```

## Padrões do repositório

- Objetivo claro no cabeçalho de cada script
- Uma pasta por projeto, com README próprio quando necessário
- Arquivos locais e gerados (`__pycache__/`, logs, bancos e workspaces) ficam fora do Git
- Credenciais nunca são versionadas: use `.env` a partir do `.env.example`

## Autor

**Saulo Prado** · Analista de Sistemas · Gestão de Ativos de TI, orçamento, automação e dashboards

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Saulo%20Prado-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/saulo-prado-ab4a0b96/)
[![GitHub](https://img.shields.io/badge/GitHub-sauloprado-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/sauloprado)
