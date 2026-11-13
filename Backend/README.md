# S.G.P.J. — Backend

API REST do **Sistema de Gestão da Prática Jurídica** — Projeto de Estágio Supervisionado, Ciência da Computação, UNINASSAU.

**Stack:** Python 3.12+ · FastAPI · SQLAlchemy 2 · MySQL 8.0.16+ · Pydantic v2

---

## Pré-requisitos

| Ferramenta | Versão Mínima |
|---|---|
| Python | 3.12 |
| MySQL Server | 8.0.16 |
| Banco de dados `sgpj` | Criado via `Database/schema.sql` |

---

## Configuração do Ambiente Local

### 1. Clone o repositório e acesse a pasta do Backend

```bash
cd sistema-gestão-pratica-juridica/Backend
```

### 2. Crie o ambiente virtual Python

```bash
python -m venv .venv
```

### 3. Ative o ambiente virtual

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Linux / macOS:**
```bash
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Configure as variáveis de ambiente

```bash
# Copie o arquivo de exemplo
copy .env.example .env     # Windows
cp .env.example .env       # Linux/macOS
```

Edite o `.env` e preencha:

```env
DB_PASSWORD=sua_senha_mysql_aqui
SECRET_KEY=gere_uma_chave_segura_aqui
```

> **Gerar uma SECRET_KEY segura:**
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

> ⚠️ **Nunca** commite o arquivo `.env` no repositório.

---

## Executando o Back-end

### Desenvolvimento (com hot-reload)

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Produção

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Verificação de Funcionamento

Após iniciar o servidor, acesse:

| URL | Descrição |
|---|---|
| `http://127.0.0.1:8000/api/v1/health` | Health check (API + banco) |
| `http://127.0.0.1:8000/docs` | Documentação Swagger UI (apenas em DEBUG=True) |
| `http://127.0.0.1:8000/redoc` | Documentação ReDoc (apenas em DEBUG=True) |
| `http://127.0.0.1:8000/` | Rota raiz com links |

**Resposta esperada de `/api/v1/health`:**

```json
{
  "status": "ok",
  "app": "Sistema de Gestão da Prática Jurídica (S.G.P.J.)",
  "environment": "development",
  "timestamp": "2026-11-12T17:59:00+00:00",
  "database": {
    "status": "ok",
    "message": "Conexão com o banco de dados estabelecida com sucesso."
  }
}
```

---

## Estrutura de Diretórios

```
Backend/
├── .env                        # Variáveis locais (NÃO comitar)
├── .env.example                # Modelo de variáveis (seguro para comitar)
├── .gitignore                  # Ignora .env, .venv, __pycache__
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
└── app/
    ├── __init__.py
    ├── main.py                 # Ponto de entrada FastAPI
    ├── api/
    │   ├── __init__.py
    │   ├── deps.py             # Injeção de dependências (get_db, auth futura)
    │   └── v1/
    │       ├── __init__.py     # api_router_v1 — agrega todos os routers
    │       └── routers/
    │           ├── __init__.py
    │           └── health.py   # GET /api/v1/health
    ├── config/
    │   ├── __init__.py
    │   └── settings.py         # Configurações via pydantic-settings + .env
    ├── db/
    │   ├── __init__.py
    │   ├── base.py             # Base declarativa SQLAlchemy
    │   └── session.py          # Engine, SessionLocal, get_db, check_db_connectivity
    ├── models/                 # Models ORM — a implementar por entidade
    │   └── __init__.py
    ├── repositories/           # Acesso ao banco (queries) — a implementar
    │   └── __init__.py
    ├── schemas/                # Schemas Pydantic v2 — a implementar
    │   └── __init__.py
    └── services/               # Lógica de negócio (RN01–RN10) — a implementar
        └── __init__.py
```

---

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_ENV` | `development` | Ambiente (`development` / `production`) |
| `DEBUG` | `True` | Ativa logs de SQL e docs Swagger/ReDoc |
| `HOST` | `127.0.0.1` | Host de escuta do servidor |
| `PORT` | `8000` | Porta de escuta |
| `DB_HOST` | `localhost` | Host do MySQL |
| `DB_PORT` | `3306` | Porta do MySQL |
| `DB_USER` | `root` | Usuário do MySQL |
| `DB_PASSWORD` | _(obrigatório)_ | Senha do MySQL |
| `DB_NAME` | `sgpj` | Nome do banco de dados |
| `SECRET_KEY` | _(obrigatório)_ | Chave secreta para JWT — sem fallback |
| `ALGORITHM` | `HS256` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Expiração do token (8h) |
| `PRAZO_ALERTA_DIAS` | `5` | Janela de alerta de prazos (RN05) |
| `CORS_ORIGINS` | `[...]` | Origens permitidas pelo CORS |

---

## Dependências Principais

```
fastapi>=0.115.0          — Framework web ASGI
uvicorn[standard]>=0.32.0 — Servidor ASGI
pydantic>=2.9.0           — Validação de schemas
pydantic-settings>=2.6.0  — Carregamento de .env
sqlalchemy>=2.0.36        — ORM e engine SQL
pymysql>=1.1.1            — Driver MySQL para Python
passlib[bcrypt]>=1.7.4    — Hashing de senhas (bcrypt)
python-jose[cryptography] — Geração e verificação de tokens JWT
python-multipart>=0.0.12  — Upload de arquivos (RF10)
```

