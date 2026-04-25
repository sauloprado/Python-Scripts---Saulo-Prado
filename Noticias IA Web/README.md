# Noticias IA Web

Aplicacao web local para buscar, salvar e ler noticias recentes sobre inteligencia artificial.

## Estrutura

- `backend/`: API Flask, login, SQLite e coleta RSS.
- `frontend/`: interface React com painel de leitura.
- `storage/leituras/`: arquivos TXT gerados.
- `storage/db/`: banco SQLite local.

## Login Inicial

Na primeira execucao, o backend cria um usuario local padrao:

- usuario: `saulo`
- senha: `trocar123`

Para mudar, crie `backend/.env` com base em `backend/.env.example` antes da primeira execucao.

## Backend

```bash
cd "Noticias IA Web/backend"
pip install -r requirements.txt
python app.py
```

API local:

```text
http://127.0.0.1:5051
```

## Frontend

```bash
cd "Noticias IA Web/frontend"
npm install
npm run dev
```

Site local:

```text
http://127.0.0.1:5174
```

## Como Funciona

1. Acesse o site e faca login.
2. Ajuste topicos, quantidade de noticias e periodo.
3. Clique em `Gerar noticias`.
4. O backend consulta os feeds RSS, salva no SQLite e gera um TXT.
5. O frontend mostra as noticias em cards e libera download do arquivo.

## Arquivos Locais

Estes itens ficam fora do Git:

- `frontend/node_modules/`
- `frontend/dist/`
- `backend/.env`
- `storage/leituras/*.txt`
- `storage/db/*.db`
