# S.G.P.J. — Backend

API REST do **Sistema de Gestão da Prática Jurídica (S.G.P.J.)**, desenvolvido como projeto acadêmico para apoiar a organização e o acompanhamento das atividades da prática jurídica supervisionada da UNINASSAU — Centro Universitário Maurício de Nassau.

O backend concentra as regras de negócio, o controle de acesso dos usuários, a comunicação com o banco de dados e o gerenciamento das informações do sistema.

## 1. Tecnologias utilizadas

- **Python 3.12+** — linguagem de programação.
- **FastAPI** — desenvolvimento da API REST.
- **Uvicorn** — servidor ASGI.
- **SQLAlchemy 2** — ORM para comunicação com o banco de dados.
- **MySQL 8.0.16+** — sistema gerenciador de banco de dados.
- **Pydantic v2** — validação e estruturação de dados.
- **Pydantic Settings** — gerenciamento das configurações da aplicação.
- **Python-JOSE** — geração e validação de tokens JWT.
- **Pwdlib com Argon2** — gerenciamento seguro de senhas.
- **Python Multipart** — recebimento de arquivos enviados por formulários.

## 2. Funcionalidades implementadas

O backend disponibiliza os recursos necessários para o gerenciamento das atividades da prática jurídica.

### Autenticação e usuários
- Autenticação de usuários.
- Controle de acesso conforme o perfil.
- Gerenciamento de usuários e permissões.
- Proteção de rotas que exigem autenticação.

### Assistidos
- Cadastro e consulta de assistidos.
- Gerenciamento dos dados dos assistidos.

### Atendimentos
- Registro de atendimentos.
- Associação dos atendimentos aos assistidos e casos.
- Consulta dos atendimentos cadastrados.

### Casos jurídicos
- Cadastro e gerenciamento de casos.
- Associação de assistidos, alunos e professores.
- Validação de casos criados por alunos.
- Controle de situações dos casos.
- Encerramento e reabertura de casos.

### Alunos e professores
- Gerenciamento dos dados dos alunos.
- Gerenciamento dos dados dos professores.
- Associação dos responsáveis aos casos.

### Atividades e prazos
- Cadastro e gerenciamento de atividades.
- Atribuição de atividades ao aluno responsável pelo caso.
- Acompanhamento das situações das atividades.
- Registro de conclusão das atividades.
- Cadastro e validação de prazos.
- Identificação de prazos próximos e vencidos.

### Documentos
- Cadastro de documentos associados aos casos.
- Envio de arquivos PDF.
- Limite de tamanho de 20 MB por arquivo.
- Armazenamento privado dos arquivos.
- Download mediante autenticação e autorização de acesso.

### Histórico
- Registro de operações relevantes realizadas nos casos.
- Identificação do usuário responsável pelas alterações.
- Registro de datas e informações das operações.
- Consulta cronológica do histórico dos casos.

### Dashboard
- Indicadores gerais de acompanhamento.
- Quantidade de atendimentos e casos.
- Acompanhamento de atividades pendentes.
- Identificação de prazos próximos e vencidos.
- Listagem de itens que exigem atenção.

## 3. Organização do projeto

O backend utiliza uma organização em camadas, separando as responsabilidades da aplicação.

```text
Backend/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── routers/
│   │
│   ├── config/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
│
├── storage/
│   └── documentos/
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

### Responsabilidades das camadas

| Camada | Responsabilidade |
|---|---|
| `api` | Define as rotas e recebe as requisições HTTP. |
| `models` | Representa as entidades e tabelas do banco de dados. |
| `schemas` | Define estruturas de entrada e saída e valida os dados. |
| `repositories` | Responsável pelas operações de acesso ao banco de dados. |
| `services` | Concentra as regras de negócio da aplicação. |
| `config` | Gerencia as configurações do sistema. |
| `core` | Reúne componentes centrais, como autenticação e permissões. |
| `db` | Contém recursos relacionados à conexão e à sessão do banco de dados. |

A pasta `storage/documentos/` é utilizada para armazenar os arquivos PDF enviados ao sistema. Esses arquivos não são disponibilizados publicamente.

## 4. Pré-requisitos

Antes de executar o projeto, é necessário possuir:

- Python 3.12 ou superior.
- MySQL 8.0.16 ou superior.
- Git.
- Visual Studio Code ou outro editor de código.
- Um terminal para executar os comandos.

## 5. Configuração do ambiente

### 5.1. Acessar a pasta do backend

No terminal, entre na pasta `Backend` do projeto:

```bash
cd Backend
```

### 5.2. Criar o ambiente virtual

```bash
python -m venv .venv
```

### 5.3. Ativar o ambiente virtual

**Windows — PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows — Prompt de Comando:**

```cmd
.venv\Scripts\activate
```

**Linux ou macOS:**

```bash
source .venv/bin/activate
```

### 5.4. Instalar as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

## 6. Configuração do banco de dados

O sistema utiliza o MySQL para armazenar as informações.

Antes de iniciar a aplicação:

1. Certifique-se de que o MySQL esteja instalado e em execução.
2. Crie o banco de dados `sgpj`.
3. Execute o script SQL localizado em `Database/schema.sql`, na estrutura principal do projeto.
4. Configure os dados de conexão no arquivo `.env`.

As informações de conexão devem corresponder à instalação local do MySQL.

## 7. Variáveis de ambiente

O projeto utiliza variáveis de ambiente para configurar a aplicação e proteger informações sensíveis.

Crie uma cópia do arquivo `.env.example` com o nome `.env` e configure os valores necessários.

Principais variáveis:

| Variável | Descrição |
|---|---|
| `APP_NAME` | Nome da aplicação. |
| `APP_ENV` | Ambiente de execução. |
| `DEBUG` | Ativa ou desativa o modo de depuração. |
| `HOST` | Endereço de execução do servidor. |
| `PORT` | Porta utilizada pelo servidor. |
| `DB_HOST` | Endereço do servidor MySQL. |
| `DB_PORT` | Porta do MySQL. |
| `DB_USER` | Usuário do banco de dados. |
| `DB_PASSWORD` | Senha do banco de dados. |
| `DB_NAME` | Nome do banco de dados. |
| `SECRET_KEY` | Chave utilizada na autenticação e assinatura dos tokens. |
| `ALGORITHM` | Algoritmo utilizado na assinatura dos tokens. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo de validade do token de acesso. |
| `PRAZO_ALERTA_DIAS` | Quantidade de dias utilizada como referência para alertas de prazo. |
| `DOCUMENTOS_MAX_SIZE_MB` | Tamanho máximo permitido para arquivos enviados. |
| `DOCUMENTOS_EXTENSAO_PERMITIDA` | Extensão permitida para documentos. |
| `DOCUMENTOS_DIR` | Diretório de armazenamento dos documentos. |
| `CORS_ORIGINS` | Endereços autorizados a realizar requisições à API. |

A variável `SECRET_KEY` deve possuir um valor seguro e não pode ficar vazia.

Para gerar uma chave aleatória, pode ser utilizado:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Importante:** o arquivo `.env` contém configurações locais e informações sensíveis. Ele não deve ser compartilhado nem enviado ao repositório Git.

## 8. Executando a aplicação

Com o ambiente virtual ativado e as configurações realizadas, inicie o servidor com:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

A opção `--reload` permite que o servidor reinicie automaticamente durante o desenvolvimento quando alterações forem realizadas no código.

Após a inicialização, a API estará disponível em:

```text
http://127.0.0.1:8000
```

## 9. Documentação e verificação da API

O FastAPI disponibiliza documentação interativa para visualizar e testar os endpoints.

**Swagger UI:**

```text
http://127.0.0.1:8000/docs
```

**ReDoc:**

```text
http://127.0.0.1:8000/redoc
```

**Verificação de saúde da aplicação:**

```text
http://127.0.0.1:8000/api/v1/health
```

A rota de saúde permite verificar se a API está respondendo corretamente.

A documentação interativa apresenta as rotas disponíveis, os parâmetros necessários, os formatos de requisição e as respostas retornadas pela aplicação.

As rotas de documentação dependem da configuração do modo de depuração (`DEBUG`).

## 10. Segurança e controle de acesso

O sistema possui mecanismos de segurança para proteger as informações e restringir operações conforme o perfil do usuário.

Entre os mecanismos implementados estão:

- Autenticação por token JWT.
- Armazenamento de senhas com hash utilizando Argon2.
- Controle de permissões por perfil.
- Restrição de acesso aos registros conforme a responsabilidade do usuário.
- Validação das operações realizadas sobre casos, atividades e prazos.
- Registro de operações relevantes no histórico.
- Armazenamento privado de documentos.
- Verificação de autorização antes do download de arquivos.

Os arquivos PDF não são disponibilizados por uma pasta pública. O acesso ocorre por uma rota autenticada da API, que verifica as permissões do usuário.

## 11. Regras de negócio

O backend aplica regras para garantir a integridade das informações e o funcionamento adequado do fluxo da prática jurídica.

Entre elas:

- Alunos podem cadastrar casos para assistidos aos quais possuem acesso, mas o caso é criado inicialmente em situação de triagem.
- A validação de casos é realizada por Professor ou Gestão.
- Prazos cadastrados por alunos ficam pendentes de validação até a análise de Professor ou Gestão.
- Casos encerrados não permitem o cadastro de novas atividades.
- As atividades devem ser atribuídas ao aluno responsável pelo caso.
- As operações relevantes são registradas no histórico para permitir rastreabilidade.

## 12. Testes e validações

Durante o desenvolvimento, foram realizados testes das principais funcionalidades e regras de negócio, incluindo:

- Autenticação de alunos e professores.
- Controle de acesso aos registros.
- Cadastro e validação de casos.
- Cadastro e aprovação ou rejeição de prazos.
- Criação, atualização e conclusão de atividades.
- Encerramento e reabertura de casos.
- Registro e consulta do histórico.
- Funcionamento dos indicadores do dashboard.
- Envio e download de documentos PDF.
- Restrições de acesso aos documentos conforme o perfil do usuário.

Os testes foram realizados por meio da documentação interativa da API e de verificações das respostas HTTP.

## 13. Considerações finais

O backend do S.G.P.J concentra a estrutura de dados, as regras de negócio, a autenticação, as permissões e os serviços necessários para o gerenciamento da prática jurídica supervisionada.

Sua arquitetura foi organizada para permitir a integração com o frontend e facilitar a manutenção e a evolução do sistema.

A interface frontend será responsável por consumir os endpoints disponibilizados pela API, permitindo que os usuários interajam com as funcionalidades por meio de uma interface gráfica.