---
name: fastapi-backend
description: >-
  Orientações e padrões para o desenvolvimento do Backend em Python com FastAPI para o Sistema de Gestão da Prática Jurídica (S.G.P.J.), incluindo arquitetura em camadas, endpoints REST, validações com Pydantic, aplicação das regras de negócio (RN01 a RN10) e persistência com SQLAlchemy e MySQL.
---

# Diretrizes de Desenvolvimento Backend (FastAPI) - S.G.P.J.

Este guia estabelece os padrões arquiteturais, regras de validação e implementação de serviços da API REST do **Sistema de Gestão da Prática Jurídica (S.G.P.J.)**, desenvolvido com **Python + FastAPI** e conectado ao banco **MySQL**, atendendo rigorosamente aos requisitos funcionais (RF01 a RF14) e às regras de negócio (RN01 a RN10).

---

## 1. Arquitetura em Camadas (Proposta Técnica de Implementação)

Para garantir o requisito não-funcional de **Manutenibilidade** (Seção 7), propõe-se a seguinte estrutura modular:

```text
backend/
├── app/
│   ├── api/
│   │   ├── deps.py               # Injeção de dependências (get_db, get_current_user, check_role)
│   │   └── v1/
│   │       └── routers/          # Endpoints REST (proposta técnica de rotas)
│   ├── core/
│   │   ├── config.py             # Configurações dinâmicas da aplicação (.env)
│   │   └── security.py           # Funções de hashing e tokens
│   ├── db/
│   │   ├── base.py               # Metadados e modelos ORM
│   │   └── session.py            # Sessão de banco de dados
│   ├── models/                   # Modelos ORM (SQLAlchemy)
│   ├── schemas/                  # Schemas de validação e transferência (Pydantic v2)
│   ├── services/                 # Lógica de negócio e orquestração de transações
│   └── main.py                   # Ponto de entrada FastAPI
```

---

## 2. Implementação das Regras de Negócio Oficiais (RN01 a RN10)

O backend é a camada responsável por aplicar as regras de negócio descritas na Seção 4.4 do documento:

* **RN01 (Autenticação e Autorização):** Somente usuários autenticados e autorizados podem acessar funcionalidades internas. Rotas protegidas via dependência de autenticação e validação de sessão ativa.
* **RN02 (Vínculo de Caso a Assistido):** Um caso deve estar obrigatoriamente vinculado a um assistido previamente cadastrado e ativo.
* **RN03 (Situação e Responsáveis do Caso):** Um caso aberto deve ter situação identificável e, preferencialmente, responsáveis definidos conforme a regra aprovada (aluno responsável e professor orientador). Estados oficiais do caso: `Em triagem`, `Aberto`, `Em Andamento`, `Suspenso` e `Encerrado`.
* **RN04 (Atividades vinculadas a Caso):** Atividades devem estar vinculadas a um caso e possuir situação atual. Os estados oficiais sugeridos para atividade são: `Pendente`, `Em andamento`, `Concluída` e `Cancelada`.
  > *Nota sobre Supervisão:* O tratamento visual "Devolvido para correção" (Seção 11.6) representa uma situação de revisão/supervisão pendente de definição formal pela coordenação sobre sua modelagem de dados definitiva.
* **RN05 (Gestão e Cálculo de Prazos):** Um prazo deve possuir descrição e data limite; sua situação deve permitir distinguir `Pendente`, `Concluído` e `Vencido`, conforme as regras de cálculo aprovadas.
  * **Configurabilidade de Prazos Próximos:** A identificação de prazos próximos (alerta de risco) **não deve ter um número fixo de dias hardcoded no código**. O sistema deve adotar um parâmetro de configuração flexível (ex.: `PRAZO_ALERTA_DIAS` definido via configuração/ambiente), permitindo que a coordenação ajuste a janela de alerta conforme as regras aprovadas pelo NPJ.
* **RN06 (Encerramento de Caso):** O encerramento de um caso deve registrar a data e preservar integralmente seus atendimentos, documentos, atividades e histórico.
* **RN07 (Rastreabilidade e Imutabilidade do Histórico):** Registros históricos não devem ser apagados silenciosamente; correções relevantes devem ser rastreáveis. Operações críticas geram evento na entidade `historico_caso`. É vedada a exclusão física (`DELETE`) de registros históricos.
* **RN08 (Isolamento por Perfil):** Usuários só podem visualizar ou alterar informações compatíveis com seu perfil e com os casos sob sua responsabilidade (Aluno consulta seus casos; Professor supervisiona sua equipe; Gestão visualiza o panorama global).
* **RN09 (Minimização de Dados Pessoais - LGPD):** Os dados pessoais devem ser limitados ao necessário para a finalidade da prática jurídica e acessíveis apenas a pessoas autorizadas.
* **RN10 (Integridade Essencial):** Não deve ser permitido concluir uma operação quando ela produzir referências inválidas ou inconsistências essenciais (exclusão de registros com vínculos ou transições de estado ilegais).

---

## 3. Endpoints REST (Especificação Recomendada para Atender aos RFs)

As rotas abaixo são uma **recomendação técnica padronizada** para materializar os Requisitos Funcionais descritos no documento:

| Módulo / Domínio | Rota Sugerida | Método | Requisito Funcional Atendido |
| :--- | :--- | :---: | :--- |
| **Autenticação** | `/api/v1/auth/login` | `POST` | **RF01** – Autenticação com encerramento de sessão seguro. |
| | `/api/v1/auth/me` | `GET` | **RF02** – Identificação e perfis de acesso. |
| **Assistidos** | `/api/v1/assistidos` | `GET` / `POST` | **RF03, RF12** – Cadastro, consulta e validação do assistido (identificador cadastral necessário). |
| | `/api/v1/assistidos/{id}` | `GET` / `PUT` | **RF03** – Detalhes e atualização cadastral. |
| **Atendimentos** | `/api/v1/atendimentos` | `POST` / `GET` | **RF04, RF12** – Registro de atendimentos e consultas por período. |
| **Casos Jurídicos** | `/api/v1/casos` | `GET` / `POST` | **RF05, RF06** – Abertura e atribuição de responsáveis (aluno e professor). |
| | `/api/v1/casos/{id}` | `GET` | **RF05** – Consulta completa de autos e abas do caso. |
| | `/api/v1/casos/{id}/status` | `PATCH` | **RF08, RN07** – Controle de situação com registro no histórico. |
| | `/api/v1/casos/{id}/encerrar` | `POST` | **RN06** – Encerramento preservando acervo e datas. |
| **Atividades** | `/api/v1/casos/{id}/atividades` | `POST` / `GET` | **RF07, RN04** – Atividades vinculadas aos casos. |
| | `/api/v1/atividades/{id}` | `PATCH` | **RF08** – Transição de situação de atividades. |
| **Prazos** | `/api/v1/casos/{id}/prazos` | `POST` / `GET` | **RF09, RN05** – Prazos com cálculo de vencimento. |
| | `/api/v1/prazos/alertas` | `GET` | **RF09** – Alerta de prazos próximos (janela parametrizável). |
| **Documentos** | `/api/v1/casos/{id}/documentos` | `POST` / `GET` | **RF10** – Associação de arquivos ou referências documentais. |
| | `/api/v1/documentos/{id}/download` | `GET` | **RF10, RN08** – Acesso controlado aos documentos. |
| **Histórico** | `/api/v1/casos/{id}/historico` | `GET` | **RF11, RN07** – Registro cronológico de ocorrências. |
| **Supervisão** | `/api/v1/supervisao/orientandos` | `GET` | **RF13** – Visão do orientador sobre estudantes e casos supervisionados. |
| **Dashboard** | `/api/v1/dashboard/indicadores` | `GET` | **RF14, Seção 9.1** – Resumo da operação com os 10 indicadores gerenciais. |

---

## 4. Agregação dos 10 Indicadores Gerenciais (Doc. Seção 9.1)

O endpoint de dashboard deve fornecer os dados consolidados definidos pela coordenação:
1. **Atendimentos Realizados:** Volume total de triagens e atendimentos no período.
2. **Novos Casos:** Quantidade de novos casos abertos no período.
3. **Casos Ativos:** Casos em andamento e sob acompanhamento em tempo real.
4. **Casos Encerrados:** Demandas concluídas ou resolvidas no período.
5. **Distribuição por Situação:** Agrupamento por estados (`Em triagem`, `Aberto`, `Em Andamento`, `Suspenso`, `Encerrado`).
6. **Atividades Pendentes:** Tarefas que aguardam execução pelos estudantes.
7. **Prazos Próximos (Alerta de Risco):** Compromissos que vencerão no intervalo configurado.
8. **Atendimentos por Estudante:** Produtividade e assiduidade individual dos estagiários.
9. **Casos por Estudante:** Distribuição de casos ativos para equidade pedagógica.
10. **Casos por Professor/Orientador:** Equilíbrio da carga horária de orientação docente.
