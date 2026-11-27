# ⚖️ Sistema de Gestão da Prática Jurídica (S.G.P.J.)

Sistema web desenvolvido para auxiliar na organização, no gerenciamento e no acompanhamento das atividades do Núcleo de Prática Jurídica (NPJ), permitindo centralizar informações sobre assistidos, casos jurídicos, atividades, prazos e documentos.

O projeto está sendo desenvolvido como parte do **Estágio Supervisionado do curso de Ciência da Computação da UNINASSAU – João Pessoa**, com a proposta de construir um MVP (Produto Mínimo Viável) funcional.

---

## 📌 Sobre o projeto

O S.G.P.J. tem como objetivo facilitar o gerenciamento das atividades desenvolvidas no Núcleo de Prática Jurídica, proporcionando maior organização dos registros, acompanhamento das demandas e controle das responsabilidades dos envolvidos.

A aplicação possui três perfis principais de acesso:

- **Aluno/Estagiário:** responsável pelo registro e acompanhamento das atividades práticas e dos casos jurídicos.
- **Professor/Orientador:** responsável pela supervisão dos alunos, acompanhamento dos casos e validações pertinentes.
- **Gestão/Coordenação:** responsável pelo gerenciamento administrativo, controle dos registros e acompanhamento geral do sistema.

Cada perfil possui permissões específicas, respeitando suas responsabilidades dentro do fluxo de trabalho.

## 🎯 Objetivos

- Centralizar as informações dos assistidos e dos casos jurídicos.
- Organizar o acompanhamento das atividades desenvolvidas pelos alunos.
- Facilitar a supervisão realizada pelos professores orientadores.
- Controlar prazos e documentos relacionados aos casos.
- Manter o histórico das ocorrências importantes.
- Disponibilizar indicadores para acompanhamento administrativo.
- Garantir controle de acesso conforme os perfis dos usuários.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| React | Desenvolvimento da interface frontend |
| JavaScript | Lógica e interatividade da aplicação |
| Python | Desenvolvimento do backend |
| FastAPI | Construção da API REST |
| MySQL | Gerenciamento e armazenamento dos dados |
| HTML5 | Estruturação das interfaces |
| CSS3 | Estilização e responsividade |
| Git e GitHub | Versionamento e gerenciamento do código |

### Arquitetura

O sistema utiliza uma arquitetura organizada em três camadas:

1. **Camada de apresentação (Frontend):** responsável pela interface gráfica e pela interação com os usuários.
2. **Camada de aplicação e negócio (Backend):** responsável pelo processamento das requisições, validações, autenticação, permissões e regras de negócio.
3. **Camada de dados (Banco de dados):** responsável pelo armazenamento, consulta e integridade das informações.

A comunicação entre frontend e backend ocorre por meio de uma API REST, utilizando requisições HTTP e dados no formato JSON.

---

## ⚙️ Funcionalidades implementadas

### 1. Autenticação e gerenciamento de usuários
- Autenticação de usuários.
- Controle de acesso por perfil.
- Solicitação de cadastro para alunos e professores.
- Aprovação e rejeição de solicitações pela Gestão.
- Ativação de contas após aprovação.
- Controle de acesso de contas pendentes.

### 2. Gerenciamento de assistidos
- Cadastro de assistidos.
- Consulta e edição conforme as permissões.
- Associação dos registros aos usuários e casos correspondentes.
- Controle de acesso de acordo com o perfil.

### 3. Gerenciamento de casos jurídicos
- Abertura de casos pelo aluno.
- Associação de assistidos.
- Seleção de professor orientador.
- Validação de casos pelo professor.
- Controle de situação dos casos.
- Registro de encerramento e respectiva data.
- Histórico das alterações relevantes.

### 4. Gerenciamento de atividades
- Cadastro de atividades vinculadas aos casos.
- Organização por prioridade e situação.
- Acompanhamento das atividades pelos professores.
- Edição de prioridade conforme as permissões.
- Registro de ocorrências no histórico.

### 5. Controle de prazos
- Cadastro de prazos vinculados aos casos.
- Situação inicial pendente de validação.
- Aprovação ou rejeição pelo professor.
- Atualização e conclusão dos prazos.
- Controle conforme as permissões dos perfis.

### 6. Gerenciamento de documentos
- Envio de documentos em formato PDF.
- Armazenamento privado dos arquivos.
- Associação dos documentos aos registros permitidos.
- Consulta e download conforme as permissões.
- Controle de acesso por perfil.

### 7. Histórico de ocorrências
- Registro de acontecimentos relevantes.
- Consulta do histórico por caso.
- Identificação do usuário responsável pelo registro.
- Registro de alterações e eventos importantes.
- Controle de acesso conforme o perfil.

### 8. Dashboards
- Dashboard específico para Aluno.
- Dashboard específico para Professor.
- Dashboard administrativo para Gestão.
- Indicadores de casos e atividades.
- Acompanhamento de prazos.
- Visualização de informações conforme as responsabilidades de cada perfil.

### 9. Notificações
- Painel de notificações.
- Consulta das notificações recebidas.
- Contagem de notificações não lidas.
- Marcação de notificações como lidas.

**Observação:** a estrutura de consulta e leitura das notificações está implementada. A geração automática de notificações a partir dos eventos do sistema ainda está prevista como evolução.

---

## 👥 Perfis e permissões

| Funcionalidade | Aluno | Professor | Gestão |
|---|:---:|:---:|:---:|
| Cadastro de assistidos | ✓ | — | ✓ |
| Consulta de assistidos | ✓ | ✓* | ✓ |
| Edição de assistidos | ✓* | — | ✓ |
| Abertura de casos | ✓ | — | ✓* |
| Validação de casos | — | ✓ | ✓* |
| Consulta de casos | ✓* | ✓* | ✓ |
| Cadastro de atividades | ✓ | — | — |
| Consulta de atividades | ✓* | ✓* | ✓ |
| Edição de prioridade | — | ✓* | ✓ |
| Cadastro de prazos | ✓ | — | ✓* |
| Validação de prazos | — | ✓ | ✓* |
| Envio de documentos | ✓* | — | ✓ |
| Consulta de documentos | ✓* | ✓* | ✓ |
| Consulta do histórico | ✓* | ✓* | ✓ |
| Gerenciamento de usuários | — | — | ✓ |
| Administração geral | — | — | ✓ |

\* Conforme os vínculos e as regras de permissão estabelecidos pelo sistema.

---

## 🗂️ Organização do projeto

O projeto está dividido em duas aplicações principais:

```text
S.G.P.J/
│
├── Backend/
│   └── app/
│       ├── api/
│       │   └── v1/
│       │       └── routers/
│       ├── models/
│       ├── schemas/
│       ├── repositories/
│       ├── services/
│       └── main.py
│
├── Frontend/
│   └── src/
│       ├── layouts/
│       ├── pages/
│       ├── services/
│       └── styles/
│
├── Database/
│   └── Scripts e migrações SQL
│
└── README.md
```

### Responsabilidades das principais pastas

**Backend**
- `api/`: organização das rotas e endpoints da API.
- `models/`: representação das entidades do banco de dados.
- `schemas/`: estruturas de dados e validações.
- `repositories/`: operações de acesso e persistência dos dados.
- `services/`: regras de negócio e processamento das funcionalidades.
- `main.py`: inicialização e configuração principal da aplicação.

**Frontend**
- `layouts/`: estruturas compartilhadas das páginas.
- `pages/`: telas e páginas da aplicação.
- `services/`: comunicação com a API e serviços específicos.
- `styles/`: estilos e padronização visual.

**Database**
- Scripts SQL e migrações utilizados na estruturação e evolução do banco de dados.

---

## 🔄 Fluxo principal do sistema

O fluxo operacional proposto para o S.G.P.J. é:

```text
Cadastro do assistido
        ↓
Registro do atendimento
        ↓
Abertura do caso jurídico
        ↓
Associação do aluno e professor orientador
        ↓
Validação do caso
        ↓
Registro de atividades e prazos
        ↓
Acompanhamento e supervisão
        ↓
Documentos e histórico
        ↓
Encerramento do caso
```

O fluxo integra os três perfis: o aluno executa e registra as atividades, o professor supervisiona e valida as etapas pertinentes, e a Gestão administra e acompanha o funcionamento geral.

---

## 🔐 Segurança e controle de acesso

O sistema possui mecanismos de controle voltados à proteção e à organização das informações:

- Autenticação de usuários.
- Controle de permissões no backend.
- Restrições de acesso conforme o perfil.
- Validação das operações realizadas.
- Armazenamento privado dos documentos.
- Controle de acesso aos registros vinculados aos casos.
- Histórico de ocorrências relevantes.

As verificações de permissão são realizadas no backend, não dependendo apenas da apresentação ou ocultação de elementos na interface.

---

## 🚧 Estado atual do desenvolvimento

O S.G.P.J. encontra-se em fase de desenvolvimento e validação do MVP.

| Módulo | Situação |
|---|---|
| Autenticação e usuários | Implementado |
| Solicitações de cadastro | Implementado |
| Assistidos | Implementado |
| Casos jurídicos | Implementado |
| Atividades | Implementado |
| Prazos | Implementado |
| Documentos | Implementado |
| Histórico | Implementado |
| Dashboards | Implementado |
| Painel de notificações | Implementado parcialmente |

### Melhorias e evoluções previstas

- Automatização da geração de notificações.
- Ampliação dos eventos registrados no histórico.
- Validação e consolidação do fluxo completo de atendimentos.
- Ampliação dos cenários de testes e validação.
- Evolução das funcionalidades conforme as necessidades identificadas.

---

## ▶️ Execução do projeto

O projeto utiliza duas aplicações independentes: frontend e backend, além de um banco de dados MySQL.

Para executar o sistema, é necessário:

- Ter Python instalado.
- Ter Node.js e npm instalados.
- Ter MySQL instalado e configurado.
- Configurar as variáveis de ambiente e as credenciais de conexão.
- Executar as migrações e scripts necessários para estruturar o banco de dados.
- Instalar as dependências do frontend e do backend.

As instruções específicas de instalação e inicialização devem acompanhar os arquivos de configuração e dependências presentes no repositório.

---

## 🎨 Identidade visual

A interface segue uma proposta visual inspirada na identidade institucional da UNINASSAU, utilizando uma paleta baseada em:

- Azul institucional: `#003874`
- Amarelo: `#E3B103`
- Branco: `#FFFFFF`
- Fundo claro: `#F4F5FA`
- Texto principal: `#202938`

O objetivo é proporcionar uma interface organizada, consistente e adequada ao ambiente acadêmico e administrativo.

---

## 📚 Contexto acadêmico

**Projeto:** Sistema de Gestão da Prática Jurídica (S.G.P.J.)  
**Instituição:** UNINASSAU – Centro Universitário Maurício de Nassau  
**Campus:** João Pessoa – PB  
**Curso:** Ciência da Computação  
**Disciplina:** Estágio Supervisionado  
**Ano:** 2026

---

## 👩‍💻 Desenvolvimento

Projeto acadêmico desenvolvido como proposta de solução tecnológica para apoiar a gestão das atividades do Núcleo de Prática Jurídica.

---

**S.G.P.J. — Organização, acompanhamento e gestão da prática jurídica.**
