---
name: security-best-practices
description: >-
  Diretrizes de segurança da informação, autenticação JWT, controle de acesso baseado em papéis (RBAC), proteção a dados sensíveis de prática jurídica (LGPD), validação de entradas e prevenção contra vulnerabilidades para o S.G.P.J.
---

# Diretrizes de Segurança, Privacidade e Integridade - S.G.P.J.

Este guia estabelece as diretrizes de segurança da informação para o **Sistema de Gestão da Prática Jurídica (S.G.P.J.)**, relacionando diretamente as recomendações técnicas aos **Requisitos Não-Funcionais (Seção 7)** e às **Regras de Negócio de Proteção de Dados (RN01, RN07, RN08, RN09 e RN10)** do projeto oficial.

---

## 1. Mapeamento Direto com os Requisitos Não-Funcionais (Doc. Seção 7)

As práticas de segurança implementadas devem atender às seguintes exigências formais:

```text
+---------------------------------------------------------------------------------------------------+
| RNF do Documento (Seção 7)    | Recomendações Técnicas Implementadas                              |
+---------------------------------------------------------------------------------------------------+
| Segurança                     | - Autenticação com OAuth2 Password Bearer e tokens JWT.           |
|                               | - Armazenamento seguro de senhas com hashing bcrypt (custo >= 12).|
|                               | - Autorização validada no servidor (guards por perfil).           |
|                               | - Proteção e download autenticado de arquivos anexados.          |
+---------------------------------------------------------------------------------------------------+
| Privacidade (LGPD)            | - Princípio do menor privilégio no acesso aos autos e casos.      |
|                               | - Minimização de dados pessoais em listagens gerais.             |
|                               | - Resguardo a demandas com segredo de justiça ou menores.         |
+---------------------------------------------------------------------------------------------------+
| Rastreabilidade               | - Registro obrigatório de autor e data/hora (RN07 e RF11).        |
|                               | - Imutabilidade da tabela `historico_caso`.                       |
+---------------------------------------------------------------------------------------------------+
| Integridade                   | - Validação rigorosa de esquemas de entrada (Pydantic).           |
|                               | - Prevenção contra SQL Injection via consultas parametrizadas.    |
|                               | - Bloqueio de registros órfãos e transições inválidas (RN10).     |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Autenticação e Gestão de Sessão (RNF Segurança, RF01 e RN01)

1. **Armazenamento Seguro de Credenciais:**
   * É vedado armazenar senhas em texto puro.
   * Recomendação técnica: Utilização de **bcrypt** com geração automática de salt, atendendo ao requisito de armazenamento seguro.
2. **Tokens de Acesso JWT (JSON Web Tokens):**
   * Recomendação de arquitetura stateless para a API REST com FastAPI.
   * O payload deve conter identificadores seguros (`sub` com id do usuário, e-mail institucional e perfil de acesso), além de tempo de expiração (`exp`).
   * A chave secreta (`SECRET_KEY`) deve residir exclusivamente em variáveis de ambiente (`.env`), nunca sendo exposta em repositórios.
3. **Encerramento de Sessão:**
   * Garantir que o encerramento da sessão no frontend invalide o token local e interrompa o acesso às rotas protegidas.

---

## 3. Controle de Acesso Baseado em Perfis (RBAC - RNF Segurança e RN08)

O sistema opera com 3 papéis com responsabilidades estritamente delimitadas (Doc. Seção 3):

* **Aluno / Estagiário:**
  * Consulta apenas os casos sob sua responsabilidade atribuída.
  * Registra atendimentos, atividades e prazos de seus casos.
  * Não possui permissão para aprovar peças ou acessar demandas de colegas sem autorização.
* **Professor / Orientador:**
  * Supervisiona e consulta casos e atividades vinculados à sua orientação.
  * Acompanha o progresso, valida ações e emite orientações de estágio.
* **Gestão / Coordenação:**
  * Acompanha a operação por meio de consultas consolidadas e indicadores gerenciais do dashboard.
  * Gerencia usuários e permissões do sistema.

### Verificação de Titularidade (Ownership Check):
Além de verificar o perfil, o backend deve assegurar que o usuário só visualize/altere casos sob sua responsabilidade (ex.: aluno só acessa caso onde `id_aluno_responsavel = id_aluno_logado`).

---

## 4. Privacidade e Proteção de Dados Pessoais (RNF Privacidade e RN09)

1. **Minimização de Dados (LGPD):**
   * Apenas dados indispensáveis à prática jurídica devem ser coletados e exibidos.
   * No cadastro de assistidos, coletar o `"identificador cadastral necessário"` e dados de contato. Dados detalhados de hipossuficiência socioeconômica só devem ser visíveis aos responsáveis diretos pelo caso.
2. **Segredo de Justiça e Casos Sensíveis:**
   * Demandas que tramitam em segredo de justiça (ex.: direito de família, alimentos, interesse de incapazes) devem ter visualização restrita exclusivamente ao estudante e orientador atribuídos, bloqueando visibilidade a outros usuários não gestores.
3. **Proteção na Exclusão (RN06 e RN07):**
   * Casos encerrados nunca são destruídos; seu acervo de atendimentos, documentos, atividades e histórico permanece arquivado e preservado para fins de comprovação acadêmica e jurídica.

---

## 5. Rastreabilidade e Auditoria (RNF Rastreabilidade e RN07)

* Toda operação relevante (abertura de caso, mudança de situação, atribuição de responsável, emissão de despacho e encerramento) deve gravar um registro na entidade **Histórico / Registro de Ocorrência** (`historico_caso`).
* Cada registro de histórico deve conter:
  * Identificador do caso (`id_caso`).
  * Usuário responsável pela ação (`id_usuario_responsavel`).
  * Tipo de ocorrência e descrição clara do evento.
  * Timestamp preciso da ação (`data_hora`).
* **Regra de Imutabilidade:** Registros de histórico não devem ser alterados ou apagados (`DELETE` e `UPDATE` desabilitados na tabela).

---

## 6. Validação de Entradas e Proteção de Arquivos (RNF Segurança e Integridade)

1. **Prevenção contra Injeção de SQL:**
   * Utilizar exclusivamente consultas parametrizadas via ORM (SQLAlchemy 2.0). Jamais interpolar strings para montar consultas dinâmicas.
2. **Prevenção contra XSS e Injeções de Código:**
   * Sanitizar entradas de texto livre no backend (Pydantic) e manter a renderização segura e tipada no frontend em React.
3. **Proteção no Armazenamento de Documentos (RF10):**
   * Validar tipos MIME permitidos (ex.: PDF, imagens de comprovantes) e limite de tamanho.
   * Armazenar os arquivos físicos fora do diretório público do servidor web com nomes aleatórios (UUID), preservando o nome original apenas no banco de dados.
   * O acesso/download do documento deve exigir token autenticado e validação de permissão sobre o caso ao qual está vinculado.
