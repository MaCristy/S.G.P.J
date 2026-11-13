---
name: mysql-database
description: >-
  Orientações e padrões para a modelagem relacional, scripts DDL, integridade referencial, indexação e consultas no MySQL para o Sistema de Gestão da Prática Jurídica (S.G.P.J.), atendendo às 10 entidades principais do projeto.
---

# Diretrizes de Banco de Dados Relacional (MySQL) - S.G.P.J.

Este guia orienta a modelagem relacional, integridade referencial, indexação e consultas no banco de dados **MySQL** do **S.G.P.J.**, fundamentado estritamente nas 10 entidades e relacionamentos descritos no documento de especificação (Seções 4.1 a 4.3).

---

## 1. Mapeamento Conceitual para o Modelo Relacional

O domínio do S.G.P.J. contempla 10 entidades principais. Abaixo, a correspondência entre a especificação e as tabelas do banco:

```text
                  +-------------------+
                  |     USUARIOS      |
                  +-------------------+
                     ^ 1           ^ 1
                     | 1           | 1
               +-----+-----+ +-----+-----+
               |   ALUNOS  | |PROFESSORES|
               +-----------+ +-----------+
                     ^             ^
                     |             | (responsáveis)
                     |             |
+--------------+ 1  N|          N  |
|  ASSISTIDOS  +-----+-------------+----+
+-------+------+     |                  |
        | 1          v N                |
        |      +--------------+         |
        +----->|CASOS_JURIDICOS|<-------+
        |      +-------+------+
        | 1            | 1
        |              +---------------+---------------+
        v N            | N             | N             | N
+--------------+ +-----+------+ +------+-----+ +---------------+
| ATENDIMENTOS | | ATIVIDADES | |   PRAZOS   | |HISTORICO_CASO |
+--------------+ +------------+ +------------+ | (Registro de  |
        |              |               |       |  Ocorrência)  |
        +--------------+---------------+       +---------------+
                       |
                       v N
                +--------------+
                |  DOCUMENTOS  |
                +--------------+
```

---

## 2. Estrutura das Tabelas: Requisitos Oficiais vs. Recomendações

Para total conformidade com a documentação do projeto, diferencia-se o que é **especificação formal** do que é **recomendação técnica de modelagem**:

### 2.1. Entidades de Usuários e Perfis (Doc. Seção 4.1 e 4.2)
1. **`usuarios`** (Conta de acesso, credenciais e perfil):
   * `id_usuario` INT AUTO_INCREMENT PRIMARY KEY
   * `nome` VARCHAR(150) NOT NULL
   * `email_institucional` VARCHAR(150) NOT NULL UNIQUE
   * `senha_armazenada` VARCHAR(255) NOT NULL *(Recomendação: hash criptográfico bcrypt)*
   * `perfil` VARCHAR(50) NOT NULL *(Recomendação de valores: 'ALUNO', 'PROFESSOR', 'GESTAO')*
   * `situacao_conta` VARCHAR(30) DEFAULT 'Ativo' *(Recomendação de valores: 'Ativo', 'Inativo')*
   * `data_criacao` DATETIME DEFAULT CURRENT_TIMESTAMP
   * `ultimo_acesso` DATETIME NULL
2. **`alunos`** (Dados específicos do estudante associado a uma conta de usuário):
   * `id_aluno` INT AUTO_INCREMENT PRIMARY KEY
   * `id_usuario` INT NOT NULL UNIQUE $\rightarrow$ FK para `usuarios(id_usuario)`
   * `matricula` VARCHAR(50) NOT NULL UNIQUE
   * `curso` VARCHAR(100) NOT NULL
   * `periodo` INT NOT NULL
   * `situacao_academica` VARCHAR(50) NOT NULL
   * `data_vinculo` DATE NOT NULL
3. **`professores`** (Dados específicos do orientador associado a uma conta de usuário):
   * `id_professor` INT AUTO_INCREMENT PRIMARY KEY
   * `id_usuario` INT NOT NULL UNIQUE $\rightarrow$ FK para `usuarios(id_usuario)`
   * `identificacao_funcional` VARCHAR(50) NOT NULL UNIQUE
   * `area_vinculo` VARCHAR(100) NULL *(Área ou vínculo, se pertinente)*
   * `situacao` VARCHAR(30) DEFAULT 'Ativo'

### 2.2. Entidades Centrais do Domínio Jurídico
4. **`assistidos`** (Identificação e contato da pessoa atendida):
   * `id_assistido` INT AUTO_INCREMENT PRIMARY KEY
   * `nome_completo` VARCHAR(200) NOT NULL
   * `identificador_cadastral` VARCHAR(50) NOT NULL UNIQUE
     > **Atenção:** Em conformidade estrita com o termo do documento (*"identificador cadastral necessário"*), este campo não deve ser restrito exclusivamente a formato de CPF sem aprovação prévia, aceitando outros identificadores se a coordenação aprovar.
   * `contato` VARCHAR(100) NOT NULL
   * `endereco` TEXT NULL *(Preenchido quando necessário)*
   * `observacoes_administrativas` TEXT NULL
   * `situacao` VARCHAR(30) DEFAULT 'Ativo'
   * `data_cadastro` DATETIME DEFAULT CURRENT_TIMESTAMP

5. **`casos_juridicos`** (Demanda acompanhada, estado, datas e responsáveis):
   * `id_caso` INT AUTO_INCREMENT PRIMARY KEY
   * `codigo_interno` VARCHAR(50) NOT NULL UNIQUE
   * `id_assistido` INT NOT NULL $\rightarrow$ FK para `assistidos(id_assistido)`
   * `titulo_assunto` VARCHAR(200) NOT NULL
   * `descricao` TEXT NOT NULL
   * `area_juridica` VARCHAR(100) NOT NULL
   * `situacao` ENUM('Em triagem', 'Aberto', 'Em Andamento', 'Suspenso', 'Encerrado') DEFAULT 'Em triagem'
     > **Estados Oficiais (Doc. Seção 5.1):** Os 5 estados do ENUM de casos são exatamente os definidos formalmente no documento.
   * `data_abertura` DATE NOT NULL
   * `data_encerramento` DATE NULL
   * `id_aluno_responsavel` INT NULL $\rightarrow$ FK para `alunos(id_aluno)`
   * `id_professor_orientador` INT NULL $\rightarrow$ FK para `professores(id_professor)`

6. **`atendimentos`** (Registro de atendimento e encaminhamentos):
   * `id_atendimento` INT AUTO_INCREMENT PRIMARY KEY
   * `id_assistido` INT NOT NULL $\rightarrow$ FK para `assistidos(id_assistido)`
   * `id_caso` INT NULL $\rightarrow$ FK para `casos_juridicos(id_caso)` *(Doc. Seção 4.3: associado quando aplicável)*
   * `id_usuario_registro` INT NOT NULL $\rightarrow$ FK para `usuarios(id_usuario)`
   * `data_hora` DATETIME NOT NULL
   * `tipo` VARCHAR(80) NOT NULL *(Recomendação de valores: 'Triagem Inicial', 'Retorno', 'Orientação')*
   * `descricao_objetiva` TEXT NOT NULL
   * `encaminhamento` TEXT NULL
   * `data_criacao` DATETIME DEFAULT CURRENT_TIMESTAMP

7. **`atividades`** (Ação prevista ou realizada dentro de um caso):
   * `id_atividade` INT AUTO_INCREMENT PRIMARY KEY
   * `id_caso` INT NOT NULL $\rightarrow$ FK para `casos_juridicos(id_caso)`
   * `id_responsavel` INT NOT NULL $\rightarrow$ FK para `usuarios(id_usuario)`
   * `titulo` VARCHAR(150) NOT NULL
   * `descricao` TEXT NOT NULL
   * `situacao` ENUM('Pendente', 'Em andamento', 'Concluída', 'Cancelada') DEFAULT 'Pendente'
     > **Estados Oficiais de Atividade (Doc. Seção 5.1):** São preservados estritamente os quatro estados sugeridos na Seção 5.1. A situação de supervisão "Devolvido para correção" não é incluída como alteração no modelo de dados neste momento, aguardando definição formal da equipe.
   * `prioridade` VARCHAR(30) DEFAULT 'Média' *(Recomendação: 'Baixa', 'Média', 'Alta')*
   * `data_criacao` DATETIME DEFAULT CURRENT_TIMESTAMP
   * `data_prevista` DATE NULL
   * `data_conclusao` DATETIME NULL

8. **`prazos`** (Data relevante associada a caso e opcionalmente a atividade):
   * `id_prazo` INT AUTO_INCREMENT PRIMARY KEY
   * `id_caso` INT NOT NULL $\rightarrow$ FK para `casos_juridicos(id_caso)`
   * `id_responsavel` INT NOT NULL $\rightarrow$ FK para `usuarios(id_usuario)`
   * `descricao` VARCHAR(255) NOT NULL
   * `data_limite` DATE NOT NULL
   * `situacao` ENUM('Pendente', 'Concluído', 'Vencido') DEFAULT 'Pendente'
     > **Estados Oficiais de Prazo (Doc. Seção 5.1):** Os três estados do ENUM correspondem aos estados oficiais da documentação. O status "Próximo do prazo" é tratado como cálculo/alerta dinâmico baseado em parâmetro configurável.
   * `observacoes` TEXT NULL
   * `data_conclusao` DATETIME NULL

9. **`documentos`** (Metadados e referência de arquivo associado a caso ou atendimento):
   * `id_documento` INT AUTO_INCREMENT PRIMARY KEY
   * `id_caso` INT NULL $\rightarrow$ FK para `casos_juridicos(id_caso)`
   * `id_atendimento` INT NULL $\rightarrow$ FK para `atendimentos(id_atendimento)`
   * `nome` VARCHAR(255) NOT NULL
   * `tipo` VARCHAR(80) NOT NULL
   * `caminho_armazenamento` VARCHAR(500) NOT NULL
   * `classificacao_acesso` VARCHAR(50) DEFAULT 'Restrito'
     > **Atenção:** Os valores sugeridos (`'Público Interno'`, `'Restrito'`, `'Segredo de Justiça'`) constituem **recomendações técnicas pendentes de aprovação formal**, mantendo-se o campo flexível para validação no backend.
   * `id_usuario_inclusao` INT NOT NULL $\rightarrow$ FK para `usuarios(id_usuario)`
   * `data_inclusao` DATETIME DEFAULT CURRENT_TIMESTAMP

10. **`historico_caso` (Representação da Entidade "Histórico / Registro de Ocorrência")**:
    * `id_historico` INT AUTO_INCREMENT PRIMARY KEY
    * `id_caso` INT NOT NULL $\rightarrow$ FK para `casos_juridicos(id_caso)`
    * `id_usuario_responsavel` INT NOT NULL $\rightarrow$ FK para `usuarios(id_usuario)`
    * `tipo_ocorrencia` VARCHAR(100) NOT NULL
    * `descricao` TEXT NOT NULL
    * `referencia_registro_afetado` VARCHAR(100) NULL
    * `data_hora` DATETIME DEFAULT CURRENT_TIMESTAMP
    > **Aplicação Mandatória da RN07:** Esta tabela materializa diretamente o requisito RN07 (*"Registros históricos não devem ser apagados silenciosamente; correções relevantes devem ser rastreáveis"*). Não deve permitir comandos `DELETE` ou `UPDATE` sob nenhuma circunstância.

---

## 3. Integridade Referencial e Restrições (RN06 e RN10)

* **Prevenção de Registros Órfãos (RN10):** Chaves estrangeiras com `ON DELETE RESTRICT` em `casos_juridicos`, `assistidos`, `documentos` e `historico_caso`.
* **Preservação de Dados de Encerramento (RN06):** Ao encerrar um caso, nenhum registro filho (atividades, documentos, prazos, histórico) deve ser excluído ou desvinculado.
* **Charset e Collation:** `utf8mb4` com `utf8mb4_unicode_ci` em todas as tabelas.

---

## 4. Índices para Otimização de Consultas e Indicadores (RF12 e Seção 9.1)

```sql
-- Otimização de busca por assistido (RF12)
CREATE INDEX idx_assistidos_busca ON assistidos(nome_completo, identificador_cadastral);

-- Otimização para os indicadores de casos e supervisão (Seção 9.1)
CREATE INDEX idx_casos_situacao ON casos_juridicos(situacao);
CREATE INDEX idx_casos_aluno ON casos_juridicos(id_aluno_responsavel);
CREATE INDEX idx_casos_professor ON casos_juridicos(id_professor_orientador);

-- Otimização para alerta preventivo de prazos (RF09)
CREATE INDEX idx_prazos_limite_status ON prazos(data_limite, situacao);
```
